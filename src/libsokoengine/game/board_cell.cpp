/// @file
#include "board_cell.hpp"

#include "characters.hpp"

using sokoengine::implementation::Characters;
using std::invalid_argument;
using std::string;

namespace sokoengine {
namespace game {

BoardCell::BoardCell(char rv)
  : m_box(false)
  , m_pusher(false)
  , m_goal(false)
  , m_wall(false)
  , m_playable(false) {
  if (!Characters::is_empty_floor(rv)) {
    if (Characters::is_wall(rv)) {
      set_is_wall(true);
    } else if (Characters::is_pusher(rv)) {
      set_has_pusher(true);
      if (Characters::is_goal(rv))
        set_has_goal(true);
    } else if (Characters::is_box(rv)) {
      set_has_box(true);
      if (Characters::is_goal(rv))
        set_has_goal(true);
    } else if (Characters::is_goal(rv)) {
      set_has_goal(true);
    } else {
      throw invalid_argument(string("Illegal character '") + rv + "' for BoardCell!");
    }
  }
}

bool BoardCell::operator==(const BoardCell &rv) const {
  return m_wall == rv.m_wall && m_pusher == rv.m_pusher && m_box == rv.m_box
      && m_goal == rv.m_goal;
}

bool BoardCell::operator!=(const BoardCell &rv) const { return !(*this == rv); }

bool BoardCell::operator==(char rv) const {
  return m_wall == Characters::is_wall(rv) && m_pusher == Characters::is_pusher(rv)
      && m_box == Characters::is_box(rv) && m_goal == Characters::is_goal(rv);
}

bool BoardCell::operator!=(char rv) const { return !(*this == rv); }

char BoardCell::to_str(bool use_visible_floor) const {
  char retv;
  if (!has_piece()) {
    if (is_wall()) {
      retv = Characters::WALL;
    } else {
      retv = use_visible_floor ? Characters::VISIBLE_FLOOR : Characters::FLOOR;
    }
  } else if (!has_box() && !has_goal() && has_pusher())
    retv = Characters::PUSHER;
  else if (!has_box() && has_goal() && !has_pusher())
    retv = Characters::GOAL;
  else if (!has_box() && has_goal() && has_pusher())
    retv = Characters::PUSHER_ON_GOAL;
  else if (has_box() && !has_goal() && !has_pusher())
    retv = Characters::BOX;
  else // if (has_box() && has_goal() && !has_pusher())
    retv = Characters::BOX_ON_GOAL;

  return retv;
}

char BoardCell::str() const { return to_str(false); }

string BoardCell::repr() const { return string("BoardCell('") + str() + "')"; }

void BoardCell::clear() { m_wall = m_goal = m_pusher = m_box = false; }

bool BoardCell::has_piece() const { return m_goal || m_box || m_pusher; }

bool BoardCell::is_empty_floor() const {
  return !(m_wall || m_pusher || m_box || m_goal);
}

bool BoardCell::is_border_element() const { return m_wall || (m_box && m_goal); }

bool BoardCell::can_put_pusher_or_box() const { return !(m_box || m_pusher || m_wall); }

bool BoardCell::has_box() const { return m_box; }

void BoardCell::set_has_box(bool rv) {
  if (rv == true) {
    m_box    = true;
    m_wall   = false;
    m_pusher = false;
  } else {
    m_box = false;
  }
}

void BoardCell::put_box() { set_has_box(true); }

void BoardCell::remove_box() { set_has_box(false); }

bool BoardCell::has_goal() const { return m_goal; }

void BoardCell::set_has_goal(bool rv) {
  if (rv == true) {
    m_goal = true;
    m_wall = false;
  } else {
    m_goal = false;
  }
}

void BoardCell::put_goal() { set_has_goal(true); }

void BoardCell::remove_goal() { set_has_goal(false); }

bool BoardCell::has_pusher() const { return m_pusher; }

void BoardCell::set_has_pusher(bool rv) {
  if (rv == true) {
    m_pusher = true;
    m_box    = false;
    m_wall   = false;
  } else {
    m_pusher = false;
  }
}

void BoardCell::put_pusher() { set_has_pusher(true); }

void BoardCell::remove_pusher() { set_has_pusher(false); }

bool BoardCell::is_wall() const { return m_wall; }

void BoardCell::set_is_wall(bool rv) {
  if (rv == true) {
    m_wall = true;
    m_goal = m_pusher = m_box = false;
  } else {
    m_wall = false;
  }
}

bool BoardCell::is_in_playable_area() const { return m_playable; }

void BoardCell::set_is_in_playable_area(bool rv) { m_playable = rv; }

} // namespace game
} // namespace sokoengine
