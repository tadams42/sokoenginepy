#ifndef COMMON_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define COMMON_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include <vector>

#include "sokoengine_config.hpp"
#include "direction.hpp"

namespace sokoengine {

typedef int position_t;
typedef int piece_id_t;
typedef std::vector<position_t> Positions;
typedef std::vector<Direction> Directions;

enum class LIBSOKOENGINE_API CellOrientation : int {
  DEFAULT = 0,
  TRIANGLE_DOWN = 1,
  OCTAGON = 2
};

enum BoardConstants {
  ///
  /// Default ID of a piece (box, goal or pusher)
  /// Piece ids are assigned sequentially on board creation and are not changed
  /// during lifetime of a board. Piece id is used to diferentiate this piece
  /// from other pieces of the same kind: ie. one box from another.
  ///
  DEFAULT_PIECE_ID = 1,
  ///
  /// Value that represents piece ID in cases where one ID was requested but it
  /// cant't be returned.
  ///
  NULL_ID = -2,
  ///
  /// Value that represents board position in cases where position was requested
  /// but it cant't be returned.
  ///
  NULL_POSITION = -1,
};

} // namespace sokoengine

#endif // HEADER_GUARD
