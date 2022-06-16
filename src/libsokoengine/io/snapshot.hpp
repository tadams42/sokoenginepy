#ifndef SNAPSHOT_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define SNAPSHOT_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "config.hpp"

#include <memory>

namespace sokoengine {

namespace game {
class PusherStep;
typedef std::vector<PusherStep> PusherSteps;
}

namespace io {

///
/// Recording of pusher movement with accompanying metadata.
///
class LIBSOKOENGINE_API Snapshot {
public:
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

  static constexpr char JUMP_BEGIN = '[';
  static constexpr char JUMP_END = ']';
  static constexpr char PUSHER_CHANGE_BEGIN = '{';
  static constexpr char PUSHER_CHANGE_END = '}';
  static constexpr char CURRENT_POSITION_CH = '*';

  static constexpr bool is_move_step(char ch) {
    return ch == l || ch == u || ch == r || ch == d || ch == w || ch == e || ch == n ||
           ch == s;
  }

  static constexpr bool is_push_step(char ch) {
    return ch == L || ch == U || ch == R || ch == D || ch == W || ch == E || ch == N ||
           ch == S;
  }

  static constexpr bool is_pusher_step(char ch) {
    return is_move_step(ch) || is_push_step(ch);
  }

  static constexpr bool is_marker(char ch) {
    return ch == JUMP_BEGIN || ch == JUMP_END || ch == PUSHER_CHANGE_BEGIN ||
           ch == PUSHER_CHANGE_END || ch == CURRENT_POSITION_CH;
  }

  static bool is_snapshot(const std::string &line);
  static std::string ast_json(const std::string &line);

  typedef std::unique_ptr<Snapshot> unique_ptr_t;
  virtual unique_ptr_t clone() const = 0;

  virtual ~Snapshot();

  const std::string &title() const;
  std::string &title();
  const std::string &solver() const;
  std::string &solver();
  const Strings &notes() const;
  Strings &notes();

  game::Tessellation tessellation() const;

  std::string to_str(bool rle_encode = false) const;
  std::string str() const;
  std::string repr() const;

  const std::string &moves_data() const;
  void set_moves_data(const std::string &rv);
  game::PusherSteps pusher_steps() const;
  void set_pusher_steps(const game::PusherSteps &rv);

  size_t pushes_count() const;
  size_t moves_count() const;
  size_t jumps_count() const;
  bool is_reverse() const;

protected:
  Snapshot(const game::Tessellation &tessellation, const std::string &moves_data);
  Snapshot(const Snapshot &rv);
  Snapshot &operator=(const Snapshot &rv);
  Snapshot(Snapshot &&rv);
  Snapshot &operator=(Snapshot &&rv);

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
