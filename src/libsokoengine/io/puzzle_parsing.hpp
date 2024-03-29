#ifndef PUZZLE_PARSING_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define PUZZLE_PARSING_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "characters.hpp"

namespace sokoengine {
namespace implementation {

typedef std::vector<char> parsed_board_t;

void LIBSOKOENGINE_LOCAL _copy(
  parsed_board_t  &parsed_board,
  board_size_t    &width,
  board_size_t    &height,
  const strings_t &strings
);

class LIBSOKOENGINE_LOCAL PuzzleResizer {
public:
  constexpr inline PuzzleResizer() {}

  virtual void add_row_top(
    parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
  ) const;
  virtual void add_row_bottom(
    parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
  ) const;
  virtual void add_column_left(
    parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
  ) const;
  virtual void add_column_right(
    parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
  ) const;

  virtual void remove_row_top(
    parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
  ) const;
  virtual void remove_row_bottom(
    parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
  ) const;
  virtual void remove_column_left(
    parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
  ) const;
  virtual void remove_column_right(
    parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
  ) const;

  virtual void trim_left(
    parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
  ) const;
  virtual void trim_right(
    parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
  ) const;
  virtual void trim_top(
    parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
  ) const;
  virtual void trim_bottom(
    parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
  ) const;

  virtual void reverse_rows(
    parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
  ) const;
  virtual void reverse_columns(
    parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
  ) const;
};

class LIBSOKOENGINE_LOCAL PuzzleParser {
public:
  constexpr inline PuzzleParser() {}

  virtual strings_t parse(const std::string &board) const;
  static size_t     calculate_width(const strings_t &strings);
  static strings_t  normalize_width(const strings_t &strings, char fill_chr = ' ');
  static strings_t  cleaned_board_lines(const std::string &line);
};

class LIBSOKOENGINE_LOCAL PuzzlePrinter {
public:
  constexpr inline PuzzlePrinter() {}

  virtual std::string print(
    const parsed_board_t &parsed_board,
    board_size_t          width,
    board_size_t          height,
    bool                  use_visible_floor = false,
    bool                  rle_encode        = false
  ) const;
};

} // namespace implementation
} // namespace sokoengine

#endif // HEADER_GUARD
