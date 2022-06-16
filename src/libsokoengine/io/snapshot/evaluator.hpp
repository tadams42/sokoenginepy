#ifndef EVAL_BDC825C2_4FAB_4173_9B94_185BD7430359
#define EVAL_BDC825C2_4FAB_4173_9B94_185BD7430359

#include "ast.hpp"

namespace sokoengine {
namespace io {
namespace snapshot_parsing {
namespace ast {

using evaluated_ast::SnapshotData;
using std::string;

struct LIBSOKOENGINE_LOCAL Evaluator {
  typedef void result_type;

  SnapshotData &dest;
  string steps_buffer;

  Evaluator(SnapshotData &dest) : dest(dest) {}

  // void operator()(expression const &o) const { boost::apply_visitor(*this, o); }

  void operator()(const Moves &o) const {
    string &buff = const_cast<string &>(steps_buffer);
    buff += o.data;
  }

  void operator()(const Pushes &o) const {
    string &buff = const_cast<string &>(steps_buffer);
    buff += o.data;
  }

  void operator()(const Steps &o) const {
    for (auto const &expr : o.data) {
      boost::apply_visitor(*this, expr);
    }
    evaluated_ast::Steps evaluated;
    string &buff = const_cast<string &>(steps_buffer);
    std::swap(buff, evaluated.data);
    dest.push_back(evaluated);
  }

  void operator()(const Jump &o) const {
    (*this)(o.data);
    evaluated_ast::Jump evaluated;
    string &buff = const_cast<string &>(steps_buffer);
    std::swap(buff, evaluated.data);
    dest.push_back(evaluated);
  }

  void operator()(const PusherSelection &o) const {
    (*this)(o.data);
    evaluated_ast::PusherSelection evaluated;
    string &buff = const_cast<string &>(steps_buffer);
    std::swap(buff, evaluated.data);
    dest.push_back(evaluated);
  }

  void operator()(const Snapshot &o) const {
    for (auto const &expr : o.data) {
      boost::apply_visitor(*this, expr);
    }
  }
};

} // namespace ast
} // namespace snapshot_parsing
} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
