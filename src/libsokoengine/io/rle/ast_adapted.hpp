#ifndef AST_ADAPTED_78FAAA5B_FC6F_4891_8173_B2B3C2BFA410
#define AST_ADAPTED_78FAAA5B_FC6F_4891_8173_B2B3C2BFA410

#include "ast.hpp"

#include <boost/fusion/include/adapt_struct.hpp>

BOOST_FUSION_ADAPT_STRUCT(sokoengine::io::sok_rle::ast::Atom, data)
BOOST_FUSION_ADAPT_STRUCT(sokoengine::io::sok_rle::ast::Atoms, data)
BOOST_FUSION_ADAPT_STRUCT(sokoengine::io::sok_rle::ast::RleChunk, cnt, data)
BOOST_FUSION_ADAPT_STRUCT(sokoengine::io::sok_rle::ast::Group, data)
BOOST_FUSION_ADAPT_STRUCT(sokoengine::io::sok_rle::ast::RleData, data)

#endif // HEADER_GUARD
