#include "atomic_move.hpp"

using namespace std;

namespace sokoengine {

AtomicMove::AtomicMove(const Direction& direction, bool box_moved) :
  m_box_moved(false), m_pusher_selected(false), m_pusher_jumped(false),
  m_direction(0),
  m_pusher_id(DEFAULT_PIECE_ID),
  m_moved_box_id(NULL_ID)
{
  set_direction(direction);
  if (box_moved) set_is_push_or_pull(true);
  else set_is_move(true);
}

string AtomicMove::str() const {
  return string() +
    "AtomicMove(" +
    direction().str() +
    ", box_moved=" + (is_push_or_pull() ? "True" : "False") +
    ", is_jump=" + (is_jump() ? "True" : "False") +
    ", is_pusher_selection=" + (is_pusher_selection() ? "True" : "False") +
    ", pusher_id=" + (pusher_id() == NULL_ID ? "None" : to_string(pusher_id())) +
    ", moved_box_id=" + (moved_box_id() == NULL_ID ? "None" : to_string(moved_box_id())) +
    ")";
}

string AtomicMove::repr() const {
  return string() +
    "AtomicMove(" +
    direction().str() +
    ", box_moved=" + (is_push_or_pull() ? "True" : "False") +
    ")";
}

} // namespace sokoengine
