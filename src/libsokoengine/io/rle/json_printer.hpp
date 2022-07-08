#ifndef PRINT_78FAAA5B_FC6F_4891_8173_B2B3C2BFA410
#define PRINT_78FAAA5B_FC6F_4891_8173_B2B3C2BFA410

#include "ast.hpp"

#include <ostream>

namespace sokoengine {
  namespace io {
    namespace sok_rle {
      namespace ast {

        struct LIBSOKOENGINE_LOCAL JsonPrinter {
          typedef void  result_type;
          std::ostream &out;

          JsonPrinter(std::ostream &out)
            : out(out) {}

          // void operator()(expression const &o) const { boost::apply_visitor(*this,
          // o);
          // }

          void operator()(char c) const {
            if (c == '\n' || c == '\r' || c == '|')
              out << "\\n";
            else
              out << c;
          }

          std::string quoted(const std::string &src) const { return '"' + src + '"'; }

          void operator()(const Atom &o) const { (*this)(o.data); }

          void operator()(const Atoms &o) const {
            out << '{' << quoted("type") << ':' << quoted("atoms") << ','
                << quoted("data") << ':';

            out << '"';
            for (char c : o.data) {
              (*this)(c);
            }
            out << '"' << '}';
          }

          void operator()(const Group &o) const {
            out << '{' << quoted("type") << ':' << quoted("group") << ','
                << quoted("data") << ":[";

            auto actual_delim = ",";
            auto delim        = "";

            for (const auto &expr : o.data) {
              out << delim;
              boost::apply_visitor(*this, expr);
              delim = actual_delim;
            }

            out << ']' << '}';
          }

          void operator()(const RleChunk &o) const {
            out << '{' << quoted("type") << ':' << quoted("rle_chunk") << ','
                << quoted("count") << ':' << o.cnt << ',' << quoted("data") << ':';

            const Atom *a = boost::get<Atom>(&o.data);
            if (a) {
              out << '"';
              boost::apply_visitor(*this, o.data);
              out << '"';
            } else {
              boost::apply_visitor(*this, o.data);
            }

            out << '}';
          }

          void operator()(const RleData &o) const {
            out << '{' << quoted("type") << ':' << quoted("sok_rle") << ','
                << quoted("data") << ':' << '[';

            auto actual_delim = ",";
            auto delim        = "";

            for (const auto &expr : o.data) {
              out << delim;
              boost::apply_visitor(*this, expr);
              delim = actual_delim;
            }

            out << ']' << '}';
          }
        };

      } // namespace ast
    }   // namespace sok_rle
  }     // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
