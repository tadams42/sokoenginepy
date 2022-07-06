#ifndef PUSHER_STEP_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define PUSHER_STEP_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

namespace sokoengine {
namespace game {

///
/// Represents single step of pusher movement.
///
/// Single step can be:
///
/// - ``move``: pusher moved without pushing box
/// - ``push/pull``: pusher pushed or pulled a box
/// - ``jump``: pusher jumped
/// - ``pusher selection``: pusher was selected among other pushers on board
///
/// @sa
///   - Mover
///   - BoardManager
///   - SokobanPlus
///
class LIBSOKOENGINE_API PusherStep {
public:
  ///
  /// @param direction direction in which movement was performed
  /// @param moved_box_id: ID of a box that was pushed or Config::NO_ID. Box usually
  ///        gets it's ID from BoardManager.
  /// @param is_jump flag marking this step as part of pusher jump in reverse solving
  ///        mode. See Mover for more details about reverse movement.
  /// @param is_pusher_selection marks this step as part of pusher selecting sequence
  /// on
  ///        boards with multiple pushers (Multiban game variant)
  /// @param pusher_id ID of pusher that performed movement. Pusher usually gets it's
  /// ID
  ///        from BoardManager
  /// @param is_current_pos flags this step as current position in game snapshot
  ///
  /// @throws std::invalid_argument single step can only be one thing at a time:
  /// `move`,
  ///         `push/pull` or `jump`.
  explicit PusherStep(
    const Direction &direction           = Direction::LEFT,
    piece_id_t       moved_box_id        = Config::NO_ID,
    bool             is_jump             = false,
    bool             is_pusher_selection = false,
    piece_id_t       pusher_id           = Config::DEFAULT_ID,
    bool             is_current_pos      = false
  );

  bool operator==(const PusherStep &rv) const;
  bool operator!=(const PusherStep &rv) const;

  ///
  /// Pretty print object
  ///
  std::string str() const;

  ///
  /// Pretty print object
  ///
  std::string repr() const;

  ///
  /// ID of box that was moved or Config::NO_ID if no box was moved.
  ///
  piece_id_t moved_box_id() const;

  ///
  /// When setting box ID on ie. `jump`, that `jump` will become `push`.
  /// To change `push` into `move`, set box ID to Config::NO_ID.
  ///
  void set_moved_box_id(piece_id_t id);

  ///
  /// ID of pusher that performed movement.
  ///
  piece_id_t pusher_id() const;

  ///
  /// Pusher ID must always be valid. When setting it to invalid value, PusherStep
  /// will silently set pusher ID to Config::DEFAULT_ID.
  ///
  void set_pusher_id(piece_id_t id);

  ///
  /// True if pusher didn't move box, didn't jump and didn't select another pusher.
  ///
  bool is_move() const;

  ///
  /// True if pusher moved a box.
  ///
  bool is_push_or_pull() const;

  ///
  /// True if this step is part of pusher selection sequence in `Multiban` games.
  ///
  bool is_pusher_selection() const;
  void set_is_pusher_selection(bool flag);

  ///
  /// True if this move is part of jump sequence in :attr:`.SolvingMode.REVERSE`
  /// games.
  ///
  bool is_jump() const;
  void set_is_jump(bool flag);

  bool             is_current_pos() const;
  void             set_is_current_pos(bool flag);
  const Direction &direction() const;
  void             set_direction(const Direction &direction);

private:
  bool       m_pusher_selected: 1;
  bool       m_pusher_jumped  : 1;
  bool       m_is_current_pos : 1;
  uint8_t    m_direction      : 5;
  piece_id_t m_pusher_id;
  piece_id_t m_moved_box_id;
};

namespace implementation {
LIBSOKOENGINE_LOCAL std::string direction_str(Direction d);
} // namespace implementation

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
