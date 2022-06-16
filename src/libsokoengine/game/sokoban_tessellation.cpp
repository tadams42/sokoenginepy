#include "sokoban_tessellation.hpp"

#include "pusher_step.hpp"
#include "snapshot.hpp"

#include <map>
#include <memory>

using namespace std;

namespace sokoengine {
namespace game {

const Directions &SokobanTessellation::legal_directions() const {
  static const Directions retv = {Direction::LEFT, Direction::RIGHT, Direction::UP,
                                  Direction::DOWN};
  return retv;
}

position_t SokobanTessellation::neighbor_position(position_t position,
                                                  const Direction &direction,
                                                  board_size_t width,
                                                  board_size_t height) const {
  position_t row = Y(position, width), column = X(position, width);
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
  default:
    throw invalid_argument(
      "Unsupported Direction received in SokobanTessellation neighbor_position!");
  }

  if (ON_BOARD(column, row, width, height))
    return index_1d(column, row, width);
  else
    return Config::MAX_POS + 1;
}

char SokobanTessellation::pusher_step_to_char(const PusherStep &rv) const {
  switch (rv.direction()) {
  case Direction::LEFT:
    return rv.is_push_or_pull() ? io::Snapshot::L : io::Snapshot::l;
  case Direction::UP:
    return rv.is_push_or_pull() ? io::Snapshot::U : io::Snapshot::u;
  case Direction::RIGHT:
    return rv.is_push_or_pull() ? io::Snapshot::R : io::Snapshot::r;
  case Direction::DOWN:
    return rv.is_push_or_pull() ? io::Snapshot::D : io::Snapshot::d;
  default:
    throw invalid_argument("Illegal PusherStep character in SokobanTessellation!");
  }
}

PusherStep SokobanTessellation::char_to_pusher_step(char rv) const {
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
  default:
    throw invalid_argument("Illegal PusherStep direction in SokobanTessellation!");
  }
}

} // namespace game
} // namespace sokoengine
