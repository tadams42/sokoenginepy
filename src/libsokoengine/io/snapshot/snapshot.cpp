#include "snapshot.hpp"

#include "ast.hpp"
#include "parser.hpp"
#include "pusher_step.hpp"
#include "rle.hpp"
#include "tessellation.hpp"

#include "hexoban.hpp"
#include "octoban.hpp"
#include "sokoban.hpp"
#include "trioban.hpp"

#include <algorithm>
#include <boost/algorithm/string.hpp>

namespace sokoengine {
namespace io {

using namespace std;
using game::PusherStep;
using game::PusherSteps;
using game::BaseTessellation;
using game::Tessellation;
using snapshot_parsing::Parser;
using snapshot_parsing::evaluated_ast::Jump;
using snapshot_parsing::evaluated_ast::PusherSelection;
using snapshot_parsing::evaluated_ast::SnapshotData;
using snapshot_parsing::evaluated_ast::Steps;

class LIBSOKOENGINE_LOCAL Snapshot::PIMPL {
public:
  string m_title;
  string m_solver;
  Strings m_notes;

  Tessellation m_tessellation;

  bool m_was_parsed = false;
  string m_moves_data;
  SnapshotData m_parsed_moves;
  size_t m_moves_count = 0;
  size_t m_pushes_count = 0;
  size_t m_jumps_count = 0;
  bool m_is_reverse = false;

  PIMPL(const Tessellation &tessellation, const string &moves_data)
    : m_tessellation(tessellation), m_was_parsed(false), m_moves_data(moves_data) {}

  void reparse() {
    m_parsed_moves = SnapshotData();
    m_pushes_count = 0;
    m_moves_count = 0;
    m_jumps_count = 0;
    m_is_reverse = false;

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
        part_variant);
    }
  }

  void reparse_if_not_parsed() {
    if (!m_was_parsed) reparse();
  }
};

Snapshot::Snapshot(const Tessellation &tessellation, const string &moves_data)
  : m_impl(make_unique<Snapshot::PIMPL>(tessellation, moves_data)) {
  if (!is_blank(moves_data) && !Snapshot::is_snapshot(moves_data)) {
    throw invalid_argument("Invalid characters in snapshot string!");
  }
}

Snapshot::Snapshot(const Snapshot &rv) : m_impl(make_unique<PIMPL>(*rv.m_impl)) {}

Snapshot &Snapshot::operator=(const Snapshot &rv) {
  if (this != &rv) m_impl = make_unique<PIMPL>(*rv.m_impl);
  return *this;
}

Snapshot::Snapshot(Snapshot &&rv) : m_impl(move(rv.m_impl)) {}

Snapshot &Snapshot::operator=(Snapshot &&rv) {
  if (this != &rv) { m_impl.swap(rv.m_impl); }
  return *this;
}

Snapshot::~Snapshot() = default;

Tessellation Snapshot::tessellation() const { return m_impl->m_tessellation; }

const string &Snapshot::title() const { return m_impl->m_title; }
string &Snapshot::title() { return m_impl->m_title; }

const string &Snapshot::solver() const { return m_impl->m_solver; }
string &Snapshot::solver() { return m_impl->m_solver; }

const Strings &Snapshot::notes() const { return m_impl->m_notes; }
Strings &Snapshot::notes() { return m_impl->m_notes; }

string Snapshot::to_str(bool rle_encode) const {
  m_impl->reparse_if_not_parsed();

  Strings lines;
  for (const auto &part_variant : m_impl->m_parsed_moves) {
    std::visit([&lines](auto &part) { lines.push_back(part.to_str()); }, part_variant);
  }
  string retv = boost::join(lines, "");

  // Reverse snapshots must start with jump, even if it is empty one
  if (m_impl->m_is_reverse &&
      (m_impl->m_parsed_moves.size() == 0 ||
       (m_impl->m_parsed_moves.size() != 0 && retv[0] != Snapshot::JUMP_BEGIN))) {
    retv = string(1, Snapshot::JUMP_BEGIN) + Snapshot::JUMP_END + retv;
  }

  if (rle_encode) { retv = Rle::encode(retv); }

  return retv;
}

string Snapshot::str() const { return to_str(false); }

string Snapshot::repr() const {
  string klass_name = "Snapshot";
  if (typeid(*this) == typeid(const SokobanSnapshot &)) klass_name = "SokobanSnapshot";
  if (typeid(*this) == typeid(const TriobanSnapshot &)) klass_name = "TriobanSnapshot";
  if (typeid(*this) == typeid(const OctobanSnapshot &)) klass_name = "OctobanSnapshot";
  if (typeid(*this) == typeid(const HexobanSnapshot &)) klass_name = "HexobanSnapshot";

  string moves = to_str(false);

  return klass_name + "(moves_data=\"" + moves + "\")";
}

const string &Snapshot::moves_data() const {
  m_impl->reparse_if_not_parsed();
  return m_impl->m_moves_data;
}

void Snapshot::set_moves_data(const string &rv) {
  if (!is_blank(rv) && !Snapshot::is_snapshot(rv)) {
    throw invalid_argument("Invalid characters in snapshot string!");
  }
  m_impl->m_moves_data = rv;
  m_impl->m_was_parsed = false;
}

PusherSteps Snapshot::pusher_steps() const {
  m_impl->reparse_if_not_parsed();

  PusherSteps retv;
  const BaseTessellation &tessellation =
    BaseTessellation::instance(m_impl->m_tessellation);

  for (const auto &part_variant : m_impl->m_parsed_moves) {
    std::visit(
      [&retv, &tessellation](auto &part) {
        PusherSteps part_steps = part.pusher_steps(tessellation);
        retv.insert(retv.end(), part_steps.cbegin(), part_steps.cend());
      },
      part_variant);
  }

  return retv;
}

void Snapshot::set_pusher_steps(const PusherSteps &rv) {
  size_t i = 0;
  size_t iend = rv.size();

  m_impl->m_parsed_moves = SnapshotData();
  m_impl->m_pushes_count = 0;
  m_impl->m_moves_count = 0;
  m_impl->m_jumps_count = 0;
  m_impl->m_is_reverse = false;
  m_impl->m_was_parsed = true;

  const BaseTessellation &tessellation =
    BaseTessellation::instance(m_impl->m_tessellation);

  while (i < iend) {
    if (rv[i].is_jump()) {
      Jump jump;
      while (i < iend && rv[i].is_jump()) {
        jump.data.append(1, tessellation.pusher_step_to_char(rv[i]));
        if (rv[i].is_current_pos()) { jump.data.append(1, CURRENT_POSITION_CH); }
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
        if (rv[i].is_current_pos()) { steps.data.append(1, CURRENT_POSITION_CH); }
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

bool Snapshot::is_snapshot(const string &line) {
  bool only_digits_and_spaces = all_of(line.cbegin(), line.cend(), [](char c) -> bool {
    return (isdigit(c) != 0) || (isspace(c) != 0);
  });
  return !only_digits_and_spaces &&
         all_of(line.begin(), line.end(), [](char c) -> bool {
           return isdigit(c) || isspace(c) || Snapshot::is_pusher_step(c) ||
                  Snapshot::is_marker(c);
         });
}

///
/// Tries to parse line as snapshot string and prints parser AST as json. Intended to be
/// used for debugging purposes.
///
string Snapshot::ast_json(const std::string &line) { return Parser::ast_json(line); }

} // namespace io
} // namespace sokoengine
