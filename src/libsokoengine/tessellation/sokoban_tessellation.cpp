#include "sokoban_tessellation.hpp"
#include "atomic_move.hpp"
#include "board_cell.hpp"
#include "direction.hpp"

#include <map>
#include <memory>

using namespace std;

namespace sokoengine {

using namespace implementation;

const Directions &SokobanTessellation::legal_directions() const {
  static const Directions retv = {Direction::LEFT, Direction::RIGHT, Direction::UP,
                                  Direction::DOWN};
  return retv;
}

position_t SokobanTessellation::neighbor_position(position_t position,
                                                  const Direction &direction,
                                                  board_size_t board_width,
                                                  board_size_t board_height) const {
  position_t row = Y(position, board_width), column = X(position, board_width);
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

  if (ON_BOARD(column, row, board_width, board_height))
    return index_1d(column, row, board_width);
  else
    return MAX_POS + 1;
}

char SokobanTessellation::atomic_move_to_char(const AtomicMove &rv) const {
  switch (rv.direction()) {
  case Direction::LEFT:
    return rv.is_push_or_pull() ? AtomicMove::L : AtomicMove::l;
  case Direction::UP:
    return rv.is_push_or_pull() ? AtomicMove::U : AtomicMove::u;
  case Direction::RIGHT:
    return rv.is_push_or_pull() ? AtomicMove::R : AtomicMove::r;
  case Direction::DOWN:
    return rv.is_push_or_pull() ? AtomicMove::D : AtomicMove::d;
  default:
    throw invalid_argument("Illegal AtomicMove character in SokobanTessellation!");
  }
}

AtomicMove SokobanTessellation::char_to_atomic_move(char rv) const {
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
  default:
    throw invalid_argument("Illegal AtomicMove direction in SokobanTessellation!");
  }
}

string SokobanTessellation::repr() const { return "SokobanTessellation()"; }
string SokobanTessellation::str() const { return "sokoban"; }

} // namespace sokoengine
