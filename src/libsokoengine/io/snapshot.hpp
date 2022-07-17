#ifndef SNAPSHOT_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define SNAPSHOT_0FEA723A_C86F_6753_04ABD475F6FCA5FB
/// @file

#include "tessellation.hpp"

namespace sokoengine {

namespace game {
class PusherStep;
typedef std::vector<PusherStep> PusherSteps;
} // namespace game

namespace io {

///
/// Pusher steps and accompanying metadata.
///
/// Snapshot is parametrized by game::Tessellation.
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

  static constexpr char JUMP_BEGIN          = '[';
  static constexpr char JUMP_END            = ']';
  static constexpr char PUSHER_CHANGE_BEGIN = '{';
  static constexpr char PUSHER_CHANGE_END   = '}';
  static constexpr char CURRENT_POSITION_CH = '*';

  static std::string ast_json(const std::string &line);

  ///
  /// @param moves_data pusher steps in textual representation.
  ///
  Snapshot(const Tessellation &tessellation, const std::string &moves_data);
  Snapshot(const Snapshot &rv);
  Snapshot &operator=(const Snapshot &rv);
  Snapshot(Snapshot &&rv);
  Snapshot &operator=(Snapshot &&rv);
  virtual ~Snapshot();

  const std::string &title() const;
  std::string       &title();
  const std::string &solver() const;
  std::string       &solver();
  const std::string &notes() const;
  std::string       &notes();

  Tessellation tessellation() const;

  std::string to_str(bool rle_encode = false) const;
  std::string str() const;
  std::string repr() const;

  const std::string &moves_data() const;
  void               set_moves_data(const std::string &rv);
  game::PusherSteps  pusher_steps() const;
  void               set_pusher_steps(const game::PusherSteps &rv);

  size_t pushes_count() const;
  size_t moves_count() const;
  size_t jumps_count() const;
  bool   is_reverse() const;

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace io

using game::PusherSteps;
using io::Snapshot;

} // namespace sokoengine

#endif // HEADER_GUARD
