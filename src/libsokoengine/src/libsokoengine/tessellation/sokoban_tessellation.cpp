#include "sokoban_tessellation.hpp"
#include "board_cell.hpp"
#include "direction.hpp"
#include "atomic_move.hpp"

#include <memory>
#include <map>

using namespace std;

namespace sokoengine {

using namespace implementation;

const Directions& SokobanTessellation::legal_directions() const {
  static const Directions retv = {
    Direction::LEFT, Direction::RIGHT, Direction::UP, Direction::DOWN
  };
  return retv;
}

position_t SokobanTessellation::neighbor_position (
  position_t position, const Direction& direction, size_t board_width,
  size_t board_height
) const {
  static const map<Direction, pair<char, char> > position_calc = {
    {Direction::LEFT,  make_pair( 0, -1)},
    {Direction::RIGHT, make_pair( 0,  1)},
    {Direction::UP,    make_pair(-1,  0)},
    {Direction::DOWN,  make_pair( 1,  0)}
  };
  if (ON_BOARD(position, board_width, board_height)) {
    position_t row = Y(position, board_width), column = X(position, board_width);
    const pair<int,int>& shift = find_in_map_or_throw<UnknownDirectionError>(
      position_calc, direction,
      "Unsupported Direction received in SokobanTessellation neighbor_position!"
    );
    row += shift.first;
    column += shift.second;
    if (ON_BOARD(column, row, board_width, board_height))
      return index_1d(column, row, board_width);
  }
  return NULL_POSITION;
}

char SokobanTessellation::atomic_move_to_char(const AtomicMove& rv) const {
  static const map< pair<Direction, bool>, AtomicMove::Characters > moves = {
    { make_pair(Direction::LEFT, true), AtomicMove::L},
    { make_pair(Direction::LEFT, false), AtomicMove::l},
    { make_pair(Direction::RIGHT, true), AtomicMove::R},
    { make_pair(Direction::RIGHT, false), AtomicMove::r},
    { make_pair(Direction::UP, true), AtomicMove::U},
    { make_pair(Direction::UP, false), AtomicMove::u},
    { make_pair(Direction::DOWN, true), AtomicMove::D},
    { make_pair(Direction::DOWN, false), AtomicMove::d}
  };
  return find_in_map_or_throw<UnknownDirectionError>(
    moves, make_pair(rv.direction(), rv.is_push_or_pull()),
      "Illegal AtomicMove character in SokobanTessellation!"
  );
}

AtomicMove SokobanTessellation::char_to_atomic_move(char rv) const {
  static const map<char, AtomicMove> moves = {
    { AtomicMove::l, AtomicMove(Direction::LEFT, false) },
    { AtomicMove::L, AtomicMove(Direction::LEFT, true) },
    { AtomicMove::r, AtomicMove(Direction::RIGHT, false) },
    { AtomicMove::R, AtomicMove(Direction::RIGHT, true) },
    { AtomicMove::u, AtomicMove(Direction::UP, false) },
    { AtomicMove::U, AtomicMove(Direction::UP, true) },
    { AtomicMove::d, AtomicMove(Direction::DOWN, false) },
    { AtomicMove::D, AtomicMove(Direction::DOWN, true) }
  };
  return find_in_map_or_throw<UnknownDirectionError>(
    moves, rv, "Illegal AtomicMove direction in SokobanTessellation!"
  );
}

string SokobanTessellation::repr() const { return "SokobanTessellation()"; }
string SokobanTessellation::str() const { return "sokoban"; }

} // namespace sokoengine
