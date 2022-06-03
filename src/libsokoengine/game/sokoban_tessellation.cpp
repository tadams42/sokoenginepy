#include "sokoban_tessellation.hpp"
#include "atomic_move.hpp"
#include "board_cell.hpp"
#include "direction.hpp"
#include "snapshot.hpp"

#include <map>
#include <memory>

using namespace std;

namespace sokoengine {
namespace game {

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
    return rv.is_push_or_pull() ? io::Snapshot::L : io::Snapshot::l;
  case Direction::UP:
    return rv.is_push_or_pull() ? io::Snapshot::U : io::Snapshot::u;
  case Direction::RIGHT:
    return rv.is_push_or_pull() ? io::Snapshot::R : io::Snapshot::r;
  case Direction::DOWN:
    return rv.is_push_or_pull() ? io::Snapshot::D : io::Snapshot::d;
  default:
    throw invalid_argument("Illegal AtomicMove character in SokobanTessellation!");
  }
}

AtomicMove SokobanTessellation::char_to_atomic_move(char rv) const {
  switch (rv) {
  case io::Snapshot::l:
    return AtomicMove(Direction::LEFT, false);
  case io::Snapshot::L:
    return AtomicMove(Direction::LEFT, true);
  case io::Snapshot::u:
    return AtomicMove(Direction::UP, false);
  case io::Snapshot::U:
    return AtomicMove(Direction::UP, true);
  case io::Snapshot::r:
    return AtomicMove(Direction::RIGHT, false);
  case io::Snapshot::R:
    return AtomicMove(Direction::RIGHT, true);
  case io::Snapshot::d:
    return AtomicMove(Direction::DOWN, false);
  case io::Snapshot::D:
    return AtomicMove(Direction::DOWN, true);
  default:
    throw invalid_argument("Illegal AtomicMove direction in SokobanTessellation!");
  }
}

string SokobanTessellation::repr() const { return "SokobanTessellation()"; }
string SokobanTessellation::str() const { return "sokoban"; }

} // namespace game
} // namespace sokoengine
