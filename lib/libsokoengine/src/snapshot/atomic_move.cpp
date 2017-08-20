#include "atomic_move.hpp"

using namespace std;

namespace sokoengine {

InvalidAtomicMoveError::InvalidAtomicMoveError(const string& mess):
  invalid_argument(mess)
{}

InvalidAtomicMoveError::~InvalidAtomicMoveError() = default;


AtomicMove::AtomicMove(
  const Direction& direction, bool box_moved, bool is_jump,
  bool is_pusher_selection, piece_id_t pusher_id, piece_id_t moved_box_id
) :
  m_box_moved(false), m_pusher_selected(false), m_pusher_jumped(false),
  m_direction(0), m_pusher_id(DEFAULT_PIECE_ID), m_moved_box_id(NULL_ID)
{
  if ((box_moved || moved_box_id != NULL_ID) && is_pusher_selection && is_jump)
    throw InvalidAtomicMoveError(
      "AtomicMove can't be all, a push, a jump and a pusher selection!"
    );

  if (is_jump && is_pusher_selection)
    throw InvalidAtomicMoveError(
      "AtomicMove can't be both, a jump and a pusher selection!"
    );

  if ((box_moved || moved_box_id != NULL_ID) && is_jump)
    throw InvalidAtomicMoveError(
      "AtomicMove can't be both, a push and a jump!"
    );

  if ((box_moved || moved_box_id != NULL_ID) && is_pusher_selection)
    throw InvalidAtomicMoveError(
      "AtomicMove can't be both, a push and a pusher selection!"
    );

  set_direction(direction);
  if (box_moved) set_is_push_or_pull(true);
  else set_is_move(true);

  if (moved_box_id != NULL_ID)
    set_moved_box_id(moved_box_id);

  if (is_jump)
    set_is_jump(is_jump);

  if (is_pusher_selection)
    set_is_pusher_selection(is_pusher_selection);
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
