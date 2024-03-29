/// @file
#include "sokoban_tessellation.hpp"

#include "characters.hpp"
#include "pusher_step.hpp"

using std::invalid_argument;
using std::string;

namespace sokoengine {
namespace implementation {

static const directions_t SOK_LEGAL_DIRECTIONS = {
  Direction::LEFT, Direction::RIGHT, Direction::UP, Direction::DOWN};

const directions_t &SokobanTessellation::legal_directions() const {
  return SOK_LEGAL_DIRECTIONS;
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
        "Unsupported direction " + to_str(direction) + " for SokobanTessellation!"
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
      return rv.is_push_or_pull() ? Characters::L : Characters::l;
    case Direction::UP:
      return rv.is_push_or_pull() ? Characters::U : Characters::u;
    case Direction::RIGHT:
      return rv.is_push_or_pull() ? Characters::R : Characters::r;
    case Direction::DOWN:
      return rv.is_push_or_pull() ? Characters::D : Characters::d;
    default:
      throw invalid_argument(
        "Illegal PusherStep direction " + to_str(rv.direction())
        + " in SokobanTessellation!"

      );
  }
}

PusherStep SokobanTessellation::char_to_pusher_step(char rv) const {
  switch (rv) {
    case Characters::l:
      return PusherStep(Direction::LEFT, Config::NO_ID);
    case Characters::L:
      return PusherStep(Direction::LEFT, Config::DEFAULT_ID);
    case Characters::u:
      return PusherStep(Direction::UP, Config::NO_ID);
    case Characters::U:
      return PusherStep(Direction::UP, Config::DEFAULT_ID);
    case Characters::r:
      return PusherStep(Direction::RIGHT, Config::NO_ID);
    case Characters::R:
      return PusherStep(Direction::RIGHT, Config::DEFAULT_ID);
    case Characters::d:
      return PusherStep(Direction::DOWN, Config::NO_ID);
    case Characters::D:
      return PusherStep(Direction::DOWN, Config::DEFAULT_ID);
    default:
      throw invalid_argument(
        string("Illegal PusherStep character '") + rv + "' in SokobanTessellation!"
      );
  }
}

} // namespace implementation
} // namespace sokoengine
