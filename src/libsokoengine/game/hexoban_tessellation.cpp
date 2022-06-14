#include "hexoban_tessellation.hpp"

#include "pusher_step.hpp"
#include "snapshot.hpp"

using namespace std;

namespace sokoengine {
namespace game {

const Directions &HexobanTessellation::legal_directions() const {
  static const Directions retv = {Direction::LEFT,       Direction::RIGHT,
                                  Direction::NORTH_EAST, Direction::NORTH_WEST,
                                  Direction::SOUTH_EAST, Direction::SOUTH_WEST};
  return retv;
}

position_t HexobanTessellation::neighbor_position(position_t position,
                                                  const Direction &direction,
                                                  board_size_t width,
                                                  board_size_t height) const {
  position_t row = Y(position, width), column = X(position, width);
  switch (direction) {
  case Direction::LEFT:
    column += -1;
    break;
  case Direction::RIGHT:
    column += 1;
    break;
  case Direction::NORTH_EAST:
    column += row % 2;
    row -= 1;
    break;
  case Direction::NORTH_WEST:
    column -= (row + 1) % 2;
    row -= 1;
    break;
  case Direction::SOUTH_EAST:
    column += row % 2;
    row += 1;
    break;
  case Direction::SOUTH_WEST:
    column -= (row + 1) % 2;
    row += 1;
    break;
  default:
    throw invalid_argument(
      "Unsupported Direction received in HexobanTessellation neighbor_position!");
  }

  if (ON_BOARD(column, row, width, height))
    return index_1d(column, row, width);
  else
    return Config::MAX_POS + 1;
}

PusherStep HexobanTessellation::char_to_pusher_step(char rv) const {
  switch (rv) {
  case io::Snapshot::l:
    return PusherStep(Direction::LEFT, false);
  case io::Snapshot::L:
    return PusherStep(Direction::LEFT, true);

  case io::Snapshot::r:
    return PusherStep(Direction::RIGHT, false);
  case io::Snapshot::R:
    return PusherStep(Direction::RIGHT, true);

  case io::Snapshot::u:
    return PusherStep(Direction::NORTH_WEST, false);
  case io::Snapshot::U:
    return PusherStep(Direction::NORTH_WEST, true);

  case io::Snapshot::d:
    return PusherStep(Direction::SOUTH_EAST, false);
  case io::Snapshot::D:
    return PusherStep(Direction::SOUTH_EAST, true);

  case io::Snapshot::n:
    return PusherStep(Direction::NORTH_EAST, false);
  case io::Snapshot::N:
    return PusherStep(Direction::NORTH_EAST, true);

  case io::Snapshot::s:
    return PusherStep(Direction::SOUTH_WEST, false);
  case io::Snapshot::S:
    return PusherStep(Direction::SOUTH_WEST, true);

  default:
    throw invalid_argument("Illegal PusherStep character in HexobanTessellation!");
  }
}

char HexobanTessellation::pusher_step_to_char(const PusherStep &rv) const {
  switch (rv.direction()) {
  case Direction::LEFT:
    return rv.is_push_or_pull() ? io::Snapshot::L : io::Snapshot::l;
  case Direction::RIGHT:
    return rv.is_push_or_pull() ? io::Snapshot::R : io::Snapshot::r;
  case Direction::NORTH_WEST:
    return rv.is_push_or_pull() ? io::Snapshot::U : io::Snapshot::u;
  case Direction::SOUTH_EAST:
    return rv.is_push_or_pull() ? io::Snapshot::D : io::Snapshot::d;
  case Direction::NORTH_EAST:
    return rv.is_push_or_pull() ? io::Snapshot::N : io::Snapshot::n;
  case Direction::SOUTH_WEST:
    return rv.is_push_or_pull() ? io::Snapshot::S : io::Snapshot::s;
  default:
    throw invalid_argument("Illegal PusherStep direction in HexobanTessellation!");
  }
}

} // namespace game
} // namespace sokoengine
