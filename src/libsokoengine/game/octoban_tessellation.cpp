#include "octoban_tessellation.hpp"

#include "pusher_step.hpp"
#include "snapshot.hpp"

using sokoengine::io::CellOrientation;
using std::invalid_argument;
using std::string;

namespace sokoengine {
namespace game {

const Directions &OctobanTessellation::legal_directions() const {
  static const Directions retv = {
    Direction::LEFT,
    Direction::RIGHT,
    Direction::UP,
    Direction::DOWN,
    Direction::NORTH_EAST,
    Direction::NORTH_WEST,
    Direction::SOUTH_EAST,
    Direction::SOUTH_WEST};
  return retv;
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
        "Unsupported direction " + implementation::direction_str(direction)
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

    case io::Snapshot::w:
      return PusherStep(Direction::NORTH_WEST, Config::NO_ID);
    case io::Snapshot::W:
      return PusherStep(Direction::NORTH_WEST, Config::DEFAULT_ID);

    case io::Snapshot::e:
      return PusherStep(Direction::SOUTH_EAST, Config::NO_ID);
    case io::Snapshot::E:
      return PusherStep(Direction::SOUTH_EAST, Config::DEFAULT_ID);

    case io::Snapshot::n:
      return PusherStep(Direction::NORTH_EAST, Config::NO_ID);
    case io::Snapshot::N:
      return PusherStep(Direction::NORTH_EAST, Config::DEFAULT_ID);

    case io::Snapshot::s:
      return PusherStep(Direction::SOUTH_WEST, Config::NO_ID);
    case io::Snapshot::S:
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
      throw invalid_argument(
        "Illegal PusherStep direction " + implementation::direction_str(rv.direction())
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

} // namespace game
} // namespace sokoengine
