#ifndef CELL_ORIENTATION_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define CELL_ORIENTATION_0FEA723A_C86F_6753_04ABD475F6FCA5FB
/// @file

#include "sokoengine_config.hpp"

namespace sokoengine {

///
/// For some types of games, individual board cell "tile" depends on board position.
///
enum class LIBSOKOENGINE_API CellOrientation : int {
  DEFAULT,
  TRIANGLE_DOWN,
  OCTAGON,
};

///
/// Default type for set of CellOrientation
///
typedef std::set<CellOrientation> cell_orientations_t;

} // namespace sokoengine

#endif // HEADER_GUARD
