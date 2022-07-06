#ifndef BOARD_CELL_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define BOARD_CELL_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

namespace sokoengine {
namespace game {

///
/// Stores properties of one cell in board layout.
///
/// @note
/// There is no game logic encoded in this class. It is perfectly fine to put pusher
/// on wall cell (in which case wall will be replaced by pusher). This is by design:
/// BoardCell is a value class, not game logic class.
///
class LIBSOKOENGINE_API BoardCell {
public:
  explicit BoardCell(char rv = ' ');

  bool operator==(const BoardCell &rv) const;
  bool operator!=(const BoardCell &rv) const;
  bool operator==(char rv) const;
  bool operator!=(char rv) const;

  ///
  /// Pretty-print cell contents.
  ///
  char to_str(bool use_visible_floor = false) const;

  ///
  /// Same as to_str() bit with hardcoded defaults.
  ///
  char str() const;

  ///
  /// Pretty-print cell object
  ///
  std::string repr() const;

  ///
  /// Clears cell, converting it to empty floor.
  ///
  void clear();

  ///
  /// True if there is pusher, box or goal on this cell.
  ///
  bool has_piece() const;

  ///
  /// True if there is no pieces and no wall on this cell.
  ///
  bool is_empty_floor() const;

  ///
  /// True if this is either a wall or box on goal.
  ///
  bool is_border_element() const;

  ///
  /// True if this cell allows putting box or pusher on self.
  ///
  /// @note
  /// This method is not used by BoardCell modifiers (ie. put_box(), put_pusher(),
  /// etc...). As far as BoardCell is concerned, nothing prevents clients from putting
  /// box on wall (which replaces that wall with box). This method is used by higher
  /// game logic that implement pusher movement in which case putting ie. pusher onto
  /// same cell where box is makes no sense.
  ///
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

private:
  bool m_box     : 1; // Does it contain box?
  bool m_pusher  : 1; // Does it contain pusher?
  bool m_goal    : 1; // Does it contain goal?
  bool m_wall    : 1; // Does it contain wall?
  bool m_playable: 1; // Is in playable area?
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
