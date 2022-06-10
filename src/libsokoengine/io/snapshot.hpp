#ifndef SNAPSHOT_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define SNAPSHOT_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

#include <memory>

namespace sokoengine {
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

  constexpr static bool is_pusher_step(char ch) {
    return ch == l || ch == u || ch == r || ch == d || ch == w || ch == e || ch == n ||
           ch == s || ch == L || ch == U || ch == R || ch == D || ch == W || ch == E ||
           ch == N || ch == S;
  }

  static bool is_snapshot(const std::string &line);
  static std::string cleaned_moves(const std::string &line);

  explicit Snapshot(size_t id = 0, const std::string &moves = "",
                    const std::string &title = "", const std::string &duration = "",
                    const std::string &solver = "", const std::string &created_at = "",
                    const std::string &updated_at = "",
                    const Strings &notes = Strings());
  Snapshot(const Snapshot &rv);
  Snapshot &operator=(const Snapshot &);
  virtual ~Snapshot();

  size_t id() const;
  size_t &id();
  const std::string &moves() const;
  std::string &moves();
  const std::string &title() const;
  std::string &title();
  const std::string &duration() const;
  std::string &duration();
  const std::string &solver() const;
  std::string &solver();
  const Strings &notes() const;
  Strings &notes();
  const std::string &created_at() const;
  std::string &created_at();
  const std::string &updated_at() const;
  std::string &updated_at();

  size_t pushes_count() const;
  size_t moves_count() const;
  bool is_reverse() const;

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
