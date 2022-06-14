#ifndef AST_78FAAA5B_FC6F_4891_8173_B2B3C2BFA410
#define AST_78FAAA5B_FC6F_4891_8173_B2B3C2BFA410

#include "config.hpp"

#include <boost/spirit/home/x3/support/ast/variant.hpp>
#include <list>

namespace sokoengine {
namespace io {
namespace sok_rle {

namespace x3 = boost::spirit::x3;

namespace ast {

struct LIBSOKOENGINE_LOCAL Atom {
  char data;
};

struct LIBSOKOENGINE_LOCAL Atoms {
  std::string data;
};

struct Group;

struct LIBSOKOENGINE_LOCAL AtomOrGroup : x3::variant<Atom, x3::forward_ast<Group>> {
  using base_type::base_type;
  using base_type::operator=;
};

struct LIBSOKOENGINE_LOCAL RleChunk {
  unsigned int cnt;
  AtomOrGroup data;
};

struct LIBSOKOENGINE_LOCAL AtomsOrRleOrGroup : x3::variant<Atoms, RleChunk, x3::forward_ast<Group>> {
  using base_type::base_type;
  using base_type::operator=;
};

struct LIBSOKOENGINE_LOCAL Group {
  std::list<AtomsOrRleOrGroup> data;
};

struct LIBSOKOENGINE_LOCAL RleData {
  std::list<AtomsOrRleOrGroup> data;
};

} // namespace ast
} // namespace sok_rle
} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
