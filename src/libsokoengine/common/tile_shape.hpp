#ifndef TILE_SHAPE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define TILE_SHAPE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
/// @file

#include "sokoengine_config.hpp"

namespace sokoengine {

///
/// For some types of games, individual board cell "tile" depends on board position.
///
enum class LIBSOKOENGINE_API TileShape : int {
  DEFAULT,
  TRIANGLE_DOWN,
  OCTAGON,
};

///
/// Default type for set of TileShape
///
typedef std::set<TileShape> tile_shapes_t;

} // namespace sokoengine

#endif // HEADER_GUARD
