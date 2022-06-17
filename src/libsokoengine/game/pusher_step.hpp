#ifndef PUSHER_STEP_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define PUSHER_STEP_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "config.hpp"

namespace sokoengine {
namespace game {

///
/// Single step of single pusher.
///
class LIBSOKOENGINE_API PusherStep {
public:
  explicit PusherStep(const Direction &direction = Direction::LEFT,
                      piece_id_t moved_box_id = Config::NO_ID, bool is_jump = false,
                      bool is_pusher_selection = false,
                      piece_id_t pusher_id = Config::DEFAULT_ID,
                      bool is_current_pos = false);

  bool operator==(const PusherStep &rv) const;
  bool operator!=(const PusherStep &rv) const;

  std::string str() const;
  std::string repr() const;

  piece_id_t moved_box_id() const;
  void set_moved_box_id(piece_id_t id);
  piece_id_t pusher_id() const;
  void set_pusher_id(piece_id_t id);
  bool is_move() const;
  bool is_push_or_pull() const;
  bool is_pusher_selection() const;
  void set_is_pusher_selection(bool flag);
  bool is_jump() const;
  void set_is_jump(bool flag);
  bool is_current_pos() const;
  void set_is_current_pos(bool flag);
  const Direction &direction() const;
  void set_direction(const Direction &direction);

private:
  bool m_pusher_selected : 1;
  bool m_pusher_jumped : 1;
  bool m_is_current_pos : 1;
  uint8_t m_direction : 5;
  piece_id_t m_pusher_id;
  piece_id_t m_moved_box_id;
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
