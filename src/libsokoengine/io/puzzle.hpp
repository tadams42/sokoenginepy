#ifndef PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "puzzle_types.hpp"

#include <vector>
#include <memory>

namespace sokoengine {
  namespace io {

class LIBSOKOENGINE_API Snapshot;

///
/// DEfault type for sequence of Snapshot
///
typedef std::vector<Snapshot> Snapshots;

///
/// Game board with accompanying metadata.
///
class LIBSOKOENGINE_API Puzzle {
public:
  static constexpr char WALL = '#';
  static constexpr char PUSHER = '@';
  static constexpr char PUSHER_ON_GOAL = '+';
  static constexpr char BOX = '$';
  static constexpr char BOX_ON_GOAL = '*';
  static constexpr char GOAL = '.';
  static constexpr char FLOOR = ' ';
  static constexpr char VISIBLE_FLOOR = '-';
  static constexpr char ALT_PUSHER1 = 'p';
  static constexpr char ALT_PUSHER2 = 'm';
  static constexpr char ALT_PUSHER_ON_GOAL1 = 'P';
  static constexpr char ALT_PUSHER_ON_GOAL2 = 'M';
  static constexpr char ALT_BOX1 = 'b';
  static constexpr char ALT_BOX_ON_GOAL1 = 'B';
  static constexpr char ALT_GOAL1 = 'o';
  static constexpr char ALT_VISIBLE_FLOOR1 = '_';

  constexpr static bool is_pusher(char ch) {
    return ch == PUSHER || ch == ALT_PUSHER1 || ch == ALT_PUSHER2 ||
           ch == PUSHER_ON_GOAL || ch == ALT_PUSHER_ON_GOAL1 ||
           ch == ALT_PUSHER_ON_GOAL2;
  }

  constexpr static bool is_box(char ch) {
    return ch == BOX || ch == ALT_BOX1 || ch == BOX_ON_GOAL || ch == ALT_BOX_ON_GOAL1;
  }

  constexpr static bool is_goal(char ch) {
    return ch == GOAL || ch == ALT_GOAL1 || ch == BOX_ON_GOAL ||
           ch == ALT_BOX_ON_GOAL1 || ch == PUSHER_ON_GOAL ||
           ch == ALT_PUSHER_ON_GOAL1 || ch == ALT_PUSHER_ON_GOAL2;
  }

  constexpr static bool is_empty_floor(char ch) {
    return ch == FLOOR || ch == VISIBLE_FLOOR || ch == ALT_VISIBLE_FLOOR1;
  }

  constexpr static bool is_wall(char ch) { return ch == WALL; }

  static bool is_board(const std::string &line);
  static bool is_sokoban_plus(const std::string &line);

  explicit Puzzle(size_t id = 0, const std::string &board = "",
                  const std::string &title = "", const std::string &author = "",
                  const std::string &boxorder = "", const std::string &goalorder = "",
                  const std::string &notes = "", const std::string &created_at = "",
                  const std::string &updated_at = "",
                  const PuzzleTypes &puzzle_type = PuzzleTypes::SOKOBAN);
  Puzzle(const Puzzle &rv);
  Puzzle& operator=(const Puzzle&);
  virtual ~Puzzle();

  void clear();

  size_t id() const;
  size_t &id();
  const std::string &board() const;
  std::string &board();
  const PuzzleTypes &puzzle_type() const;
  PuzzleTypes &puzzle_type();
  const std::string &title() const;
  std::string &title();
  const std::string &author() const;
  std::string &author();
  const std::string &boxorder() const;
  std::string &boxorder();
  const std::string &goalorder() const;
  std::string &goalorder();
  const std::string &notes() const;
  std::string &notes();
  const std::string &created_at() const;
  std::string &created_at();
  const std::string &updated_at() const;
  std::string &updated_at();
  const Snapshots &snapshots() const;
  Snapshots &snapshots();

  size_t pushers_count() const;
  size_t boxes_count() const;
  size_t goals_count() const;

  std::string reformatted(bool use_visible_floor = false,
                          uint8_t break_long_lines_at = 80, bool rle_encode = false);

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

  } // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
