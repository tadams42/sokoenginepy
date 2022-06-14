#include "trioban_tessellation.hpp"

#include "pusher_step.hpp"
#include "snapshot.hpp"

using namespace std;

namespace sokoengine {
namespace game {

using io::CellOrientation;

const Directions &TriobanTessellation::legal_directions() const {
  static const Directions retv{Direction::LEFT,       Direction::RIGHT,
                               Direction::NORTH_EAST, Direction::NORTH_WEST,
                               Direction::SOUTH_EAST, Direction::SOUTH_WEST};
  return retv;
}

position_t TriobanTessellation::neighbor_position(position_t position,
                                                  const Direction &direction,
                                                  board_size_t width,
                                                  board_size_t height) const {
  if (!ON_BOARD(position, width, height)) return Config::MAX_POS + 1;
  position_t row = Y(position, width), column = X(position, width);
  int8_t dy, dx;
  bool tpd = cell_orientation(position, width, height) ==
             CellOrientation::TRIANGLE_DOWN;

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
      "Unsupported Direction received in TriobanTessellation neighbor_position!");
  }

  row += dy;
  column += dx;
  if (ON_BOARD(column, row, width, height))
    return index_1d(column, row, width);
  else
    return Config::MAX_POS + 1;
}

PusherStep TriobanTessellation::char_to_pusher_step(char rv) const {
  switch (rv) {
  case io::Snapshot::l:
    return PusherStep(Direction::LEFT, false);
  case io::Snapshot::L:
    return PusherStep(Direction::LEFT, true);

  case io::Snapshot::r:
    return PusherStep(Direction::RIGHT, false);
  case io::Snapshot::R:
    return PusherStep(Direction::RIGHT, true);

  case io::Snapshot::n:
    return PusherStep(Direction::NORTH_EAST, false);
  case io::Snapshot::N:
    return PusherStep(Direction::NORTH_EAST, true);

  case io::Snapshot::u:
    return PusherStep(Direction::NORTH_WEST, false);
  case io::Snapshot::U:
    return PusherStep(Direction::NORTH_WEST, true);

  case io::Snapshot::d:
    return PusherStep(Direction::SOUTH_EAST, false);
  case io::Snapshot::D:
    return PusherStep(Direction::SOUTH_EAST, true);

  case io::Snapshot::s:
    return PusherStep(Direction::SOUTH_WEST, false);
  case io::Snapshot::S:
    return PusherStep(Direction::SOUTH_WEST, true);

  default:
    throw invalid_argument("Illegal PusherStep character in TriobanTessellation!");
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
    throw invalid_argument("Illegal PusherStep direction in TriobanTessellation!");
  }
}

CellOrientation TriobanTessellation::cell_orientation(position_t pos,
                                                      board_size_t width,
                                                      board_size_t height) const {
  position_t column = COLUMN(pos, width);
  position_t row = ROW(pos, width);
  return (column + (row % 2)) % 2 == 0 ? CellOrientation::TRIANGLE_DOWN
                                       : CellOrientation::DEFAULT;
}

GraphType TriobanTessellation::graph_type() const { return GraphType::DIRECTED_MULTI; }

} // namespace game
} // namespace sokoengine
