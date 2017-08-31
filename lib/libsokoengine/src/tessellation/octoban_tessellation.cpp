#include "octoban_tessellation.hpp"
#include "board_cell.hpp"
#include "direction.hpp"
#include "atomic_move.hpp"

#include <memory>
#include <map>

using namespace std;

namespace sokoengine {
  
using namespace implementation;

const Directions& OctobanTessellation::legal_directions() const {
  static const Directions retv = {
    Direction::LEFT, Direction::RIGHT,
    Direction::UP, Direction::DOWN,
    Direction::NORTH_EAST, Direction::NORTH_WEST,
    Direction::SOUTH_EAST, Direction::SOUTH_WEST
  };
  return retv;
}

position_t OctobanTessellation::neighbor_position(
  position_t position, const Direction& direction, size_t board_width,
  size_t board_height
) const {
  static const map<Direction, pair<char, char> > position_calc {
    {Direction::LEFT,       make_pair( 0, -1)},
    {Direction::RIGHT,      make_pair( 0, 1)},
    {Direction::UP,         make_pair(-1, 0)},
    {Direction::DOWN,       make_pair( 1, 0)},
    {Direction::NORTH_WEST, make_pair( -1, -1)},
    {Direction::NORTH_EAST, make_pair( -1, 1)},
    {Direction::SOUTH_WEST, make_pair( 1, -1)},
    {Direction::SOUTH_EAST, make_pair( 1, 1)}
  };
  if (ON_BOARD(position, board_width, board_height)) {
    position_t row = Y(position, board_width), column = X(position, board_width);
    if (cell_orientation(position, board_width, board_height) != CellOrientation::OCTAGON &&
        (direction == Direction::NORTH_EAST || direction == Direction::NORTH_WEST ||
        direction == Direction::SOUTH_EAST || direction == Direction::SOUTH_WEST) ) {
      return NULL_POSITION;
    }
    const pair<int,int>& shift = find_in_map_or_throw<UnknownDirectionError>(
      position_calc, direction,
        "Unsupported Direction received in OctobanTessellation neighbor_position!"
    );
    row += shift.first;
    column += shift.second;
    if (ON_BOARD(column, row, board_width, board_height)) {
      return index_1d(column, row, board_width);
    }
  }
  return NULL_POSITION;
}

AtomicMove OctobanTessellation::char_to_atomic_move(char rv) const {
  static const map<char, AtomicMove> moves = {
    { AtomicMove::l, AtomicMove(Direction::LEFT, false) },
    { AtomicMove::L, AtomicMove(Direction::LEFT, true) },
    { AtomicMove::r, AtomicMove(Direction::RIGHT, false) },
    { AtomicMove::R, AtomicMove(Direction::RIGHT, true) },
    { AtomicMove::u, AtomicMove(Direction::UP, false) },
    { AtomicMove::U, AtomicMove(Direction::UP, true) },
    { AtomicMove::d, AtomicMove(Direction::DOWN, false) },
    { AtomicMove::D, AtomicMove(Direction::DOWN, true) },
    { AtomicMove::w, AtomicMove(Direction::NORTH_WEST, false) },
    { AtomicMove::W, AtomicMove(Direction::NORTH_WEST, true) },
    { AtomicMove::e, AtomicMove(Direction::SOUTH_EAST, false) },
    { AtomicMove::E, AtomicMove(Direction::SOUTH_EAST, true) },
    { AtomicMove::n, AtomicMove(Direction::NORTH_EAST, false) },
    { AtomicMove::N, AtomicMove(Direction::NORTH_EAST, true) },
    { AtomicMove::s, AtomicMove(Direction::SOUTH_WEST, false) },
    { AtomicMove::S, AtomicMove(Direction::SOUTH_WEST, true) }
  };
  return find_in_map_or_throw<UnknownDirectionError>(
    moves, rv, "Illegal AtomicMove character in OctobanTessellation!"
  );
}

char OctobanTessellation::atomic_move_to_char(const AtomicMove& rv) const {
  static const map< pair<Direction, bool>, AtomicMove::Characters > moves = {
    { make_pair(Direction::LEFT, false), AtomicMove::l },
    { make_pair(Direction::LEFT, true), AtomicMove::L },
    { make_pair(Direction::RIGHT, false), AtomicMove::r },
    { make_pair(Direction::RIGHT, true), AtomicMove::R },
    { make_pair(Direction::UP, false), AtomicMove::u },
    { make_pair(Direction::UP, true), AtomicMove::U },
    { make_pair(Direction::DOWN, false), AtomicMove::d },
    { make_pair(Direction::DOWN, true), AtomicMove::D },
    { make_pair(Direction::NORTH_WEST, false), AtomicMove::w },
    { make_pair(Direction::NORTH_WEST, true), AtomicMove::W },
    { make_pair(Direction::SOUTH_EAST, false), AtomicMove::e },
    { make_pair(Direction::SOUTH_EAST, true), AtomicMove::E },
    { make_pair(Direction::NORTH_EAST, false), AtomicMove::n },
    { make_pair(Direction::NORTH_EAST, true), AtomicMove::N },
    { make_pair(Direction::SOUTH_WEST, false), AtomicMove::s },
    { make_pair(Direction::SOUTH_WEST, true), AtomicMove::S }
  };
  return find_in_map_or_throw<UnknownDirectionError>(
    moves, make_pair(rv.direction(), rv.is_push_or_pull()),
    "Illegal AtomicMove direction in OctobanTessellation!"
  );
}

CellOrientation OctobanTessellation::cell_orientation(
  position_t pos, size_t board_width, size_t board_height
) const {
  position_t column = COLUMN(pos, board_width);
  position_t row = ROW(pos, board_width);
  return ((column + (row % 2)) % 2 == 0) ?
         CellOrientation::OCTAGON :
         CellOrientation::DEFAULT;
}

string OctobanTessellation::repr() const { return "OctobanTessellation()"; }
string OctobanTessellation::str() const { return "octoban"; }

} // namespace sokoengine
