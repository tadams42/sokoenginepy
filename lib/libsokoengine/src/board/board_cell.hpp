#ifndef BOARD_CELL_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define BOARD_CELL_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

#include <string>
#include <stdexcept>

namespace sokoengine {

class LIBSOKOENGINE_API BoardConversionError: public std::runtime_error {
public:
  BoardConversionError(const std::string& mess);
  virtual ~BoardConversionError();
};

class LIBSOKOENGINE_API IllegalBoardCharacterError: public std::invalid_argument {
public:
  IllegalBoardCharacterError(const std::string& mess);
  virtual ~IllegalBoardCharacterError();
};

///
/// Stores properties of one cell in board layout.
///
class LIBSOKOENGINE_API BoardCell {
public:
  ///
  /// Characters used in textual representation of board cells.
  ///
  enum Characters {
    WALL                = '#',
    PUSHER              = '@',
    PUSHER_ON_GOAL      = '+',
    BOX                 = '$',
    BOX_ON_GOAL         = '*',
    GOAL                = '.',
    FLOOR               = ' ',
    VISIBLE_FLOOR       = '-',
    ALT_PUSHER1         = 'p',
    ALT_PUSHER2         = 'm',
    ALT_PUSHER_ON_GOAL1 = 'P',
    ALT_PUSHER_ON_GOAL2 = 'M',
    ALT_BOX1            = 'b',
    ALT_BOX_ON_GOAL1    = 'B',
    ALT_GOAL1           = 'o',
    ALT_VISIBLE_FLOOR1  = '_',
  };

  constexpr static bool is_pusher_chr(char ch) {
    return ch == PUSHER ||
           ch == ALT_PUSHER1 ||
           ch == ALT_PUSHER2 ||
           ch == PUSHER_ON_GOAL ||
           ch == ALT_PUSHER_ON_GOAL1 ||
           ch == ALT_PUSHER_ON_GOAL2;
  }

  constexpr static bool is_box_chr(char ch) {
    return ch == BOX ||
           ch == ALT_BOX1 ||
           ch == BOX_ON_GOAL ||
           ch == ALT_BOX_ON_GOAL1;
  }

  constexpr static bool is_goal_chr(char ch) {
    return ch == GOAL ||
           ch == ALT_GOAL1 ||
           ch == BOX_ON_GOAL ||
           ch == ALT_BOX_ON_GOAL1 ||
           ch == PUSHER_ON_GOAL ||
           ch == ALT_PUSHER_ON_GOAL1 ||
           ch == ALT_PUSHER_ON_GOAL2;
  }

  constexpr static bool is_empty_floor_chr(char ch) {
    return ch == FLOOR ||
           ch == VISIBLE_FLOOR ||
           ch == ALT_VISIBLE_FLOOR1;
  }

  constexpr static bool is_wall_chr(char ch) {
    return ch == WALL;
  }

  explicit BoardCell(
    char rv = ' ', bool is_in_playable_area=false, bool is_deadlock=false
  );

  bool operator== (const BoardCell& rv) const {
    return m_wall == rv.m_wall &&
           m_pusher == rv.m_pusher &&
           m_box == rv.m_box &&
           m_goal == rv.m_goal;
  }

  bool operator!= (const BoardCell& rv) const {
    return !(*this == rv);
  }

  char str() const;
  std::string repr() const;
  char to_str(bool use_visible_floor = false) const;

  void clear() { m_wall = m_goal = m_pusher = m_box = false; }

  bool has_piece() const { return m_goal || m_box || m_pusher; }

  bool is_empty_floor() const {
      return !(m_wall || m_pusher || m_box || m_goal);
  }

  ///
  /// Returns true if this is either wall or box on goal.
  ///
  bool is_border_element() const { return m_wall || (m_box && m_goal); }

  ///
  /// Pusher or box can be dropped on empty goal or empty floor
  ///
  bool can_put_pusher_or_box() const { return !(m_box || m_pusher || m_wall); }

  bool has_box() const { return m_box; }

  void set_has_box(bool rv) {
    if (rv == true) {
      m_box = true;
      m_wall = false;
      m_pusher = false;
    } else {
      m_box = false;
    }
  }

  void put_box() { set_has_box(true); }

  void remove_box() { set_has_box(false); }

  bool has_goal() const { return m_goal; }

  void set_has_goal(bool rv) {
    if (rv == true) {
      m_goal = true;
      m_wall = false;
    } else {
      m_goal = false;
    }
  }

  void put_goal() { set_has_goal(true); }

  void remove_goal() { set_has_goal(false); }

  bool has_pusher() const { return m_pusher; }

  void set_has_pusher(bool rv) {
    if (rv == true) {
      m_pusher = true;
      m_box = false;
      m_wall = false;
    } else {
      m_pusher = false;
    }
  }

  void put_pusher() { set_has_pusher(true); }

  void remove_pusher() { set_has_pusher(false); }

  bool is_wall() const { return m_wall; }

  void set_is_wall(bool rv) {
    if (rv == true) {
      m_wall = true;
      m_goal = m_pusher = m_box = false;
    } else {
      m_wall = false;
    }
  }

  bool is_in_playable_area() const { return m_playable; }
  void set_is_in_playable_area(bool rv) { m_playable = rv; }

  bool is_deadlock() const { return m_deadlock; }
  void set_is_deadlock(bool rv) { m_deadlock = rv; }

private:
  bool m_box      : 1; ///< Does it contain box?
  bool m_pusher   : 1; ///< Does it contain pusher?
  bool m_goal     : 1; ///< Does it contain goal?
  bool m_wall     : 1; ///< Does it contain wall?
  bool m_playable : 1; ///< Is in playable area?
  bool m_deadlock : 1; ///< Is movement deadlock?
};

} // namespace sokoengine

#endif // HEADER_GUARD
