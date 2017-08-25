#ifndef ATOMIC_MOVE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define ATOMIC_MOVE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"
#include "direction.hpp"

#include <string>
#include <stdexcept>

namespace sokoengine {

class LIBSOKOENGINE_API InvalidAtomicMoveError: public std::invalid_argument {
public:
  InvalidAtomicMoveError(const std::string& mess);
  virtual ~InvalidAtomicMoveError();
};

class LIBSOKOENGINE_API AtomicMove {
public:
  enum Characters {
    l = 'l', u = 'u', r = 'r', d = 'd',
    L = 'L', U = 'U', R = 'R', D = 'D',
    w = 'w', W = 'W', e = 'e', E = 'E',
    n = 'n', N = 'N', s = 's', S = 'S'
  };

  constexpr static bool is_atomic_move(char ch) {
    return ch == l || ch == u || ch == r || ch == d ||
           ch == w || ch == e || ch == n || ch == s ||
           ch == L || ch == U || ch == R || ch == D ||
           ch == W || ch == E || ch == N || ch == S;
  }

  AtomicMove(
    const Direction& direction=Direction::LEFT, bool box_moved=false,
    bool is_jump=false, bool is_pusher_selection=false,
    piece_id_t pusher_id=DEFAULT_PIECE_ID, piece_id_t moved_box_id=NULL_ID
  );

  bool operator== (const AtomicMove& rv) const {
    return direction() == rv.direction() &&
           is_push_or_pull() == rv.is_push_or_pull() &&
           is_pusher_selection() == rv.is_pusher_selection() &&
           is_jump() == rv.is_jump();
  }
  bool operator!= (const AtomicMove& rv) const { return !(*this == rv); }

  std::string str() const;
  std::string repr() const;

  piece_id_t moved_box_id() const {
    if (is_push_or_pull()) {
      return m_moved_box_id;
    } else {
      return NULL_ID;
    }
  }

  void set_moved_box_id(piece_id_t id) {
    if (id >= DEFAULT_PIECE_ID) {
      m_moved_box_id = id;
      set_is_push_or_pull(true);
    } else {
      m_moved_box_id = NULL_ID;
      set_is_push_or_pull(false);
    }
  }

  piece_id_t pusher_id() const { return m_pusher_id; }

  void set_pusher_id (piece_id_t id) {
    if (id >= DEFAULT_PIECE_ID) {
      m_pusher_id = id;
    } else {
      m_pusher_id = DEFAULT_PIECE_ID;
    }
  }

  bool is_move() const {
    return !m_box_moved && !m_pusher_selected && !m_pusher_jumped;
  }

  void set_is_move(bool flag) {
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

  bool is_push_or_pull() const {
    return m_box_moved && !m_pusher_selected && !m_pusher_jumped;
  }

  void set_is_push_or_pull(bool flag) {
    if (flag) {
      m_box_moved = true;
      m_pusher_jumped = false;
      m_pusher_selected = false;
    } else {
      m_box_moved = false;
      m_moved_box_id = NULL_ID;
    }
  }

  bool is_pusher_selection() const {
    return m_pusher_selected && !m_box_moved && !m_pusher_jumped;
  }

  void set_is_pusher_selection(bool flag) {
    if (flag) {
      m_pusher_selected = true;
      m_box_moved = false;
      m_pusher_jumped = false;
      m_moved_box_id = NULL_ID;
    } else {
      m_pusher_selected = false;
    }
  }

  bool is_jump() const {
    return m_pusher_jumped && !m_pusher_selected && !m_box_moved;
  }

  void set_is_jump(bool flag) {
    if (flag) {
      m_pusher_jumped = true;
      m_pusher_selected = false;
      m_box_moved = false;
      m_moved_box_id = NULL_ID;
    } else {
      m_pusher_jumped = false;
    }
  }

  const Direction& direction() const {
    switch (m_direction) {
      case 0:
        return Direction::LEFT;
      case 1:
        return Direction::RIGHT;
      case 2:
        return Direction::UP;
      case 3:
        return Direction::DOWN;
      case 4:
        return Direction::NORTH_WEST;
      case 5:
        return Direction::NORTH_EAST;
      case 6:
        return Direction::SOUTH_WEST;
      case 7:
      default:
        return Direction::SOUTH_EAST;
    }
  }

  void set_direction(const Direction& direction) {
    if (direction == Direction::LEFT) m_direction = 0;
    else if (direction == Direction::RIGHT) m_direction = 1;
    else if (direction == Direction::UP) m_direction = 2;
    else if (direction == Direction::DOWN) m_direction = 3;
    else if (direction == Direction::NORTH_WEST) m_direction = 4;
    else if (direction == Direction::NORTH_EAST) m_direction = 5;
    else if (direction == Direction::SOUTH_WEST) m_direction = 6;
    else
      // if (direction == Direction::SOUTH_EAST)
      m_direction = 7;
  }

private:
  bool m_box_moved          : 1;
  bool m_pusher_selected    : 1;
  bool m_pusher_jumped      : 1;
  unsigned char m_direction : 5;
  piece_id_t m_pusher_id;
  piece_id_t m_moved_box_id;
};

} // namespace sokoengine

#endif // HEADER_GUARD
