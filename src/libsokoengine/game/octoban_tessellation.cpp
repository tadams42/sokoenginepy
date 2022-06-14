#include "octoban_tessellation.hpp"

#include "pusher_step.hpp"
#include "snapshot.hpp"

using namespace std;

namespace sokoengine {
namespace game {

using io::CellOrientation;

const Directions &OctobanTessellation::legal_directions() const {
  static const Directions retv = {Direction::LEFT,       Direction::RIGHT,
                                  Direction::UP,         Direction::DOWN,
                                  Direction::NORTH_EAST, Direction::NORTH_WEST,
                                  Direction::SOUTH_EAST, Direction::SOUTH_WEST};
  return retv;
}

position_t OctobanTessellation::neighbor_position(position_t position,
                                                  const Direction &direction,
                                                  board_size_t width,
                                                  board_size_t height) const {
  position_t row = Y(position, width), column = X(position, width);

  if (cell_orientation(position, width, height) != CellOrientation::OCTAGON &&
      (direction == Direction::NORTH_EAST || direction == Direction::NORTH_WEST ||
       direction == Direction::SOUTH_EAST || direction == Direction::SOUTH_WEST)) {
    return Config::MAX_POS + 1;
  }

  switch (direction) {
  case Direction::LEFT:
    column += -1;
    break;
  case Direction::UP:
    row += -1;
    break;
  case Direction::RIGHT:
    column += 1;
    break;
  case Direction::DOWN:
    row += 1;
    break;
  case Direction::NORTH_WEST:
    row += -1;
    column += -1;
    break;
  case Direction::NORTH_EAST:
    row += -1;
    column += 1;
    break;
  case Direction::SOUTH_WEST:
    row += 1;
    column += -1;
    break;
  case Direction::SOUTH_EAST:
    row += 1;
    column += 1;
    break;
  default:
    throw invalid_argument(
      "Unsupported Direction received in OctobanTessellation neighbor_position!");
  }
  if (ON_BOARD(column, row, width, height))
    return index_1d(column, row, width);
  else
    return Config::MAX_POS + 1;
}

PusherStep OctobanTessellation::char_to_pusher_step(char rv) const {
  switch (rv) {
  case io::Snapshot::l:
    return PusherStep(Direction::LEFT, false);
  case io::Snapshot::L:
    return PusherStep(Direction::LEFT, true);

  case io::Snapshot::u:
    return PusherStep(Direction::UP, false);
  case io::Snapshot::U:
    return PusherStep(Direction::UP, true);

  case io::Snapshot::r:
    return PusherStep(Direction::RIGHT, false);
  case io::Snapshot::R:
    return PusherStep(Direction::RIGHT, true);

  case io::Snapshot::d:
    return PusherStep(Direction::DOWN, false);
  case io::Snapshot::D:
    return PusherStep(Direction::DOWN, true);

  case io::Snapshot::w:
    return PusherStep(Direction::NORTH_WEST, false);
  case io::Snapshot::W:
    return PusherStep(Direction::NORTH_WEST, true);

  case io::Snapshot::e:
    return PusherStep(Direction::SOUTH_EAST, false);
  case io::Snapshot::E:
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
    throw invalid_argument("Illegal PusherStep direction in SokobanTessellation!");
  }
}

char OctobanTessellation::pusher_step_to_char(const PusherStep &rv) const {
  switch (rv.direction()) {
  case Direction::LEFT:
    return rv.is_push_or_pull() ? io::Snapshot::L : io::Snapshot::l;
  case Direction::UP:
    return rv.is_push_or_pull() ? io::Snapshot::U : io::Snapshot::u;
  case Direction::RIGHT:
    return rv.is_push_or_pull() ? io::Snapshot::R : io::Snapshot::r;
  case Direction::DOWN:
    return rv.is_push_or_pull() ? io::Snapshot::D : io::Snapshot::d;
  case Direction::NORTH_WEST:
    return rv.is_push_or_pull() ? io::Snapshot::W : io::Snapshot::w;
  case Direction::SOUTH_EAST:
    return rv.is_push_or_pull() ? io::Snapshot::E : io::Snapshot::e;
  case Direction::NORTH_EAST:
    return rv.is_push_or_pull() ? io::Snapshot::N : io::Snapshot::n;
  case Direction::SOUTH_WEST:
    return rv.is_push_or_pull() ? io::Snapshot::S : io::Snapshot::s;
  default:
    throw invalid_argument("Illegal PusherStep direction in OctobanTessellation!");
  }
}

CellOrientation OctobanTessellation::cell_orientation(position_t pos,
                                                      board_size_t width,
                                                      board_size_t height) const {
  position_t column = COLUMN(pos, width);
  position_t row = ROW(pos, width);
  return ((column + (row % 2)) % 2 == 0) ? CellOrientation::OCTAGON
                                         : CellOrientation::DEFAULT;
}

} // namespace game
} // namespace sokoengine
