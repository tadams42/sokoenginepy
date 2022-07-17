#ifndef CHARACTERS_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define CHARACTERS_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "puzzle.hpp"
#include "rle.hpp"
#include "snapshot.hpp"

namespace sokoengine {
namespace implementation {

///
/// Test if line is zero length or contains only spaces.
///
bool LIBSOKOENGINE_API is_blank(const std::string &line);

typedef std::vector<std::string> Strings;

class LIBSOKOENGINE_LOCAL Characters {
public:
  static constexpr char WALL                = Puzzle::WALL;
  static constexpr char PUSHER              = Puzzle::PUSHER;
  static constexpr char PUSHER_ON_GOAL      = Puzzle::PUSHER_ON_GOAL;
  static constexpr char BOX                 = Puzzle::BOX;
  static constexpr char BOX_ON_GOAL         = Puzzle::BOX_ON_GOAL;
  static constexpr char GOAL                = Puzzle::GOAL;
  static constexpr char FLOOR               = Puzzle::FLOOR;
  static constexpr char VISIBLE_FLOOR       = Puzzle::VISIBLE_FLOOR;
  static constexpr char ALT_PUSHER1         = 'p';
  static constexpr char ALT_PUSHER2         = 'm';
  static constexpr char ALT_PUSHER_ON_GOAL1 = 'P';
  static constexpr char ALT_PUSHER_ON_GOAL2 = 'M';
  static constexpr char ALT_BOX1            = 'b';
  static constexpr char ALT_BOX_ON_GOAL1    = 'B';
  static constexpr char ALT_GOAL1           = 'o';
  static constexpr char ALT_VISIBLE_FLOOR1  = '_';

  static constexpr bool is_pusher(char ch) {
    return ch == PUSHER || ch == ALT_PUSHER1 || ch == ALT_PUSHER2
        || ch == PUSHER_ON_GOAL || ch == ALT_PUSHER_ON_GOAL1
        || ch == ALT_PUSHER_ON_GOAL2;
  }

  static constexpr bool is_box(char ch) {
    return ch == BOX || ch == ALT_BOX1 || ch == BOX_ON_GOAL || ch == ALT_BOX_ON_GOAL1;
  }

  static constexpr bool is_goal(char ch) {
    return ch == GOAL || ch == ALT_GOAL1 || ch == BOX_ON_GOAL || ch == ALT_BOX_ON_GOAL1
        || ch == PUSHER_ON_GOAL || ch == ALT_PUSHER_ON_GOAL1
        || ch == ALT_PUSHER_ON_GOAL2;
  }

  static constexpr bool is_empty_floor(char ch) {
    return ch == FLOOR || ch == VISIBLE_FLOOR || ch == ALT_VISIBLE_FLOOR1;
  }

  static constexpr bool is_wall(char ch) { return ch == WALL; }

  static constexpr bool is_border_element(char ch) {
    return ch == WALL || ch == BOX_ON_GOAL || ch == ALT_BOX_ON_GOAL1;
  }

  static constexpr bool is_puzzle_element(char ch) {
    return is_empty_floor(ch) || is_wall(ch) || is_pusher(ch) || is_box(ch)
        || is_goal(ch);
  }

  ///
  /// Checks if line contains only characters legal in textual representation of
  /// boards.
  ///
  /// Doesn't check if it actually contains legal board, it only checks that there are
  /// no illegal characters.
  ///
  static bool is_board(const std::string &line);
  static bool is_sokoban_plus(const std::string &line);

  static constexpr char l = Snapshot::l;
  static constexpr char u = Snapshot::u;
  static constexpr char r = Snapshot::r;
  static constexpr char d = Snapshot::d;
  static constexpr char L = Snapshot::L;
  static constexpr char U = Snapshot::U;
  static constexpr char R = Snapshot::R;
  static constexpr char D = Snapshot::D;
  static constexpr char w = Snapshot::w;
  static constexpr char W = Snapshot::W;
  static constexpr char e = Snapshot::e;
  static constexpr char E = Snapshot::E;
  static constexpr char n = Snapshot::n;
  static constexpr char N = Snapshot::N;
  static constexpr char s = Snapshot::s;
  static constexpr char S = Snapshot::S;

  static constexpr char JUMP_BEGIN          = Snapshot::JUMP_BEGIN;
  static constexpr char JUMP_END            = Snapshot::JUMP_END;
  static constexpr char PUSHER_CHANGE_BEGIN = Snapshot::PUSHER_CHANGE_BEGIN;
  static constexpr char PUSHER_CHANGE_END   = Snapshot::PUSHER_CHANGE_END;
  static constexpr char CURRENT_POSITION_CH = Snapshot::CURRENT_POSITION_CH;

  static constexpr bool is_move_step(char ch) {
    return ch == l || ch == u || ch == r || ch == d || ch == w || ch == e || ch == n
        || ch == s;
  }

  static constexpr bool is_push_step(char ch) {
    return ch == L || ch == U || ch == R || ch == D || ch == W || ch == E || ch == N
        || ch == S;
  }

  static constexpr bool is_pusher_step(char ch) {
    return is_move_step(ch) || is_push_step(ch);
  }

  static constexpr bool is_marker(char ch) {
    return ch == JUMP_BEGIN || ch == JUMP_END || ch == PUSHER_CHANGE_BEGIN
        || ch == PUSHER_CHANGE_END || ch == CURRENT_POSITION_CH;
  }

  static bool is_snapshot(const std::string &line);

  static constexpr char RLE_GROUP_START = Rle::GROUP_START;
  static constexpr char RLE_GROUP_END   = Rle::GROUP_END;
  static constexpr char RLE_EOL         = Rle::EOL;
};

} // namespace implementation
} // namespace sokoengine

#endif // HEADER_GUARD
