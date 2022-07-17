/// @file
#include "octoban_tessellation.hpp"

#include "characters.hpp"
#include "pusher_step.hpp"

using std::invalid_argument;
using std::string;

namespace sokoengine {
namespace implementation {

static const Directions OCT_LEGAL_DIRECTIONS = {
  Direction::LEFT,
  Direction::RIGHT,
  Direction::UP,
  Direction::DOWN,
  Direction::NORTH_EAST,
  Direction::NORTH_WEST,
  Direction::SOUTH_EAST,
  Direction::SOUTH_WEST};

const Directions &OctobanTessellation::legal_directions() const {
  return OCT_LEGAL_DIRECTIONS;
}

position_t OctobanTessellation::neighbor_position(
  position_t       position,
  const Direction &direction,
  board_size_t     width,
  board_size_t     height
) const {
  position_t row = index_y(position, width), column = index_x(position, width);

  // clang-format off
  if (
    cell_orientation(position, width, height) != CellOrientation::OCTAGON
    && (
      direction == Direction::NORTH_EAST
      || direction == Direction::NORTH_WEST
      || direction == Direction::SOUTH_EAST
      || direction == Direction::SOUTH_WEST
    )
  ) {
    return Config::NO_POS;
  }
  // clang-format off

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
        "Unsupported direction " + implementation::to_str(direction)
        + " for OctobanTessellation!"
      );
  }
  if (is_on_board_2d(column, row, width, height))
    return index_1d(column, row, width);
  else
    return Config::NO_POS;
}

PusherStep OctobanTessellation::char_to_pusher_step(char rv) const {
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

    case Characters::w:
      return PusherStep(Direction::NORTH_WEST, Config::NO_ID);
    case Characters::W:
      return PusherStep(Direction::NORTH_WEST, Config::DEFAULT_ID);

    case Characters::e:
      return PusherStep(Direction::SOUTH_EAST, Config::NO_ID);
    case Characters::E:
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
        string("Illegal PusherStep character '") + rv + "' in OctobanTessellation!"
      );
  }
}

char OctobanTessellation::pusher_step_to_char(const PusherStep &rv) const {
  switch (rv.direction()) {
    case Direction::LEFT:
      return rv.is_push_or_pull() ? Characters::L : Characters::l;
    case Direction::UP:
      return rv.is_push_or_pull() ? Characters::U : Characters::u;
    case Direction::RIGHT:
      return rv.is_push_or_pull() ? Characters::R : Characters::r;
    case Direction::DOWN:
      return rv.is_push_or_pull() ? Characters::D : Characters::d;
    case Direction::NORTH_WEST:
      return rv.is_push_or_pull() ? Characters::W : Characters::w;
    case Direction::SOUTH_EAST:
      return rv.is_push_or_pull() ? Characters::E : Characters::e;
    case Direction::NORTH_EAST:
      return rv.is_push_or_pull() ? Characters::N : Characters::n;
    case Direction::SOUTH_WEST:
      return rv.is_push_or_pull() ? Characters::S : Characters::s;
    default:
      throw invalid_argument(
        "Illegal PusherStep direction " + implementation::to_str(rv.direction())
        + " in OctobanTessellation!"
      );
  }
}

CellOrientation OctobanTessellation::cell_orientation(
  position_t pos, board_size_t width, board_size_t height
) const {
  position_t column = index_column(pos, width);
  position_t row    = index_row(pos, width);
  return ((column + (row % 2)) % 2 == 0) ? CellOrientation::OCTAGON
                                         : CellOrientation::DEFAULT;
}

} // namespace implementation
} // namespace sokoengine
