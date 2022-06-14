#ifndef BOARD_CELL_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define BOARD_CELL_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "config.hpp"

namespace sokoengine {
namespace game {

///
/// Stores properties of one cell in board layout.
///
class LIBSOKOENGINE_API BoardCell {
public:
  explicit BoardCell(char rv = ' ', bool is_in_playable_area = false,
                     bool is_deadlock = false);

  bool operator==(const BoardCell &rv) const;
  bool operator!=(const BoardCell &rv) const;
  bool operator==(char rv) const;
  bool operator!=(char rv) const;

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
  bool m_box : 1;      // Does it contain box?
  bool m_pusher : 1;   // Does it contain pusher?
  bool m_goal : 1;     // Does it contain goal?
  bool m_wall : 1;     // Does it contain wall?
  bool m_playable : 1; // Is in playable area?
  bool m_deadlock : 1; // Is movement deadlock?
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
