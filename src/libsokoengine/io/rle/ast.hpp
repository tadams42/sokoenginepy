#ifndef AST_78FAAA5B_FC6F_4891_8173_B2B3C2BFA410
#define AST_78FAAA5B_FC6F_4891_8173_B2B3C2BFA410

#include "sokoengine_config.hpp"

#include <boost/spirit/home/x3/support/ast/variant.hpp>
#include <list>

namespace sokoengine {
  namespace io {
    namespace sok_rle {

      namespace x3 = boost::spirit::x3;

      namespace ast {
        // clang-format off
        // Beware of single-member-is-container AST structs
        //
        // https://github.com/boostorg/spirit/issues/463
        // https://github.com/boostorg/spirit/pull/178
        // https://stackoverflow.com/questions/50252680/boost-spirit-x3-parser-no-type-named-type-in
        //
        // When making an AST type, I'm always going into 1 of these:
        //
        // AST type of 1 member T: overload operator=(T)
        // AST type of 2+ members: BOOST_FUSION_ADAPT_STRUCT
        // AST type that inherits from some container (no further code required but must not contain members)
        // AST type that inherits from x3::variant: add using base_type::base_type;, using base_type::operator=, must not contain members
        // Other mixes of AST types end in various (long long) compilation errors.
        // clang-format on

        typedef char Atom;

        struct LIBSOKOENGINE_LOCAL Atoms : std::vector<char> {
          using std::vector<char>::vector;
          using std::vector<char>::operator=;
        };

        struct Group;

        struct LIBSOKOENGINE_LOCAL AtomOrGroup
          : x3::variant<Atom, x3::forward_ast<Group>> {
          using base_type::base_type;
          using base_type::operator=;
        };

        struct LIBSOKOENGINE_LOCAL RleChunk {
          unsigned int cnt;
          AtomOrGroup  data;
        };

        struct LIBSOKOENGINE_LOCAL AtomsOrRleOrGroup
          : x3::variant<Atoms, RleChunk, x3::forward_ast<Group>> {
          using base_type::base_type;
          using base_type::operator=;
        };

        struct LIBSOKOENGINE_LOCAL Group : std::list<AtomsOrRleOrGroup> {
          using std::list<AtomsOrRleOrGroup>::list;
          using std::list<AtomsOrRleOrGroup>::operator=;
        };

        struct LIBSOKOENGINE_LOCAL RleData : std::list<AtomsOrRleOrGroup> {
          using std::list<AtomsOrRleOrGroup>::list;
          using std::list<AtomsOrRleOrGroup>::operator=;
        };

      } // namespace ast
    }   // namespace sok_rle
  }     // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
