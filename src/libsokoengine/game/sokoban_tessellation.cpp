#include "sokoban_tessellation.hpp"

#include "pusher_step.hpp"
#include "snapshot.hpp"

#include <map>
#include <memory>

using std::invalid_argument;
using std::string;

namespace sokoengine {
namespace game {

using implementation::direction_str;

const Directions &SokobanTessellation::legal_directions() const {
  static const Directions retv = {
    Direction::LEFT, Direction::RIGHT, Direction::UP, Direction::DOWN};
  return retv;
}

position_t SokobanTessellation::neighbor_position(
  position_t       position,
  const Direction &direction,
  board_size_t     width,
  board_size_t     height
) const {
  position_t row = index_y(position, width), column = index_x(position, width);
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
        "Unsupported direction " + direction_str(direction)
        + " for SokobanTessellation!"
      );
  }

  if (is_on_board_2d(column, row, width, height))
    return index_1d(column, row, width);
  else
    return Config::NO_POS;
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
      throw invalid_argument(
        "Illegal PusherStep direction " + direction_str(rv.direction())
        + " in SokobanTessellation!"

      );
  }
}

PusherStep SokobanTessellation::char_to_pusher_step(char rv) const {
  switch (rv) {
    case io::Snapshot::l:
      return PusherStep(Direction::LEFT, Config::NO_ID);
    case io::Snapshot::L:
      return PusherStep(Direction::LEFT, Config::DEFAULT_ID);
    case io::Snapshot::u:
      return PusherStep(Direction::UP, Config::NO_ID);
    case io::Snapshot::U:
      return PusherStep(Direction::UP, Config::DEFAULT_ID);
    case io::Snapshot::r:
      return PusherStep(Direction::RIGHT, Config::NO_ID);
    case io::Snapshot::R:
      return PusherStep(Direction::RIGHT, Config::DEFAULT_ID);
    case io::Snapshot::d:
      return PusherStep(Direction::DOWN, Config::NO_ID);
    case io::Snapshot::D:
      return PusherStep(Direction::DOWN, Config::DEFAULT_ID);
    default:
      throw invalid_argument(
        string("Illegal PusherStep character '") + rv + "' in SokobanTessellation!"
      );
  }
}

} // namespace game
} // namespace sokoengine
