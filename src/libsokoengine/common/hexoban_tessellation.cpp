/// @file
#include "hexoban_tessellation.hpp"

#include "characters.hpp"
#include "pusher_step.hpp"

using std::invalid_argument;
using std::string;

namespace sokoengine {
namespace implementation {

static const Directions HEX_LEGAL_DIRECTIONS = {
  Direction::LEFT,
  Direction::RIGHT,
  Direction::NORTH_EAST,
  Direction::NORTH_WEST,
  Direction::SOUTH_EAST,
  Direction::SOUTH_WEST};

const Directions &HexobanTessellation::legal_directions() const {
  return HEX_LEGAL_DIRECTIONS;
}

position_t HexobanTessellation::neighbor_position(
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
        "Unsupported direction " + to_str(direction) + " for HexobanTessellation!"
      );
  }

  if (is_on_board_2d(column, row, width, height))
    return index_1d(column, row, width);
  else
    return Config::NO_POS;
}

PusherStep HexobanTessellation::char_to_pusher_step(char rv) const {
  switch (rv) {
    case Characters::l:
      return PusherStep(Direction::LEFT, Config::NO_ID);
    case Characters::L:
      return PusherStep(Direction::LEFT, Config::DEFAULT_ID);

    case Characters::r:
      return PusherStep(Direction::RIGHT, Config::NO_ID);
    case Characters::R:
      return PusherStep(Direction::RIGHT, Config::DEFAULT_ID);

    case Characters::u:
      return PusherStep(Direction::NORTH_WEST, Config::NO_ID);
    case Characters::U:
      return PusherStep(Direction::NORTH_WEST, Config::DEFAULT_ID);

    case Characters::d:
      return PusherStep(Direction::SOUTH_EAST, Config::NO_ID);
    case Characters::D:
      return PusherStep(Direction::SOUTH_EAST, Config::DEFAULT_ID);

    case Characters::n:
      return PusherStep(Direction::NORTH_EAST, Config::NO_ID);
    case Characters::N:
      return PusherStep(Direction::NORTH_EAST, Config::DEFAULT_ID);

    case Characters::s:
      return PusherStep(Direction::SOUTH_WEST, Config::NO_ID);
    case Characters::S:
      return PusherStep(Direction::SOUTH_WEST, Config::DEFAULT_ID);

    default:
      throw invalid_argument(
        string("Illegal PusherStep character '") + rv + "' in HexobanTessellation!"
      );
  }
}

char HexobanTessellation::pusher_step_to_char(const PusherStep &rv) const {
  switch (rv.direction()) {
    case Direction::LEFT:
      return rv.is_push_or_pull() ? Characters::L : Characters::l;
    case Direction::RIGHT:
      return rv.is_push_or_pull() ? Characters::R : Characters::r;
    case Direction::NORTH_WEST:
      return rv.is_push_or_pull() ? Characters::U : Characters::u;
    case Direction::SOUTH_EAST:
      return rv.is_push_or_pull() ? Characters::D : Characters::d;
    case Direction::NORTH_EAST:
      return rv.is_push_or_pull() ? Characters::N : Characters::n;
    case Direction::SOUTH_WEST:
      return rv.is_push_or_pull() ? Characters::S : Characters::s;
    default:
      throw invalid_argument(
        "Illegal PusherStep direction " + to_str(rv.direction())
        + " in HexobanTessellation!"
      );
  }
}

} // namespace implementation
} // namespace sokoengine
