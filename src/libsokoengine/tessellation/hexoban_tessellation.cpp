#include "hexoban_tessellation.hpp"
#include "atomic_move.hpp"
#include "board_cell.hpp"
#include "direction.hpp"
#include "hexoban_board.hpp"

using namespace std;

namespace sokoengine {

using namespace implementation;

const Directions &HexobanTessellation::legal_directions() const {
  static const Directions retv = {Direction::LEFT,       Direction::RIGHT,
                                  Direction::NORTH_EAST, Direction::NORTH_WEST,
                                  Direction::SOUTH_EAST, Direction::SOUTH_WEST};
  return retv;
}

position_t HexobanTessellation::neighbor_position(position_t position,
                                                  const Direction &direction,
                                                  board_size_t board_width,
                                                  board_size_t board_height) const {
  position_t row = Y(position, board_width), column = X(position, board_width);
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

  if (ON_BOARD(column, row, board_width, board_height))
    return index_1d(column, row, board_width);
  else
    return MAX_POS + 1;
}

AtomicMove HexobanTessellation::char_to_atomic_move(char rv) const {
  switch (rv) {
  case AtomicMove::l:
    return AtomicMove(Direction::LEFT, false);
  case AtomicMove::L:
    return AtomicMove(Direction::LEFT, true);

  case AtomicMove::r:
    return AtomicMove(Direction::RIGHT, false);
  case AtomicMove::R:
    return AtomicMove(Direction::RIGHT, true);

  case AtomicMove::u:
    return AtomicMove(Direction::NORTH_WEST, false);
  case AtomicMove::U:
    return AtomicMove(Direction::NORTH_WEST, true);

  case AtomicMove::d:
    return AtomicMove(Direction::SOUTH_EAST, false);
  case AtomicMove::D:
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
    throw invalid_argument("Illegal AtomicMove character in HexobanTessellation!");
  }
}

char HexobanTessellation::atomic_move_to_char(const AtomicMove &rv) const {
  switch (rv.direction()) {
  case Direction::LEFT:
    return rv.is_push_or_pull() ? AtomicMove::L : AtomicMove::l;
  case Direction::RIGHT:
    return rv.is_push_or_pull() ? AtomicMove::R : AtomicMove::r;
  case Direction::NORTH_WEST:
    return rv.is_push_or_pull() ? AtomicMove::U : AtomicMove::u;
  case Direction::SOUTH_EAST:
    return rv.is_push_or_pull() ? AtomicMove::D : AtomicMove::d;
  case Direction::NORTH_EAST:
    return rv.is_push_or_pull() ? AtomicMove::N : AtomicMove::n;
  case Direction::SOUTH_WEST:
    return rv.is_push_or_pull() ? AtomicMove::S : AtomicMove::s;
  default:
    throw invalid_argument("Illegal AtomicMove direction in HexobanTessellation!");
  }
}

string HexobanTessellation::repr() const { return "HexobanTessellation()"; }
string HexobanTessellation::str() const { return "hexoban"; }

const VariantBoardResizer &HexobanTessellation::resizer() const {
  static const HexobanBoardResizer retv = HexobanBoardResizer();
  return retv;
}

const VariantBoardPrinter &HexobanTessellation::printer() const {
  static const HexobanBoardPrinter retv = HexobanBoardPrinter();
  return retv;
}

const VariantBoardParser &HexobanTessellation::parser() const {
  static const HexobanBoardParser retv = HexobanBoardParser();
  return retv;
}

} // namespace sokoengine
