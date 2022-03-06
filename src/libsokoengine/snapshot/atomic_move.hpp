#ifndef ATOMIC_MOVE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define ATOMIC_MOVE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "direction.hpp"
#include "sokoengine_config.hpp"

#include <stdexcept>
#include <string>

namespace sokoengine {

///
/// Single step of single pusher.
///
class LIBSOKOENGINE_API AtomicMove {
public:
  // Characters representing AtomicMove in game snapshot strings.

  static constexpr char l = 'l';
  static constexpr char u = 'u';
  static constexpr char r = 'r';
  static constexpr char d = 'd';
  static constexpr char L = 'L';
  static constexpr char U = 'U';
  static constexpr char R = 'R';
  static constexpr char D = 'D';
  static constexpr char w = 'w';
  static constexpr char W = 'W';
  static constexpr char e = 'e';
  static constexpr char E = 'E';
  static constexpr char n = 'n';
  static constexpr char N = 'N';
  static constexpr char s = 's';
  static constexpr char S = 'S';

  constexpr static bool is_atomic_move_chr(char ch) {
    return ch == l || ch == u || ch == r || ch == d || ch == w || ch == e || ch == n ||
           ch == s || ch == L || ch == U || ch == R || ch == D || ch == W || ch == E ||
           ch == N || ch == S;
  }

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
  Direction::packed_t m_direction : 5;
  piece_id_t m_pusher_id;
  piece_id_t m_moved_box_id;
};

} // namespace sokoengine

#endif // HEADER_GUARD
