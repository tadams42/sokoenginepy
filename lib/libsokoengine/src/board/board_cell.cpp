#include "board_cell.hpp"

using namespace std;

namespace sokoengine {

BoardConversionError::BoardConversionError(const string& mess):
  runtime_error(mess)
{}

BoardConversionError::~BoardConversionError() = default;

IllegalBoardCharacterError::IllegalBoardCharacterError(const string& mess):
  invalid_argument(mess)
{}

IllegalBoardCharacterError::~IllegalBoardCharacterError() = default;

BoardCell::BoardCell(char rv, bool is_in_playable_area, bool is_deadlock) :
  m_box(false), m_pusher(false), m_goal(false), m_wall(false),
  m_playable(is_in_playable_area), m_deadlock(is_deadlock)
{
  // of the board space consists of empty floors, thus a chance this
  // test succeeds is larger than for other cases. This means that
  // branches will not be executed most of the time, which means
  // method runs faster
  if (!is_empty_floor_chr(rv)) {
    if (is_wall_chr(rv)) {
      set_is_wall(true);
    } else if (is_pusher_chr(rv)) {
      set_has_pusher(true);
      if (is_goal_chr(rv)) set_has_goal(true);
    } else if (is_box_chr(rv)) {
      set_has_box(true);
      if (is_goal_chr(rv)) set_has_goal(true);
    } else if (is_goal_chr(rv)) {
      set_has_goal(true);
    } else {
      throw IllegalBoardCharacterError(
        "Invalid character in BoardCell constructor!"
      );
    }
  }
}

char BoardCell::to_str(bool use_visible_floor) const {
  char retv;
  if (!has_piece()) {
    if (is_wall()) {
      retv = WALL;
    } else {
      retv = use_visible_floor ? VISIBLE_FLOOR : FLOOR;
    }
  } else if (!has_box() && !has_goal() && has_pusher())
    retv = PUSHER;
  else if (!has_box() && has_goal() && !has_pusher())
    retv = GOAL;
  else if (!has_box() && has_goal() && has_pusher())
    retv = PUSHER_ON_GOAL;
  else if (has_box() && !has_goal() && !has_pusher())
    retv = BOX;
  else // if (has_box() && has_goal() && !has_pusher())
    retv = BOX_ON_GOAL;

  return retv;
}

char BoardCell::str() const { return to_str(false); }

string BoardCell::repr() const {
  return string("BoardCell('") + str() + "')";
}

} // namespace sokoengine
