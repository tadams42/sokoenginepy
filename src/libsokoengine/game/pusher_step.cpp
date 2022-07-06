#include "pusher_step.hpp"

#include "tessellation.hpp"

#include <boost/algorithm/string.hpp>
#include <stdexcept>

using sokoengine::implementation::Strings;
using sokoengine::io::is_blank;
using std::invalid_argument;
using std::runtime_error;
using std::string;
using std::to_string;

namespace sokoengine {
namespace game {
namespace implementation {

string direction_str(Direction d) {
  switch (d) {
    case Direction::UP:
      return "Direction.UP";
      break;
    case Direction::DOWN:
      return "Direction.DOWN";
      break;
    case Direction::LEFT:
      return "Direction.LEFT";
      break;
    case Direction::RIGHT:
      return "Direction.RIGHT";
      break;
    case Direction::NORTH_EAST:
      return "Direction.NORTH_EAST";
      break;
    case Direction::NORTH_WEST:
      return "Direction.NORTH_WEST";
      break;
    case Direction::SOUTH_EAST:
      return "Direction.SOUTH_EAST";
      break;
    case Direction::SOUTH_WEST:
      return "Direction.SOUTH_WEST";
      break;
  }
  throw runtime_error("Unhandled direction!");
}

} // namespace implementation

using implementation::direction_str;

PusherStep::PusherStep(
  const Direction &direction,
  piece_id_t       moved_box_id,
  bool             is_jump,
  bool             is_pusher_selection,
  piece_id_t       pusher_id,
  bool             is_current_pos
)
  : m_pusher_selected(is_pusher_selection)
  , m_pusher_jumped(is_jump)
  , m_is_current_pos(is_current_pos)
  , m_direction(direction_pack(direction)) {
  bool box_moved = moved_box_id != Config::NO_ID or moved_box_id >= Config::DEFAULT_ID;

  if (box_moved && is_pusher_selection && is_jump)
    throw invalid_argument(
      "PusherStep can't be everything, a push, a jump and a pusher selection, all at "
      "once!"
    );
  if (box_moved && is_jump)
    throw invalid_argument("PusherStep can't be both, a push and a jump!");
  if (box_moved && is_pusher_selection)
    throw invalid_argument("PusherStep can't be both, a push and a pusher selection!");
  if (is_jump && is_pusher_selection)
    throw invalid_argument("PusherStep can't be both, a jump and a pusher selection!");

  set_moved_box_id(moved_box_id);
  set_pusher_id(pusher_id);
}

bool PusherStep::operator==(const PusherStep &rv) const {
  return m_direction == rv.m_direction && is_push_or_pull() == rv.is_push_or_pull()
      && m_pusher_selected == rv.m_pusher_selected
      && m_pusher_jumped == rv.m_pusher_jumped;
}

bool PusherStep::operator!=(const PusherStep &rv) const { return !(*this == rv); }

string PusherStep::repr() const {
  string s_pusher_id;
  if (m_pusher_id != Config::DEFAULT_ID) {
    s_pusher_id =
      "pusher_id=Config.DEFAULT_ID + " + to_string(m_pusher_id - Config::DEFAULT_ID);
  }

  string s_box_id;
  if (m_moved_box_id != Config::NO_ID) {
    if (m_moved_box_id == Config::DEFAULT_ID)
      s_box_id = "moved_box_id=Config.DEFAULT_ID";
    else
      s_box_id = "moved_box_id=Config.DEFAULT_ID + "
               + to_string(m_moved_box_id - Config::DEFAULT_ID);
  }

  string s_jump;
  if (m_pusher_jumped)
    s_jump = "is_jump=True";

  string s_pusher_select;
  if (m_pusher_selected)
    s_pusher_select = "is_pusher_selection=True";

  string curr_pos;
  if (m_is_current_pos)
    curr_pos = "is_current_pos=True";

  Strings args;
  args.push_back(direction_str(direction()));
  if (!is_blank(s_box_id))
    args.push_back(s_box_id);
  if (!is_blank(s_jump))
    args.push_back(s_jump);
  if (!is_blank(s_pusher_select))
    args.push_back(s_pusher_select);
  if (!is_blank(s_pusher_id))
    args.push_back(s_pusher_id);
  if (!is_blank(curr_pos))
    args.push_back(curr_pos);

  return string("PusherStep(") + boost::join(args, ", ") + ")";
}

string PusherStep::str() const { return repr(); }

piece_id_t PusherStep::moved_box_id() const { return m_moved_box_id; }

void PusherStep::set_moved_box_id(piece_id_t id) {
  if (id == Config::NO_ID || id < Config::DEFAULT_ID) {
    m_moved_box_id = Config::NO_ID;
  } else {
    m_moved_box_id    = id;
    m_pusher_selected = false;
    m_pusher_jumped   = false;
  }
}

piece_id_t PusherStep::pusher_id() const { return m_pusher_id; }

void PusherStep::set_pusher_id(piece_id_t id) {
  if (id == Config::NO_ID || id < Config::DEFAULT_ID) {
    m_pusher_id = Config::DEFAULT_ID;
  } else {
    m_pusher_id = id;
  }
}

bool PusherStep::is_move() const {
  return m_moved_box_id == Config::NO_ID && !m_pusher_selected && !m_pusher_jumped;
}

bool PusherStep::is_push_or_pull() const {
  return m_moved_box_id != Config::NO_ID && !m_pusher_selected && !m_pusher_jumped;
}

bool PusherStep::is_pusher_selection() const { return m_pusher_selected; }

void PusherStep::set_is_pusher_selection(bool flag) {
  if (flag) {
    m_pusher_selected = true;
    m_pusher_jumped   = false;
    m_moved_box_id    = Config::NO_ID;
  } else {
    m_pusher_selected = false;
  }
}

bool PusherStep::is_jump() const { return m_pusher_jumped; }

void PusherStep::set_is_jump(bool flag) {
  if (flag) {
    m_pusher_jumped   = true;
    m_pusher_selected = false;
    m_moved_box_id    = Config::NO_ID;
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
