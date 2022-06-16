#ifndef PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "config.hpp"

#include <memory>

namespace sokoengine {
namespace io {

namespace implementation {
class PuzzleResizer;
class PuzzleParser;
class PuzzlePrinter;
} // namespace implementation

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

  static constexpr bool is_pusher(char ch) {
    return ch == PUSHER || ch == ALT_PUSHER1 || ch == ALT_PUSHER2 ||
           ch == PUSHER_ON_GOAL || ch == ALT_PUSHER_ON_GOAL1 ||
           ch == ALT_PUSHER_ON_GOAL2;
  }

  static constexpr bool is_box(char ch) {
    return ch == BOX || ch == ALT_BOX1 || ch == BOX_ON_GOAL || ch == ALT_BOX_ON_GOAL1;
  }

  static constexpr bool is_goal(char ch) {
    return ch == GOAL || ch == ALT_GOAL1 || ch == BOX_ON_GOAL ||
           ch == ALT_BOX_ON_GOAL1 || ch == PUSHER_ON_GOAL ||
           ch == ALT_PUSHER_ON_GOAL1 || ch == ALT_PUSHER_ON_GOAL2;
  }

  static constexpr bool is_empty_floor(char ch) {
    return ch == FLOOR || ch == VISIBLE_FLOOR || ch == ALT_VISIBLE_FLOOR1;
  }

  static constexpr bool is_wall(char ch) { return ch == WALL; }

  static constexpr bool is_border_element(char ch) {
    return ch == WALL || ch == BOX_ON_GOAL || ch == ALT_BOX_ON_GOAL1;
  }

  static constexpr bool is_puzzle_element(char ch) {
    return is_empty_floor(ch) || is_wall(ch) || is_pusher(ch) || is_box(ch) ||
           is_goal(ch);
  }

  static bool is_board(const std::string &line);
  static bool is_sokoban_plus(const std::string &line);

  virtual ~Puzzle();

  typedef std::unique_ptr<Puzzle> unique_ptr_t;

  static unique_ptr_t instance_from(game::Tessellation tessellation, board_size_t width,
                                    board_size_t height);
  static unique_ptr_t instance_from(game::Tessellation tessellation,
                                    const std::string &board);

  virtual unique_ptr_t clone() const = 0;

  const std::string &title() const;
  std::string &title();
  const std::string &author() const;
  std::string &author();
  const std::string &boxorder() const;
  std::string &boxorder();
  const std::string &goalorder() const;
  std::string &goalorder();
  const Strings &notes() const;
  Strings &notes();

  game::Tessellation tessellation() const;
  CellOrientation cell_orientation(position_t position) const;

  char at(position_t position) const;
  void set_at(position_t position, char c);
  char operator[](position_t position) const;
  void set(position_t position, char c);

  std::string str() const;
  std::string repr() const;

  ///
  /// Formatted string representation of board.
  ///
  std::string to_board_str(bool use_visible_floor = false,
                           bool rle_encode = false) const;

  ///
  /// Original, non-parsed board string.
  ///
  const std::string &board() const;
  void set_board(const std::string &board);

  ///
  /// Internal, parsed board string for debugging purposes.
  ///
  std::string internal_board() const;

  board_size_t width() const;
  board_size_t height() const;
  board_size_t size() const;

  size_t pushers_count() const;
  size_t boxes_count() const;
  size_t goals_count() const;

  void add_row_top();
  void add_row_bottom();
  void add_column_left();
  void add_column_right();

  void remove_row_top();
  void remove_row_bottom();
  void remove_column_left();
  void remove_column_right();

  void trim_left();
  void trim_right();
  void trim_top();
  void trim_bottom();

  void reverse_rows();
  void reverse_columns();

  void resize(board_size_t new_width, board_size_t new_height);
  void resize_and_center(board_size_t new_width, board_size_t new_height);
  void trim();

protected:
  Puzzle(const game::Tessellation &tessellation,
         const implementation::PuzzleResizer &resizer,
         const implementation::PuzzleParser &parser,
         const implementation::PuzzlePrinter &printer, board_size_t width = 0,
         board_size_t height = 0);
  Puzzle(const game::Tessellation &tessellation,
         const implementation::PuzzleResizer &resizer,
         const implementation::PuzzleParser &parser,
         const implementation::PuzzlePrinter &printer, const std::string &board = "");
  Puzzle(const Puzzle &rv);
  Puzzle &operator=(const Puzzle &rv);
  Puzzle(Puzzle &&rv);
  Puzzle &operator=(Puzzle &&rv);

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

namespace implementation {

typedef std::vector<char> parsed_board_t;

void LIBSOKOENGINE_LOCAL _copy(parsed_board_t &parsed_board, board_size_t &width,
                               board_size_t &height, const Strings &strings);

class LIBSOKOENGINE_LOCAL PuzzleResizer {
public:
  virtual ~PuzzleResizer() = default;

  virtual void add_row_top(parsed_board_t &parsed_board, board_size_t &width,
                           board_size_t &height) const;
  virtual void add_row_bottom(parsed_board_t &parsed_board, board_size_t &width,
                              board_size_t &height) const;
  virtual void add_column_left(parsed_board_t &parsed_board, board_size_t &width,
                               board_size_t &height) const;
  virtual void add_column_right(parsed_board_t &parsed_board, board_size_t &width,
                                board_size_t &height) const;

  virtual void remove_row_top(parsed_board_t &parsed_board, board_size_t &width,
                              board_size_t &height) const;
  virtual void remove_row_bottom(parsed_board_t &parsed_board, board_size_t &width,
                                 board_size_t &height) const;
  virtual void remove_column_left(parsed_board_t &parsed_board, board_size_t &width,
                                  board_size_t &height) const;
  virtual void remove_column_right(parsed_board_t &parsed_board, board_size_t &width,
                                   board_size_t &height) const;

  virtual void trim_left(parsed_board_t &parsed_board, board_size_t &width,
                         board_size_t &height) const;
  virtual void trim_right(parsed_board_t &parsed_board, board_size_t &width,
                          board_size_t &height) const;
  virtual void trim_top(parsed_board_t &parsed_board, board_size_t &width,
                        board_size_t &height) const;
  virtual void trim_bottom(parsed_board_t &parsed_board, board_size_t &width,
                           board_size_t &height) const;

  virtual void reverse_rows(parsed_board_t &parsed_board, board_size_t &width,
                            board_size_t &height) const;
  virtual void reverse_columns(parsed_board_t &parsed_board, board_size_t &width,
                               board_size_t &height) const;
};

class LIBSOKOENGINE_LOCAL PuzzleParser {
public:
  virtual ~PuzzleParser() = default;

  virtual Strings parse(const std::string &board) const;
  static size_t calculate_width(const Strings &strings);
  static Strings normalize_width(const Strings &strings, char fill_chr = ' ');
  static Strings cleaned_board_lines(const std::string &line);
};

class LIBSOKOENGINE_LOCAL PuzzlePrinter {
public:
  virtual ~PuzzlePrinter() = default;

  virtual std::string print(const parsed_board_t &parsed_board, board_size_t width,
                            board_size_t height, bool use_visible_floor = false,
                            bool rle_encode = false) const;
};

} // namespace implementation
} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
