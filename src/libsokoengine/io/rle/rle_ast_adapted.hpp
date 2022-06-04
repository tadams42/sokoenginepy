#ifndef RLE_AST_ADAPTED_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define RLE_AST_ADAPTED_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "rle_ast.hpp"

#include <boost/fusion/include/adapt_struct.hpp>

BOOST_FUSION_ADAPT_STRUCT(sokoengine::io::sok_rle::ast::Atom, data)
BOOST_FUSION_ADAPT_STRUCT(sokoengine::io::sok_rle::ast::Atoms, data)
BOOST_FUSION_ADAPT_STRUCT(sokoengine::io::sok_rle::ast::RleChunk, cnt, data)
BOOST_FUSION_ADAPT_STRUCT(sokoengine::io::sok_rle::ast::Group, data)
BOOST_FUSION_ADAPT_STRUCT(sokoengine::io::sok_rle::ast::RleData, data)

#endif // HEADER_GUARD
