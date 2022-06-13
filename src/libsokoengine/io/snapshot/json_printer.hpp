#ifndef PRINT_BDC825C2_4FAB_4173_9B94_185BD7430359
#define PRINT_BDC825C2_4FAB_4173_9B94_185BD7430359

#include "ast.hpp"

#include <ostream>

namespace sokoengine {
namespace io {
namespace snapshot_parsing {
namespace ast {

struct LIBSOKOENGINE_LOCAL JsonPrinter {
  typedef void result_type;

  std::ostream &out;

  JsonPrinter(std::ostream &out) : out(out) {}

  std::string quoted(const std::string &src) const { return '"' + src + '"'; }

  void operator()(const Moves &o) const {
    out << '{' << quoted("type") << ':' << quoted("moves") << ',' << quoted("data")
        << ':' << quoted(o.data) << "}";
  }

  void operator()(const Pushes &o) const {
    out << '{' << quoted("type") << ':' << quoted("pushes") << ',' << quoted("data")
        << ':' << quoted(o.data) << "}";
  }

  void operator()(const Steps &o) const {
    out << '{' << quoted("type") << ':' << quoted("steps") << ',' << quoted("data")
        << ':' << '[';

    auto actual_delim = ",";
    auto delim = "";

    for (auto const &expr : o.data) {
      out << delim;
      boost::apply_visitor(*this, expr);
      delim = actual_delim;
    }

    out << ']' << '}';
  }

  void operator()(const Jump &o) const {
    out << '{' << quoted("type") << ':' << quoted("jump") << ',' << quoted("data")
        << ':';
    (*this)(o.data);
    out << '}';
  }

  void operator()(const PusherSelection &o) const {
    out << '{' << quoted("type") << ':' << quoted("pusher_selection") << ','
        << quoted("data") << ':';
    (*this)(o.data);
    out << '}';
  }

  void operator()(const Snapshot &o) const {
    out << '{' << quoted("type") << ':' << quoted("snapshot") << ',' << quoted("data")
        << ':' << '[';

    auto actual_delim = ",";
    auto delim = "";

    for (auto const &expr : o.data) {
      out << delim;
      boost::apply_visitor(*this, expr);
      delim = actual_delim;
    }

    out << ']' << '}';
  }
};

} // namespace ast
} // namespace snapshot_parsing
} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
