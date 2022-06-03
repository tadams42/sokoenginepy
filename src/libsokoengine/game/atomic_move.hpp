#ifndef ATOMIC_MOVE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define ATOMIC_MOVE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"
#include "direction.hpp"

#include <stdexcept>

namespace sokoengine {
namespace game {

///
/// Single step of single pusher.
///
class LIBSOKOENGINE_API AtomicMove {
public:
  explicit AtomicMove(const Direction &direction = Direction::LEFT,
                      bool box_moved = false, bool is_jump = false,
                      bool is_pusher_selection = false,
                      piece_id_t pusher_id = DEFAULT_PIECE_ID,
                      piece_id_t moved_box_id = NULL_ID);

  bool operator==(const AtomicMove &rv) const;
  bool operator!=(const AtomicMove &rv) const;

  std::string str() const;
  std::string repr() const;
  piece_id_t moved_box_id() const;
  void set_moved_box_id(piece_id_t id);
  piece_id_t pusher_id() const;
  void set_pusher_id(piece_id_t id);
  bool is_move() const;
  void set_is_move(bool flag);
  bool is_push_or_pull() const;
  void set_is_push_or_pull(bool flag);
  bool is_pusher_selection() const;
  void set_is_pusher_selection(bool flag);
  bool is_jump() const;
  void set_is_jump(bool flag);
  const Direction &direction() const;
  void set_direction(const Direction &direction);

private:
  bool m_box_moved : 1;
  bool m_pusher_selected : 1;
  bool m_pusher_jumped : 1;
  uint8_t m_direction: 5;
  piece_id_t m_pusher_id;
  piece_id_t m_moved_box_id;
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
