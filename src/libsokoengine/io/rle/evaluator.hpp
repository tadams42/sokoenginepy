#ifndef EVAL_78FAAA5B_FC6F_4891_8173_B2B3C2BFA410
#define EVAL_78FAAA5B_FC6F_4891_8173_B2B3C2BFA410

#include "ast.hpp"

namespace sokoengine {
namespace io {
namespace sok_rle {
namespace ast {

struct LIBSOKOENGINE_LOCAL Evaluator {
  typedef void result_type;

  std::string &dest;

  Evaluator(std::string &dest) : dest(dest) {}

  // void operator()(expression const &o) const { boost::apply_visitor(*this, o); }

  void operator()(char c) const {
    if (c == '\n' || c == '\r' || c == '|')
      dest.push_back('\n');
    else
      dest.push_back(c);
  }

  void operator()(Atom const &o) const { (*this)(o.data); }

  void operator()(Atoms const &o) const {
    for (char c : o.data) {
      (*this)(c);
    }
  }

  void operator()(Group const &o) const {
    for (auto const &expr : o.data) {
      boost::apply_visitor(*this, expr);
    }
  }

  void operator()(RleChunk const &o) const {
    for (unsigned int i = 0; i < o.cnt; i++) {
      boost::apply_visitor(*this, o.data);
    }
  }

  void operator()(RleData const &o) const {
    for (auto const &expr : o.data) {
      boost::apply_visitor(*this, expr);
    }
  }
};

} // namespace ast
} // namespace sok_rle
} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
