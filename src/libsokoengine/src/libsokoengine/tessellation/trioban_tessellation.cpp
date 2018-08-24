#include "trioban_tessellation.hpp"
#include "board_cell.hpp"
#include "direction.hpp"
#include "atomic_move.hpp"

#include <memory>
#include <map>

using namespace std;

namespace sokoengine {

using namespace implementation;

const Directions& TriobanTessellation::legal_directions() const {
  static const Directions retv {
    Direction::LEFT, Direction::RIGHT, Direction::NORTH_EAST,
    Direction::NORTH_WEST, Direction::SOUTH_EAST, Direction::SOUTH_WEST
  };
  return retv;
}

position_t TriobanTessellation::neighbor_position (
  position_t position, const Direction& direction, size_t board_width,
  size_t board_height
) const {
  if (!ON_BOARD(position, board_width, board_height))
    return NULL_POSITION;
  position_t row = Y(position, board_width), column = X(position, board_width);
  char dy, dx;
  bool tpd = cell_orientation(
    position, board_width, board_height
  ) == CellOrientation::TRIANGLE_DOWN;

  if (direction == Direction::LEFT) {
    dy = 0;
    dx = -1;
  }
  else if (direction == Direction::RIGHT) {
    dy = 0;
    dx = 1;
  }
  else if (direction == Direction::NORTH_EAST) {
    if (tpd) {
      dy = -1;
      dx = 0;
    } else {
      dy = 0;
      dx = 1;
    }
  }
  else if (direction == Direction::NORTH_WEST) {
    if (tpd) {
      dy = -1;
      dx = 0;
    } else {
      dy = 0;
      dx = -1;
    }
  }
  else if (direction == Direction::SOUTH_EAST) {
    if (tpd) {
      dy = 0;
      dx = 1;
    } else {
      dy = 1;
      dx = 0;
    }
  }
  else if (direction == Direction::SOUTH_WEST) {
    if (tpd) {
      dy = 0;
      dx = -1;
    } else {
      dy = 1;
      dx = 0;
    }
  }
  else throw UnknownDirectionError(
    "Unsupported Direction received in TriobanTessellation neighbor_position!"
  );

  row += dy;
  column += dx;
  if (ON_BOARD(column, row, board_width, board_height)) {
    return index_1d(column, row, board_width);
  }
  return NULL_POSITION;
}

AtomicMove TriobanTessellation::char_to_atomic_move(char rv) const {
  static const map<char, AtomicMove> moves {
    { AtomicMove::l, AtomicMove(Direction::LEFT, false) },
    { AtomicMove::L, AtomicMove(Direction::LEFT, true) },
    { AtomicMove::r, AtomicMove(Direction::RIGHT, false) },
    { AtomicMove::R, AtomicMove(Direction::RIGHT, true) },
    { AtomicMove::n, AtomicMove(Direction::NORTH_EAST, false) },
    { AtomicMove::N, AtomicMove(Direction::NORTH_EAST, true) },
    { AtomicMove::u, AtomicMove(Direction::NORTH_WEST, false) },
    { AtomicMove::U, AtomicMove(Direction::NORTH_WEST, true) },
    { AtomicMove::d, AtomicMove(Direction::SOUTH_EAST, false) },
    { AtomicMove::D, AtomicMove(Direction::SOUTH_EAST, true) },
    { AtomicMove::s, AtomicMove(Direction::SOUTH_WEST, false) },
    { AtomicMove::S, AtomicMove(Direction::SOUTH_WEST, true) }
  };
  return find_in_map_or_throw<UnknownDirectionError>(
    moves, rv, "Illegal AtomicMove character in TriobanTessellation!"
  );
}

char TriobanTessellation::atomic_move_to_char(const AtomicMove& rv) const {
  static const map< pair<Direction, bool>, AtomicMove::Characters > moves {
    { make_pair(Direction::LEFT, false), AtomicMove::l },
    { make_pair(Direction::LEFT, true), AtomicMove::L },
    { make_pair(Direction::RIGHT, false), AtomicMove::r },
    { make_pair(Direction::RIGHT, true), AtomicMove::R },
    { make_pair(Direction::NORTH_EAST, false), AtomicMove::n},
    { make_pair(Direction::NORTH_EAST, true), AtomicMove::N},
    { make_pair(Direction::NORTH_WEST, false), AtomicMove::u},
    { make_pair(Direction::NORTH_WEST, true), AtomicMove::U},
    { make_pair(Direction::SOUTH_EAST, false), AtomicMove::d},
    { make_pair(Direction::SOUTH_EAST, true), AtomicMove::D},
    { make_pair(Direction::SOUTH_WEST, false), AtomicMove::s},
    { make_pair(Direction::SOUTH_WEST, true), AtomicMove::S}
  };
  return find_in_map_or_throw<UnknownDirectionError>(
    moves, make_pair(rv.direction(), rv.is_push_or_pull()),
    "Illegal AtomicMove direction in TriobanTessellation!"
  );
}

CellOrientation TriobanTessellation::cell_orientation(position_t pos, size_t board_width, size_t board_height) const {
  position_t column = COLUMN(pos, board_width);
  position_t row = ROW(pos, board_width);
  return (column + (row % 2) ) % 2 == 0 ? CellOrientation::TRIANGLE_DOWN : CellOrientation::DEFAULT;
}

GraphType TriobanTessellation::graph_type() const {
  return GraphType::DIRECTED_MULTI;
}

string TriobanTessellation::repr() const { return "TriobanTessellation()"; }
string TriobanTessellation::str() const { return "trioban"; }

} // namespace sokoengine
