#include "octoban_tessellation.hpp"
#include "atomic_move.hpp"
#include "board_cell.hpp"
#include "direction.hpp"

using namespace std;

namespace sokoengine {

using namespace implementation;

const Directions &OctobanTessellation::legal_directions() const {
  static const Directions retv = {Direction::LEFT,       Direction::RIGHT,
                                  Direction::UP,         Direction::DOWN,
                                  Direction::NORTH_EAST, Direction::NORTH_WEST,
                                  Direction::SOUTH_EAST, Direction::SOUTH_WEST};
  return retv;
}

position_t OctobanTessellation::neighbor_position(position_t position,
                                                  const Direction &direction,
                                                  board_size_t board_width,
                                                  board_size_t board_height) const {
  position_t row = Y(position, board_width), column = X(position, board_width);

  if (cell_orientation(position, board_width, board_height) !=
        CellOrientation::OCTAGON &&
      (direction == Direction::NORTH_EAST || direction == Direction::NORTH_WEST ||
       direction == Direction::SOUTH_EAST || direction == Direction::SOUTH_WEST)) {
    return MAX_POS + 1;
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
  if (ON_BOARD(column, row, board_width, board_height))
    return index_1d(column, row, board_width);
  else
    return MAX_POS + 1;
}

AtomicMove OctobanTessellation::char_to_atomic_move(char rv) const {
  switch (rv) {
  case AtomicMove::l:
    return AtomicMove(Direction::LEFT, false);
  case AtomicMove::L:
    return AtomicMove(Direction::LEFT, true);

  case AtomicMove::u:
    return AtomicMove(Direction::UP, false);
  case AtomicMove::U:
    return AtomicMove(Direction::UP, true);

  case AtomicMove::r:
    return AtomicMove(Direction::RIGHT, false);
  case AtomicMove::R:
    return AtomicMove(Direction::RIGHT, true);

  case AtomicMove::d:
    return AtomicMove(Direction::DOWN, false);
  case AtomicMove::D:
    return AtomicMove(Direction::DOWN, true);

  case AtomicMove::w:
    return AtomicMove(Direction::NORTH_WEST, false);
  case AtomicMove::W:
    return AtomicMove(Direction::NORTH_WEST, true);

  case AtomicMove::e:
    return AtomicMove(Direction::SOUTH_EAST, false);
  case AtomicMove::E:
    return AtomicMove(Direction::SOUTH_EAST, true);

  case AtomicMove::n:
    return AtomicMove(Direction::NORTH_EAST, false);
  case AtomicMove::N:
    return AtomicMove(Direction::NORTH_EAST, true);

  case AtomicMove::s:
    return AtomicMove(Direction::SOUTH_WEST, false);
  case AtomicMove::S:
    return AtomicMove(Direction::SOUTH_WEST, true);

  default:
    throw invalid_argument("Illegal AtomicMove direction in SokobanTessellation!");
  }
}

char OctobanTessellation::atomic_move_to_char(const AtomicMove &rv) const {
  switch (rv.direction()) {
  case Direction::LEFT:
    return rv.is_push_or_pull() ? AtomicMove::L : AtomicMove::l;
  case Direction::UP:
    return rv.is_push_or_pull() ? AtomicMove::U : AtomicMove::u;
  case Direction::RIGHT:
    return rv.is_push_or_pull() ? AtomicMove::R : AtomicMove::r;
  case Direction::DOWN:
    return rv.is_push_or_pull() ? AtomicMove::D : AtomicMove::d;
  case Direction::NORTH_WEST:
    return rv.is_push_or_pull() ? AtomicMove::W : AtomicMove::w;
  case Direction::SOUTH_EAST:
    return rv.is_push_or_pull() ? AtomicMove::E : AtomicMove::e;
  case Direction::NORTH_EAST:
    return rv.is_push_or_pull() ? AtomicMove::N : AtomicMove::n;
  case Direction::SOUTH_WEST:
    return rv.is_push_or_pull() ? AtomicMove::S : AtomicMove::s;
  default:
    throw invalid_argument("Illegal AtomicMove direction in OctobanTessellation!");
  }
}

CellOrientation OctobanTessellation::cell_orientation(position_t pos,
                                                      board_size_t board_width,
                                                      board_size_t board_height) const {
  position_t column = COLUMN(pos, board_width);
  position_t row = ROW(pos, board_width);
  return ((column + (row % 2)) % 2 == 0) ? CellOrientation::OCTAGON
                                         : CellOrientation::DEFAULT;
}

string OctobanTessellation::repr() const { return "OctobanTessellation()"; }
string OctobanTessellation::str() const { return "octoban"; }

} // namespace sokoengine
