#include "hexoban_tessellation.hpp"
#include "hexoban_board.hpp"
#include "board_cell.hpp"
#include "direction.hpp"
#include "atomic_move.hpp"

#include <memory>
#include <map>

using namespace std;

namespace sokoengine {

using namespace implementation;

const Directions& HexobanTessellation::legal_directions() const {
  static const Directions retv = {
    Direction::LEFT, Direction::RIGHT,
    Direction::NORTH_EAST, Direction::NORTH_WEST,
    Direction::SOUTH_EAST, Direction::SOUTH_WEST
  };
  return retv;
}

position_t HexobanTessellation::neighbor_position(
  position_t position, const Direction& direction, size_t board_width,
  size_t board_height
) const {
  if (ON_BOARD(position, board_width, board_height)) {
    position_t row = Y(position, board_width), column = X(position, board_width);
    if (direction == Direction::LEFT) {
      column -= 1;
    } else if (direction == Direction::RIGHT) {
      column += 1;
    } else if (direction == Direction::NORTH_EAST) {
      column += row % 2;
      row -= 1;
    } else if (direction == Direction::NORTH_WEST) {
      column -= (row + 1) % 2;
      row -= 1;
    } else if (direction == Direction::SOUTH_EAST) {
      column += row % 2;
      row += 1;
    } else if (direction == Direction::SOUTH_WEST) {
      column -= (row + 1) % 2;
      row += 1;
    } else throw UnknownDirectionError(
      "Unsupported Direction received in HexobanTessellation neighbor_position!"
    );
    if (ON_BOARD(column, row, board_width, board_height)) {
      return index_1d(column, row, board_width);
    }
  }
  return NULL_POSITION;
}

AtomicMove HexobanTessellation::char_to_atomic_move(char rv) const {
  static const map<char, AtomicMove> moves = {
    { AtomicMove::l, AtomicMove(Direction::LEFT, false) },
    { AtomicMove::L, AtomicMove(Direction::LEFT, true) },
    { AtomicMove::r, AtomicMove(Direction::RIGHT, false) },
    { AtomicMove::R, AtomicMove(Direction::RIGHT, true) },
    { AtomicMove::u, AtomicMove(Direction::NORTH_WEST, false) },
    { AtomicMove::U, AtomicMove(Direction::NORTH_WEST, true) },
    { AtomicMove::d, AtomicMove(Direction::SOUTH_EAST, false) },
    { AtomicMove::D, AtomicMove(Direction::SOUTH_EAST, true) },
    { AtomicMove::n, AtomicMove(Direction::NORTH_EAST, false) },
    { AtomicMove::N, AtomicMove(Direction::NORTH_EAST, true) },
    { AtomicMove::s, AtomicMove(Direction::SOUTH_WEST, false) },
    { AtomicMove::S, AtomicMove(Direction::SOUTH_WEST, true) }
  };
  return find_in_map_or_throw<UnknownDirectionError>(
    moves, rv, "Illegal AtomicMove character in HexobanTessellation!"
  );
}

char HexobanTessellation::atomic_move_to_char(const AtomicMove& rv) const {
  static const map< pair<Direction, bool>, AtomicMove::Characters > moves = {
    { make_pair(Direction::LEFT, false), AtomicMove::l },
    { make_pair(Direction::LEFT, true), AtomicMove::L },
    { make_pair(Direction::RIGHT, false), AtomicMove::r },
    { make_pair(Direction::RIGHT, true), AtomicMove::R },
    { make_pair(Direction::NORTH_WEST, false), AtomicMove::u },
    { make_pair(Direction::NORTH_WEST, true), AtomicMove::U },
    { make_pair(Direction::SOUTH_EAST, false), AtomicMove::d },
    { make_pair(Direction::SOUTH_EAST, true), AtomicMove::D },
    { make_pair(Direction::NORTH_EAST, false), AtomicMove::n },
    { make_pair(Direction::NORTH_EAST, true), AtomicMove::N },
    { make_pair(Direction::SOUTH_WEST, false), AtomicMove::s },
    { make_pair(Direction::SOUTH_WEST, true), AtomicMove::S }
  };
  return find_in_map_or_throw<UnknownDirectionError>(
    moves, make_pair(rv.direction(), rv.is_push_or_pull()),
    "Illegal AtomicMove direction in HexobanTessellation!"
  );
}

string HexobanTessellation::repr() const { return "HexobanTessellation()"; }
string HexobanTessellation::str() const { return "hexoban"; }

const VariantBoardResizer& HexobanTessellation::resizer() const {
  static const HexobanBoardResizer retv = HexobanBoardResizer();
  return retv;
}

const VariantBoardPrinter& HexobanTessellation::printer() const {
  static const HexobanBoardPrinter retv = HexobanBoardPrinter();
  return retv;
}

const VariantBoardParser& HexobanTessellation::parser() const {
  static const HexobanBoardParser retv = HexobanBoardParser();
  return retv;
}

} // namespace sokoengine
