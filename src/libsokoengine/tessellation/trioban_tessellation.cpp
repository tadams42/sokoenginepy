#include "trioban_tessellation.hpp"
#include "atomic_move.hpp"
#include "board_cell.hpp"
#include "direction.hpp"

using namespace std;

namespace sokoengine {

using namespace implementation;

const Directions &TriobanTessellation::legal_directions() const {
  static const Directions retv{Direction::LEFT,       Direction::RIGHT,
                               Direction::NORTH_EAST, Direction::NORTH_WEST,
                               Direction::SOUTH_EAST, Direction::SOUTH_WEST};
  return retv;
}

position_t TriobanTessellation::neighbor_position(position_t position,
                                                  const Direction &direction,
                                                  board_size_t board_width,
                                                  board_size_t board_height) const {
  if (!ON_BOARD(position, board_width, board_height)) return MAX_POS + 1;
  position_t row = Y(position, board_width), column = X(position, board_width);
  int8_t dy, dx;
  bool tpd = cell_orientation(position, board_width, board_height) ==
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
  if (ON_BOARD(column, row, board_width, board_height))
    return index_1d(column, row, board_width);
  else
    return MAX_POS + 1;
}

AtomicMove TriobanTessellation::char_to_atomic_move(char rv) const {
  switch (rv) {
  case AtomicMove::l:
    return AtomicMove(Direction::LEFT, false);
  case AtomicMove::L:
    return AtomicMove(Direction::LEFT, true);

  case AtomicMove::r:
    return AtomicMove(Direction::RIGHT, false);
  case AtomicMove::R:
    return AtomicMove(Direction::RIGHT, true);

  case AtomicMove::n:
    return AtomicMove(Direction::NORTH_EAST, false);
  case AtomicMove::N:
    return AtomicMove(Direction::NORTH_EAST, true);

  case AtomicMove::u:
    return AtomicMove(Direction::NORTH_WEST, false);
  case AtomicMove::U:
    return AtomicMove(Direction::NORTH_WEST, true);

  case AtomicMove::d:
    return AtomicMove(Direction::SOUTH_EAST, false);
  case AtomicMove::D:
    return AtomicMove(Direction::SOUTH_EAST, true);

  case AtomicMove::s:
    return AtomicMove(Direction::SOUTH_WEST, false);
  case AtomicMove::S:
    return AtomicMove(Direction::SOUTH_WEST, true);

  default:
    throw invalid_argument("Illegal AtomicMove character in TriobanTessellation!");
  }
}

char TriobanTessellation::atomic_move_to_char(const AtomicMove &rv) const {
  switch (rv.direction()) {
  case Direction::LEFT:
    return rv.is_push_or_pull() ? AtomicMove::L : AtomicMove::l;
  case Direction::RIGHT:
    return rv.is_push_or_pull() ? AtomicMove::R : AtomicMove::r;
  case Direction::NORTH_EAST:
    return rv.is_push_or_pull() ? AtomicMove::N : AtomicMove::n;
  case Direction::NORTH_WEST:
    return rv.is_push_or_pull() ? AtomicMove::U : AtomicMove::u;
  case Direction::SOUTH_EAST:
    return rv.is_push_or_pull() ? AtomicMove::D : AtomicMove::d;
  case Direction::SOUTH_WEST:
    return rv.is_push_or_pull() ? AtomicMove::S : AtomicMove::s;
  default:
    throw invalid_argument("Illegal AtomicMove direction in TriobanTessellation!");
  }
}

CellOrientation TriobanTessellation::cell_orientation(position_t pos,
                                                      board_size_t board_width,
                                                      board_size_t board_height) const {
  position_t column = COLUMN(pos, board_width);
  position_t row = ROW(pos, board_width);
  return (column + (row % 2)) % 2 == 0 ? CellOrientation::TRIANGLE_DOWN
                                       : CellOrientation::DEFAULT;
}

GraphType TriobanTessellation::graph_type() const { return GraphType::DIRECTED_MULTI; }

string TriobanTessellation::repr() const { return "TriobanTessellation()"; }
string TriobanTessellation::str() const { return "trioban"; }

} // namespace sokoengine
