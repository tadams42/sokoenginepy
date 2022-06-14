#include "pusher_step.hpp"

#include "tessellation.hpp"

#include <stdexcept>

using namespace std;

namespace sokoengine {
namespace game {

PusherStep::PusherStep(const Direction &direction, bool box_moved, bool is_jump,
                       bool is_pusher_selection, piece_id_t pusher_id,
                       piece_id_t moved_box_id, bool is_current_pos)
  : m_box_moved(false),
    m_pusher_selected(false),
    m_pusher_jumped(false),
    m_is_current_pos(is_current_pos),
    m_direction(direction_pack(Direction::LEFT)),
    m_pusher_id(Config::DEFAULT_PIECE_ID),
    m_moved_box_id(Config::NULL_ID) {
  if ((box_moved || moved_box_id != Config::NULL_ID) && is_pusher_selection && is_jump)
    throw invalid_argument(
      "PusherStep can't be all, a push, a jump and a pusher selection!");

  if (is_jump && is_pusher_selection)
    throw invalid_argument("PusherStep can't be both, a jump and a pusher selection!");

  if ((box_moved || moved_box_id != Config::NULL_ID) && is_jump)
    throw invalid_argument("PusherStep can't be both, a push and a jump!");

  if ((box_moved || moved_box_id != Config::NULL_ID) && is_pusher_selection)
    throw invalid_argument("PusherStep can't be both, a push and a pusher selection!");

  set_pusher_id(pusher_id);

  set_direction(direction);
  if (box_moved)
    set_is_push_or_pull(true);
  else
    set_is_move(true);

  if (moved_box_id != Config::NULL_ID) set_moved_box_id(moved_box_id);

  if (is_jump) set_is_jump(is_jump);

  if (is_pusher_selection) set_is_pusher_selection(is_pusher_selection);
}

bool PusherStep::operator==(const PusherStep &rv) const {
  return m_direction == rv.m_direction && m_box_moved == rv.m_box_moved &&
         m_pusher_selected == rv.m_pusher_selected &&
         m_pusher_jumped == rv.m_pusher_jumped;
}
bool PusherStep::operator!=(const PusherStep &rv) const { return !(*this == rv); }

string PusherStep::str() const {
  return string() + "PusherStep(" + BaseTessellation::direction_str(direction()) +
         ", box_moved=" + (is_push_or_pull() ? "True" : "False") +
         ", is_jump=" + (is_jump() ? "True" : "False") +
         ", is_pusher_selection=" + (is_pusher_selection() ? "True" : "False") +
         ", pusher_id=" +
         (pusher_id() == Config::NULL_ID ? "None" : to_string(pusher_id())) +
         ", moved_box_id=" +
         (moved_box_id() == Config::NULL_ID ? "None" : to_string(moved_box_id())) + ")";
}

string PusherStep::repr() const {
  return string() + "PusherStep(" + BaseTessellation::direction_repr(direction()) +
         ", box_moved=" + (is_push_or_pull() ? "True" : "False") + ")";
}

piece_id_t PusherStep::moved_box_id() const {
  if (is_push_or_pull()) return m_moved_box_id;
  return Config::NULL_ID;
}

void PusherStep::set_moved_box_id(piece_id_t id) {
  if (id >= Config::DEFAULT_PIECE_ID) {
    m_moved_box_id = id;
    set_is_push_or_pull(true);
  } else {
    m_moved_box_id = Config::NULL_ID;
    set_is_push_or_pull(false);
  }
}

piece_id_t PusherStep::pusher_id() const { return m_pusher_id; }

void PusherStep::set_pusher_id(piece_id_t id) {
  if (id >= Config::DEFAULT_PIECE_ID)
    m_pusher_id = id;
  else
    m_pusher_id = Config::DEFAULT_PIECE_ID;
}

bool PusherStep::is_move() const {
  return !m_box_moved && !m_pusher_selected && !m_pusher_jumped;
}

void PusherStep::set_is_move(bool flag) {
  if (flag) {
    m_box_moved = false;
    m_pusher_jumped = false;
    m_pusher_selected = false;
    m_moved_box_id = Config::NULL_ID;
  } else {
    m_box_moved = true;
    m_pusher_jumped = false;
    m_pusher_selected = false;
  }
}

bool PusherStep::is_push_or_pull() const {
  return m_box_moved && !m_pusher_selected && !m_pusher_jumped;
}

void PusherStep::set_is_push_or_pull(bool flag) {
  if (flag) {
    m_box_moved = true;
    m_pusher_jumped = false;
    m_pusher_selected = false;
  } else {
    m_box_moved = false;
    m_moved_box_id = Config::NULL_ID;
  }
}

bool PusherStep::is_pusher_selection() const {
  return m_pusher_selected && !m_box_moved && !m_pusher_jumped;
}

void PusherStep::set_is_pusher_selection(bool flag) {
  if (flag) {
    m_pusher_selected = true;
    m_box_moved = false;
    m_pusher_jumped = false;
    m_moved_box_id = Config::NULL_ID;
  } else {
    m_pusher_selected = false;
  }
}

bool PusherStep::is_jump() const {
  return m_pusher_jumped && !m_pusher_selected && !m_box_moved;
}

void PusherStep::set_is_jump(bool flag) {
  if (flag) {
    m_pusher_jumped = true;
    m_pusher_selected = false;
    m_box_moved = false;
    m_moved_box_id = Config::NULL_ID;
  } else {
    m_pusher_jumped = false;
  }
}

bool PusherStep::is_current_pos() const { return m_is_current_pos; }

void PusherStep::set_is_current_pos(bool flag) { m_is_current_pos = flag; }

const Direction &PusherStep::direction() const { return direction_unpack(m_direction); }

void PusherStep::set_direction(const Direction &direction) {
  m_direction = direction_pack(direction);
}

} // namespace game
} // namespace sokoengine
