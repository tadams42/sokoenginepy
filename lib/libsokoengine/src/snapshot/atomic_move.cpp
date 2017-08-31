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
  m_direction(Direction::LEFT.pack()), m_pusher_id(DEFAULT_PIECE_ID),
  m_moved_box_id(NULL_ID)
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

bool AtomicMove::operator== (const AtomicMove& rv) const {
  return m_direction == rv.m_direction &&
         m_box_moved == rv.m_box_moved &&
         m_pusher_selected == rv.m_pusher_selected &&
         m_pusher_jumped == rv.m_pusher_jumped;
}
bool AtomicMove::operator!= (const AtomicMove& rv) const { return !(*this == rv); }

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

piece_id_t AtomicMove::moved_box_id() const {
  if (is_push_or_pull()) return m_moved_box_id;
  else return NULL_ID;
}

void AtomicMove::set_moved_box_id(piece_id_t id) {
  if (id >= DEFAULT_PIECE_ID) {
    m_moved_box_id = id;
    set_is_push_or_pull(true);
  } else {
    m_moved_box_id = NULL_ID;
    set_is_push_or_pull(false);
  }
}

piece_id_t AtomicMove::pusher_id() const { return m_pusher_id; }

void AtomicMove::set_pusher_id (piece_id_t id) {
  if (id >= DEFAULT_PIECE_ID) m_pusher_id = id;
  else m_pusher_id = DEFAULT_PIECE_ID;
}

bool AtomicMove::is_move() const {
  return !m_box_moved && !m_pusher_selected && !m_pusher_jumped;
}

void AtomicMove::set_is_move(bool flag) {
  if (flag) {
    m_box_moved = false;
    m_pusher_jumped = false;
    m_pusher_selected = false;
    m_moved_box_id = NULL_ID;
  } else {
    m_box_moved = true;
    m_pusher_jumped = false;
    m_pusher_selected = false;
  }
}

bool AtomicMove::is_push_or_pull() const {
  return m_box_moved && !m_pusher_selected && !m_pusher_jumped;
}

void AtomicMove::set_is_push_or_pull(bool flag) {
  if (flag) {
    m_box_moved = true;
    m_pusher_jumped = false;
    m_pusher_selected = false;
  } else {
    m_box_moved = false;
    m_moved_box_id = NULL_ID;
  }
}

bool AtomicMove::is_pusher_selection() const {
  return m_pusher_selected && !m_box_moved && !m_pusher_jumped;
}

void AtomicMove::set_is_pusher_selection(bool flag) {
  if (flag) {
    m_pusher_selected = true;
    m_box_moved = false;
    m_pusher_jumped = false;
    m_moved_box_id = NULL_ID;
  } else {
    m_pusher_selected = false;
  }
}

bool AtomicMove::is_jump() const {
  return m_pusher_jumped && !m_pusher_selected && !m_box_moved;
}

void AtomicMove::set_is_jump(bool flag) {
  if (flag) {
    m_pusher_jumped = true;
    m_pusher_selected = false;
    m_box_moved = false;
    m_moved_box_id = NULL_ID;
  } else {
    m_pusher_jumped = false;
  }
}

const Direction& AtomicMove::direction() const {
  return Direction::unpack(m_direction);
}

void AtomicMove::set_direction(const Direction& direction) {
  m_direction = direction.pack();
}

} // namespace sokoengine
