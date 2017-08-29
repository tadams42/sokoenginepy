#ifndef BOARD_CELL_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define BOARD_CELL_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

#include <string>
#include <stdexcept>

namespace sokoengine {

///
/// Exception.
///
class LIBSOKOENGINE_API BoardConversionError: public std::runtime_error {
public:
  BoardConversionError(const std::string& mess);
  virtual ~BoardConversionError();
};

///
/// Exception.
///
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

  bool operator== (const BoardCell& rv) const;
  bool operator!= (const BoardCell& rv) const;

  char str() const;
  std::string repr() const;
  char to_str(bool use_visible_floor = false) const;

  void clear();
  bool has_piece() const;
  bool is_empty_floor() const;
  bool is_border_element() const;
  bool can_put_pusher_or_box() const;
  bool has_box() const;
  void set_has_box(bool rv);
  void put_box();
  void remove_box();
  bool has_goal() const;
  void set_has_goal(bool rv);
  void put_goal();
  void remove_goal();
  bool has_pusher() const;
  void set_has_pusher(bool rv);
  void put_pusher();
  void remove_pusher();
  bool is_wall() const;
  void set_is_wall(bool rv);
  bool is_in_playable_area() const;
  void set_is_in_playable_area(bool rv);
  bool is_deadlock() const;
  void set_is_deadlock(bool rv);

private:
  bool m_box      : 1; // Does it contain box?
  bool m_pusher   : 1; // Does it contain pusher?
  bool m_goal     : 1; // Does it contain goal?
  bool m_wall     : 1; // Does it contain wall?
  bool m_playable : 1; // Is in playable area?
  bool m_deadlock : 1; // Is movement deadlock?
};

} // namespace sokoengine

#endif // HEADER_GUARD
