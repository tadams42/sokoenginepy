#include "trioban_tessellation.hpp"

#include "pusher_step.hpp"
#include "snapshot.hpp"

using sokoengine::io::CellOrientation;
using std::invalid_argument;
using std::string;

namespace sokoengine {
namespace game {

using implementation::direction_str;

const Directions &TriobanTessellation::legal_directions() const {
  static const Directions retv{
    Direction::LEFT,
    Direction::RIGHT,
    Direction::NORTH_EAST,
    Direction::NORTH_WEST,
    Direction::SOUTH_EAST,
    Direction::SOUTH_WEST};
  return retv;
}

position_t TriobanTessellation::neighbor_position(
  position_t       position,
  const Direction &direction,
  board_size_t     width,
  board_size_t     height
) const {
  if (!is_on_board_1d(position, width, height))
    return Config::NO_POS;
  position_t row = index_y(position, width), column = index_x(position, width);
  int8_t     dy, dx;
  bool       tpd =
    cell_orientation(position, width, height) == CellOrientation::TRIANGLE_DOWN;

  switch (direction) {
    case Direction::LEFT:
      dy = 0;
      dx = -1;
      break;
    case Direction::RIGHT:
      dy = 0;
      dx = 1;
      break;
    case Direction::NORTH_EAST:
      if (tpd) {
        dy = -1;
        dx = 0;
      } else {
        dy = 0;
        dx = 1;
      }
      break;
    case Direction::NORTH_WEST:
      if (tpd) {
        dy = -1;
        dx = 0;
      } else {
        dy = 0;
        dx = -1;
      }
      break;
    case Direction::SOUTH_EAST:
      if (tpd) {
        dy = 0;
        dx = 1;
      } else {
        dy = 1;
        dx = 0;
      }
      break;
    case Direction::SOUTH_WEST:
      if (tpd) {
        dy = 0;
        dx = -1;
      } else {
        dy = 1;
        dx = 0;
      }
      break;
    default:
      throw invalid_argument(
        "Unsupported direction " + direction_str(direction)
        + " for TriobanTessellation!"
      );
  }

  row += dy;
  column += dx;
  if (is_on_board_2d(column, row, width, height))
    return index_1d(column, row, width);
  else
    return Config::NO_POS;
}

PusherStep TriobanTessellation::char_to_pusher_step(char rv) const {
  switch (rv) {
    case io::Snapshot::l:
      return PusherStep(Direction::LEFT, Config::NO_ID);
    case io::Snapshot::L:
      return PusherStep(Direction::LEFT, Config::DEFAULT_ID);

    case io::Snapshot::r:
      return PusherStep(Direction::RIGHT, Config::NO_ID);
    case io::Snapshot::R:
      return PusherStep(Direction::RIGHT, Config::DEFAULT_ID);

    case io::Snapshot::n:
      return PusherStep(Direction::NORTH_EAST, Config::NO_ID);
    case io::Snapshot::N:
      return PusherStep(Direction::NORTH_EAST, Config::DEFAULT_ID);

    case io::Snapshot::u:
      return PusherStep(Direction::NORTH_WEST, Config::NO_ID);
    case io::Snapshot::U:
      return PusherStep(Direction::NORTH_WEST, Config::DEFAULT_ID);

    case io::Snapshot::d:
      return PusherStep(Direction::SOUTH_EAST, Config::NO_ID);
    case io::Snapshot::D:
      return PusherStep(Direction::SOUTH_EAST, Config::DEFAULT_ID);

    case io::Snapshot::s:
      return PusherStep(Direction::SOUTH_WEST, Config::NO_ID);
    case io::Snapshot::S:
      return PusherStep(Direction::SOUTH_WEST, Config::DEFAULT_ID);

    default:
      throw invalid_argument(
        string("Illegal PusherStep character '") + rv + "' in TriobanTessellation!"
      );
  }
}

char TriobanTessellation::pusher_step_to_char(const PusherStep &rv) const {
  switch (rv.direction()) {
    case Direction::LEFT:
      return rv.is_push_or_pull() ? io::Snapshot::L : io::Snapshot::l;
    case Direction::RIGHT:
      return rv.is_push_or_pull() ? io::Snapshot::R : io::Snapshot::r;
    case Direction::NORTH_EAST:
      return rv.is_push_or_pull() ? io::Snapshot::N : io::Snapshot::n;
    case Direction::NORTH_WEST:
      return rv.is_push_or_pull() ? io::Snapshot::U : io::Snapshot::u;
    case Direction::SOUTH_EAST:
      return rv.is_push_or_pull() ? io::Snapshot::D : io::Snapshot::d;
    case Direction::SOUTH_WEST:
      return rv.is_push_or_pull() ? io::Snapshot::S : io::Snapshot::s;
    default:
      throw invalid_argument(
        "Illegal PusherStep direction " + direction_str(rv.direction())
        + " in TriobanTessellation!"
      );
  }
}

CellOrientation TriobanTessellation::cell_orientation(
  position_t pos, board_size_t width, board_size_t height
) const {
  position_t column = index_column(pos, width);
  position_t row    = index_row(pos, width);
  return (column + (row % 2)) % 2 == 0 ? CellOrientation::TRIANGLE_DOWN
                                       : CellOrientation::DEFAULT;
}

GraphType TriobanTessellation::graph_type() const { return GraphType::DIRECTED_MULTI; }

} // namespace game
} // namespace sokoengine
