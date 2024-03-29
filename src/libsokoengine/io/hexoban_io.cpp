/// @file
#include "hexoban_io.hpp"

#include "game_config.hpp"
#include "puzzle_parsing.hpp"

#include <boost/algorithm/string.hpp>

using sokoengine::implementation::strings_t;
using std::invalid_argument;
using std::make_tuple;
using std::make_unique;
using std::numeric_limits;
using std::pair;
using std::string;
using std::tie;
using std::tuple;

namespace sokoengine {
namespace implementation {

class LIBSOKOENGINE_LOCAL HexobanPuzzleResizer : public PuzzleResizer {
public:
  constexpr inline HexobanPuzzleResizer()
    : PuzzleResizer() {}

  virtual void add_row_top(
    parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
  ) const override;
  virtual void remove_row_top(
    parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
  ) const override;
  virtual void remove_row_bottom(
    parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
  ) const override;
  virtual void reverse_columns(
    parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
  ) const override;
};

class LIBSOKOENGINE_LOCAL HexobanPuzzleParser : public PuzzleParser {
public:
  constexpr inline HexobanPuzzleParser()
    : PuzzleParser() {}

  virtual strings_t parse(const string &board) const override;
};

class LIBSOKOENGINE_LOCAL HexobanPuzzlePrinter : public PuzzlePrinter {
public:
  constexpr inline HexobanPuzzlePrinter()
    : PuzzlePrinter() {}

  virtual string print(
    const parsed_board_t &parsed_board,
    board_size_t          width,
    board_size_t          height,
    bool                  use_visible_floor = false,
    bool                  rle_encode        = false
  ) const override;
};

static constexpr HexobanPuzzleResizer HEX_RESIZER;
static constexpr HexobanPuzzleParser  HEX_PARSER;
static constexpr HexobanPuzzlePrinter HEX_PRINTER;

const PuzzleResizer &HexobanIo::resizer() { return HEX_RESIZER; }

const PuzzleParser &HexobanIo::parser() { return HEX_PARSER; }

const PuzzlePrinter &HexobanIo::printer() { return HEX_PRINTER; }

class LIBSOKOENGINE_LOCAL HexobanTextConverter {
  typedef tuple<strings_t, board_size_t, board_size_t, int8_t, int8_t>
    preparse_results_t;
  typedef tuple<char, board_size_t, board_size_t, int8_t, int8_t>
                            text_cell_position_data_t;
  typedef tuple<bool, bool> text_cell_position_status_t;

public:
  string convert_to_string(
    const parsed_board_t &parsed_board,
    board_size_t          width,
    board_size_t          height,
    bool                  use_visible_floor = false
  ) {
    char floor = use_visible_floor ? Characters::VISIBLE_FLOOR : Characters::FLOOR;

    strings_t retv_list;
    for (position_t row = 0; row < height; row++) {
      string line;
      if (row % 2 != 0) {
        line += floor; // beginning half hex for odd rows
      }
      for (position_t col = 0; col < width; col++) {
        line += floor;

        char board_char = parsed_board[index_1d(col, row, width)];
        if (Characters::is_empty_floor(board_char)) {
          line += floor;
        } else {
          line += board_char;
        }
      }
      retv_list.push_back(line);
    }
    retv_list = PuzzleParser::normalize_width(retv_list, floor);
    if (is_type1(retv_list)) {
      remove_column_right(retv_list);
    }

    return boost::join(retv_list, "\n");
  }

  bool is_type1(const strings_t &list) const {
    position_t rmnf = find_rightmost_non_floor(list);
    if (rmnf != Config::NO_POS) {
      board_size_t y = index_y(rmnf, PuzzleParser::calculate_width(list));
      return y % 2 == 0;
    }
    return false;
  }

  pair<strings_t, bool> convert_to_internal(const string &board) const {
    strings_t    parsed;
    board_size_t height, width;
    int8_t       even_row_x_parity, odd_row_x_parity;

    tie(parsed, width, height, even_row_x_parity, odd_row_x_parity) =
      preparse_board(board);

    strings_t internal_list;

    // Handle empty board
    if (width == 0 || height == 0) {
      return make_pair(strings_t(), true);
    } else if (even_row_x_parity < 0 || odd_row_x_parity < 0) {
      for (board_size_t i = 0; i < height; i++) {
        internal_list.push_back(string(width / 2, Characters::VISIBLE_FLOOR));
      }
      return make_pair(internal_list, true);
    }

    bool layout_ok = true;

    for (board_size_t y = 0; y < height && layout_ok; y++) {
      string internal_line;
      for (board_size_t x = 0; x < width && layout_ok; x++) {
        bool should_copy_cell;

        tie(layout_ok, should_copy_cell) = analyze_text_cell_position(
          make_tuple(parsed[y][x], x, y, odd_row_x_parity, even_row_x_parity)
        );

        if (layout_ok && should_copy_cell)
          internal_line += parsed[y][x];
      }
      if (layout_ok)
        internal_list.push_back(internal_line);
    }

    if (layout_ok)
      internal_list =
        PuzzleParser::normalize_width(internal_list, Characters::VISIBLE_FLOOR);

    return make_pair(internal_list, layout_ok);
  }

  void add_column_left(strings_t &list) const {
    for (string &line : list)
      line.insert(line.cbegin(), Characters::VISIBLE_FLOOR);
  }

  void add_column_right(strings_t &list) const {
    for (string &line : list)
      line.append(1, Characters::VISIBLE_FLOOR);
  }

  void add_row_top(strings_t &list) const {
    list.insert(list.begin(), string(list.front().size(), Characters::VISIBLE_FLOOR));
  }

  void remove_column_right(strings_t &list) const {
    for (string &line : list)
      line.pop_back();
  }

  void reverse_columns(strings_t &list) const {
    for (string &line : list)
      reverse(line.begin(), line.end());
  }

  void remove_row_top(strings_t &list) const { list.erase(list.begin()); }

  void remove_row_bottom(strings_t &list) const { list.pop_back(); }

private:
  text_cell_position_status_t
  analyze_text_cell_position(text_cell_position_data_t position) const {
    char         cell;
    board_size_t x, y;
    int8_t       odd_row_x_parity, even_row_x_parity;
    tie(cell, x, y, odd_row_x_parity, even_row_x_parity) = position;

    int8_t y_parity = y % 2;
    int8_t x_parity = x % 2;

    bool layout_ok = true;
    // Is current cell part of board or only part of textual layout?
    bool is_cell_for_layout;
    bool should_copy_cell;

    // Check if textual encoding (layout) is legal. Positions of all board elements
    // in textual layout depend on position of first non floor element. If that
    // element is (odd column, even row) than all other elements in even rows must
    // be in odd columns. Other cells in even rows must be empty cells and their
    // purpose is to define board textual layout (they are not board elements).
    if (y_parity == 0) { // even rows
      if (x_parity == even_row_x_parity) {
        is_cell_for_layout = false;
      } else {
        // Cell is part of layout, it must be empty
        layout_ok          = Characters::is_empty_floor(cell);
        is_cell_for_layout = true;
      }
    } else {        // odd rows
      if (x == 0) { // row start half hexes are always layout cells
        layout_ok          = Characters::is_empty_floor(cell);
        is_cell_for_layout = true;
      } else {
        if (x_parity == odd_row_x_parity) {
          is_cell_for_layout = false;
        } else {
          // Cell is part of layout, it must be empty
          layout_ok          = Characters::is_empty_floor(cell);
          is_cell_for_layout = true;
        }
      }
    }

    should_copy_cell = layout_ok && !is_cell_for_layout;

    return make_tuple(layout_ok, should_copy_cell);
  }

  preparse_results_t preparse_board(const string &board) const {
    strings_t    parsed;
    board_size_t height = 0, width = 0;

    parsed                   = PuzzleParser::cleaned_board_lines(board);
    height                   = parsed.size();
    width                    = height > 0 ? parsed.front().size() : 0;
    int8_t even_row_x_parity = -1, odd_row_x_parity = -1;

    if (height == 0 || width == 0)
      return make_tuple(parsed, width, height, even_row_x_parity, odd_row_x_parity);

    // Compensate for scheme2
    bool has_non_floor_left_in_odd_row = false;
    for (board_size_t i = 0; i < height && !has_non_floor_left_in_odd_row; ++i) {
      has_non_floor_left_in_odd_row =
        has_non_floor_left_in_odd_row
        || (i % 2 == 1 && !Characters::is_empty_floor(parsed[i][0]));
    }
    if (has_non_floor_left_in_odd_row) {
      add_column_left(parsed);
      width += 1;
    }

    // Calculate parities
    position_t first_cell = find_first_non_floor(parsed);
    if (first_cell != Config::NO_POS) {
      int8_t first_cell_x_parity = index_x(first_cell, width) % 2;
      int8_t first_cell_y_parity = index_y(first_cell, width) % 2;

      if (first_cell_y_parity == 0) {
        even_row_x_parity = first_cell_x_parity;
      } else {
        even_row_x_parity = (first_cell_x_parity + 1) % 2;
      }
      odd_row_x_parity = (even_row_x_parity + 1) % 2;
    }

    return make_tuple(parsed, width, height, even_row_x_parity, odd_row_x_parity);
  }

  position_t find_first_non_floor(const strings_t &list) const {
    strings_t    normalized = HexobanPuzzleParser::normalize_width(list);
    board_size_t height     = normalized.size();
    board_size_t width      = height > 0 ? normalized.front().size() : 0;
    if (height == 0 || width == 0)
      return Config::NO_POS;

    position_t x = 0, y = 0;
    bool       non_floor_found = false;
    for (position_t row = 0; row < height && !non_floor_found; row++) {
      for (position_t col = 0; col < width && !non_floor_found; col++) {
        if (!Characters::is_empty_floor(normalized[row][col]) && (col > x || row > y)) {
          x               = col;
          y               = row;
          non_floor_found = true;
        }
      }
    }
    if (non_floor_found) {
      return index_1d(x, y, width);
    } else {
      return index_1d(1, 0, width); // Empty board, assuming scheme1
    }
  }

  position_t find_rightmost_non_floor(const strings_t &strings) const {
    auto rightmost_finder =
      [](const strings_t &strings, int8_t row_parity) -> position_t {
      position_t   retv       = Config::NO_POS;
      bool         cell_found = false;
      board_size_t height     = strings.size();
      board_size_t width      = strings.front().size();
      position_t   x = 0, y = 0;
      for (position_t row = row_parity % 2; row < height; row += 2) {
        for (position_t col = 0; col < width; col++) {
          if (!Characters::is_empty_floor(strings[row][col])) {
            cell_found = true;
            if (col > x || (col >= x && row > y)) {
              x = col;
              y = row;
            }
          }
        }
      }
      if (cell_found) {
        retv = index_1d(x, y, width);
      }
      return retv;
    };

    strings_t    normalized = HexobanPuzzleParser::normalize_width(strings);
    board_size_t height     = normalized.size();
    board_size_t width      = height > 0 ? normalized.front().size() : 0;
    if (height == 0 || width == 0) {
      return numeric_limits<position_t>::max();
    }

    position_t rightmost_in_even_rows = rightmost_finder(normalized, 0);
    position_t rightmost_in_odd_rows  = rightmost_finder(normalized, 1);

    if (rightmost_in_even_rows == numeric_limits<position_t>::max() || rightmost_in_odd_rows == numeric_limits<position_t>::max()) { // Empty board
      return index_1d(0, 0, width);
    }

    position_t odd_x  = index_x(rightmost_in_odd_rows, width);
    position_t odd_y  = index_y(rightmost_in_odd_rows, width);
    position_t even_x = index_x(rightmost_in_even_rows, width);
    position_t even_y = index_y(rightmost_in_even_rows, width);

    if (odd_x > even_x) {
      return rightmost_in_odd_rows;
    } else if (even_x > odd_x) {
      return rightmost_in_even_rows;
    } else {
      return (odd_y >= even_y ? rightmost_in_odd_rows : rightmost_in_even_rows);
    }
  }

  bool is_type2(const strings_t &strings) const { return !is_type1(strings); }
};

void HexobanPuzzleResizer::reverse_columns(
  parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
) const {
  HexobanTextConverter converter;

  strings_t printed_board;
  boost::split(
    printed_board,
    converter.convert_to_string(parsed_board, width, height, true),
    boost::is_any_of("\n")
  );

  if (converter.is_type1(printed_board))
    converter.add_column_left(printed_board);
  else
    converter.add_column_right(printed_board);

  converter.reverse_columns(printed_board);
  converter.remove_column_right(printed_board);

  strings_t new_parsed_board =
    converter.convert_to_internal(boost::join(printed_board, "\n")).first;
  _copy(parsed_board, width, height, new_parsed_board);
}

void HexobanPuzzleResizer::add_row_top(
  parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
) const {
  HexobanTextConverter converter;

  strings_t printed_board;
  boost::split(
    printed_board,
    converter.convert_to_string(parsed_board, width, height, true),
    boost::is_any_of("\n")
  );

  converter.add_row_top(printed_board);

  strings_t new_parsed_board =
    converter.convert_to_internal(boost::join(printed_board, "\n")).first;
  _copy(parsed_board, width, height, new_parsed_board);
}

void HexobanPuzzleResizer::remove_row_top(
  parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
) const {
  HexobanTextConverter converter;

  strings_t printed_board;
  boost::split(
    printed_board,
    converter.convert_to_string(parsed_board, width, height, true),
    boost::is_any_of("\n")
  );

  converter.remove_row_top(printed_board);

  strings_t new_parsed_board =
    converter.convert_to_internal(boost::join(printed_board, "\n")).first;
  _copy(parsed_board, width, height, new_parsed_board);
}

void HexobanPuzzleResizer::remove_row_bottom(
  parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
) const {
  HexobanTextConverter converter;

  strings_t printed_board;
  boost::split(
    printed_board,
    converter.convert_to_string(parsed_board, width, height, true),
    boost::is_any_of("\n")
  );

  converter.remove_row_bottom(printed_board);

  strings_t new_parsed_board =
    converter.convert_to_internal(boost::join(printed_board, "\n")).first;
  _copy(parsed_board, width, height, new_parsed_board);
}

strings_t HexobanPuzzleParser::parse(const string &board) const {
  auto result = HexobanTextConverter().convert_to_internal(board);

  if (result.second)
    return result.first;

  throw invalid_argument(
    "String can't be parsed to HexobanPuzzle. Probable cause is invalid "
    "text layout - there are either missing or misaligned filler floor "
    "characters."
  );
}

string HexobanPuzzlePrinter::print(
  const parsed_board_t &parsed_board,
  board_size_t          width,
  board_size_t          height,
  bool                  use_visible_floor,
  bool                  rle_encode
) const {
  string retv = HexobanTextConverter().convert_to_string(
    parsed_board, width, height, use_visible_floor
  );

  if (rle_encode) {
    retv = io::Rle::encode(retv);
  }

  return retv;
}

} // namespace implementation
} // namespace sokoengine
