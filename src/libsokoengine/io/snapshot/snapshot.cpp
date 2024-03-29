/// @file
#include "snapshot.hpp"

#include "characters.hpp"
#include "parser.hpp"
#include "pusher_step.hpp"
#include "tessellation_impl.hpp"

#include <algorithm>
#include <boost/algorithm/string.hpp>

using sokoengine::implementation::Characters;
using sokoengine::implementation::is_blank;
using sokoengine::implementation::strings_t;
using sokoengine::implementation::TessellationImpl;
using std::invalid_argument;
using std::make_unique;
using std::string;

namespace sokoengine {
  namespace io {

    using snapshot_parsing::Parser;
    using snapshot_parsing::evaluated_ast::Jump;
    using snapshot_parsing::evaluated_ast::PusherSelection;
    using snapshot_parsing::evaluated_ast::SnapshotData;
    using snapshot_parsing::evaluated_ast::Steps;

    class LIBSOKOENGINE_LOCAL Snapshot::PIMPL {
    public:
      string m_title;
      string m_solver;
      string m_notes;

      Tessellation m_tessellation;

      bool         m_was_parsed = false;
      string       m_moves_data;
      SnapshotData m_parsed_moves;
      size_t       m_moves_count  = 0;
      size_t       m_pushes_count = 0;
      size_t       m_jumps_count  = 0;
      bool         m_is_reverse   = false;

      PIMPL(const Tessellation &tessellation, const string &moves_data)
        : m_tessellation(tessellation)
        , m_was_parsed(false)
        , m_moves_data(moves_data) {}

      void reparse() {
        m_parsed_moves = SnapshotData();
        m_pushes_count = 0;
        m_moves_count  = 0;
        m_jumps_count  = 0;
        m_is_reverse   = false;

        m_parsed_moves = Parser::parse(m_moves_data);

        for (const auto &part_variant : m_parsed_moves) {
          std::visit(
            [this](auto &part) {
              if (part.is_jump) {
                m_jumps_count++;
                m_is_reverse = true;
              }
              m_moves_count += part.moves_count();
              m_pushes_count += part.pushes_count();
            },
            part_variant
          );
        }
      }

      void reparse_if_not_parsed() {
        if (!m_was_parsed)
          reparse();
      }
    };

    Snapshot::Snapshot(const Tessellation &tessellation, const string &moves_data)
      : m_impl(make_unique<Snapshot::PIMPL>(tessellation, moves_data)) {
      if (!is_blank(moves_data) && !Characters::is_snapshot(moves_data)) {
        throw invalid_argument("Invalid characters in snapshot string!");
      }
    }

    Snapshot::Snapshot(const Snapshot &rv)
      : m_impl(make_unique<PIMPL>(*rv.m_impl)) {}

    Snapshot &Snapshot::operator=(const Snapshot &rv) {
      if (this != &rv)
        m_impl = make_unique<PIMPL>(*rv.m_impl);
      return *this;
    }

    Snapshot::Snapshot(Snapshot &&rv)
      : m_impl(move(rv.m_impl)) {}

    Snapshot &Snapshot::operator=(Snapshot &&rv) {
      if (this != &rv) {
        m_impl.swap(rv.m_impl);
      }
      return *this;
    }

    Snapshot::~Snapshot() = default;

    Tessellation Snapshot::tessellation() const { return m_impl->m_tessellation; }

    const string &Snapshot::title() const { return m_impl->m_title; }

    string &Snapshot::title() { return m_impl->m_title; }

    const string &Snapshot::solver() const { return m_impl->m_solver; }

    string &Snapshot::solver() { return m_impl->m_solver; }

    const string &Snapshot::notes() const { return m_impl->m_notes; }

    string &Snapshot::notes() { return m_impl->m_notes; }

    string Snapshot::to_str(bool rle_encode) const {
      m_impl->reparse_if_not_parsed();

      strings_t lines;
      for (const auto &part_variant : m_impl->m_parsed_moves) {
        std::visit(
          [&lines](auto &part) {
            lines.push_back(part.to_str());
          },
          part_variant
        );
      }
      string retv = boost::join(lines, "");

      // Reverse snapshots must start with jump, even if it is empty one
      if (m_impl->m_is_reverse &&
      (m_impl->m_parsed_moves.size() == 0 ||
       (m_impl->m_parsed_moves.size() != 0 && retv[0] != Characters::JUMP_BEGIN))) {
        retv = string(1, Characters::JUMP_BEGIN) + Characters::JUMP_END + retv;
      }

      if (rle_encode) {
        retv = Rle::encode(retv);
      }

      return retv;
    }

    string Snapshot::str() const { return to_str(false); }

    string Snapshot::repr() const {
      string klass_name = "Snapshot";

      string moves = to_str(false);

      return klass_name + "(" + implementation::to_str(m_impl->m_tessellation)
           + ", moves_data=\"" + moves + "\")";
    }

    const string &Snapshot::moves_data() const {
      m_impl->reparse_if_not_parsed();
      return m_impl->m_moves_data;
    }

    void Snapshot::set_moves_data(const string &rv) {
      if (!is_blank(rv) && !Characters::is_snapshot(rv)) {
        throw invalid_argument("Invalid characters in snapshot string!");
      }
      m_impl->m_moves_data = rv;
      m_impl->m_was_parsed = false;
    }

    pusher_steps_t Snapshot::pusher_steps() const {
      m_impl->reparse_if_not_parsed();

      pusher_steps_t          retv;
      const TessellationImpl &tessellation =
        TessellationImpl::instance(m_impl->m_tessellation);

      for (const auto &part_variant : m_impl->m_parsed_moves) {
        std::visit(
          [&retv, &tessellation](auto &part) {
            pusher_steps_t part_steps = part.pusher_steps(tessellation);
            retv.insert(retv.end(), part_steps.cbegin(), part_steps.cend());
          },
          part_variant
        );
      }

      return retv;
    }

    void Snapshot::set_pusher_steps(const pusher_steps_t &rv) {
      size_t i    = 0;
      size_t iend = rv.size();

      m_impl->m_parsed_moves = SnapshotData();
      m_impl->m_pushes_count = 0;
      m_impl->m_moves_count  = 0;
      m_impl->m_jumps_count  = 0;
      m_impl->m_is_reverse   = false;
      m_impl->m_was_parsed   = true;

      const TessellationImpl &tessellation =
        TessellationImpl::instance(m_impl->m_tessellation);

      while (i < iend) {
        if (rv[i].is_jump()) {
          Jump jump;
          while (i < iend && rv[i].is_jump()) {
            jump.data.append(1, tessellation.pusher_step_to_char(rv[i]));
            if (rv[i].is_current_pos()) {
              jump.data.append(1, CURRENT_POSITION_CH);
            }
            i++;
          }
          m_impl->m_jumps_count++;
          m_impl->m_is_reverse = true;
          m_impl->m_moves_count += jump.moves_count();
          m_impl->m_parsed_moves.push_back(jump);
        }

        else if (rv[i].is_pusher_selection()) {
          PusherSelection pusher_selection;
          while (i < iend && rv[i].is_pusher_selection()) {
            pusher_selection.data.append(1, tessellation.pusher_step_to_char(rv[i]));
            if (rv[i].is_current_pos()) {
              pusher_selection.data.append(1, CURRENT_POSITION_CH);
            }
            i++;
          }
          m_impl->m_parsed_moves.push_back(pusher_selection);
        }

        else {
          Steps steps;
          while (i < iend && !rv[i].is_jump() && !rv[i].is_pusher_selection()) {
            steps.data.append(1, tessellation.pusher_step_to_char(rv[i]));
            if (rv[i].is_current_pos()) {
              steps.data.append(1, CURRENT_POSITION_CH);
            }
            i++;
          }
          m_impl->m_pushes_count += steps.pushes_count();
          m_impl->m_moves_count += steps.moves_count();
          m_impl->m_parsed_moves.push_back(steps);
        }
      }

      m_impl->m_moves_data = to_str(false);
    }

    size_t Snapshot::pushes_count() const {
      m_impl->reparse_if_not_parsed();
      return m_impl->m_pushes_count;
    }

    size_t Snapshot::moves_count() const {
      m_impl->reparse_if_not_parsed();
      return m_impl->m_moves_count;
    }

    size_t Snapshot::jumps_count() const {
      m_impl->reparse_if_not_parsed();
      return m_impl->m_is_reverse;
    }

    bool Snapshot::is_reverse() const {
      m_impl->reparse_if_not_parsed();
      return m_impl->m_is_reverse;
    }

    ///
    /// Tries to parse line as snapshot string and prints parser AST as json. Intended
    /// to be used for debugging purposes.
    ///
    string Snapshot::ast_json(const std::string &line) {
      return Parser::ast_json(line);
    }

  } // namespace io
} // namespace sokoengine
