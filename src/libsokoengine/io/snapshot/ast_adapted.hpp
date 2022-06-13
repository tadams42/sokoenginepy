#ifndef AST_ADAPTED_BDC825C2_4FAB_4173_9B94_185BD7430359
#define AST_ADAPTED_BDC825C2_4FAB_4173_9B94_185BD7430359

#include "ast.hpp"

#include <boost/fusion/include/adapt_struct.hpp>

BOOST_FUSION_ADAPT_STRUCT(sokoengine::io::snapshot_parsing::ast::Moves, data)
BOOST_FUSION_ADAPT_STRUCT(sokoengine::io::snapshot_parsing::ast::Pushes, data)
BOOST_FUSION_ADAPT_STRUCT(sokoengine::io::snapshot_parsing::ast::Steps, data)
BOOST_FUSION_ADAPT_STRUCT(sokoengine::io::snapshot_parsing::ast::PusherSelection, data)
BOOST_FUSION_ADAPT_STRUCT(sokoengine::io::snapshot_parsing::ast::Jump, data)
BOOST_FUSION_ADAPT_STRUCT(sokoengine::io::snapshot_parsing::ast::Snapshot, data)

#endif // HEADER_GUARD
