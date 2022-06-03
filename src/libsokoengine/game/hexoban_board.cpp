#include "hexoban_board.hpp"
#include "atomic_move.hpp"
#include "board_cell.hpp"
#include "hexoban_tessellation.hpp"
#include "sokoban_board.hpp"
#include "puzzle.hpp"
#include "utilities.hpp"

#include <algorithm>
#include <functional>

#include <boost/algorithm/string.hpp>

using namespace std;
using namespace boost;

namespace sokoengine {
namespace game {

HexobanBoard::HexobanBoard() : HexobanBoard(0, 0) {}

HexobanBoard::HexobanBoard(board_size_t width, board_size_t height)
  : VariantBoard(Tessellation::HEXOBAN, width, height) {}

HexobanBoard::HexobanBoard(const string &src)
  : VariantBoard(Tessellation::HEXOBAN, src) {}

HexobanBoard::HexobanBoard(const HexobanBoard &rv) : VariantBoard(rv) {}

HexobanBoard &HexobanBoard::operator=(const HexobanBoard &rv) {
  if (this != &rv) VariantBoard::operator=(rv);
  return *this;
}

HexobanBoard::HexobanBoard(HexobanBoard &&) = default;

HexobanBoard &HexobanBoard::operator=(HexobanBoard &&) = default;

HexobanBoard::~HexobanBoard() = default;

HexobanBoard::unique_ptr_t HexobanBoard::create_clone() const {
  return make_unique<HexobanBoard>(*this);
}

namespace implementation {

class LIBSOKOENGINE_LOCAL HexobanTextConverter {
  typedef tuple<Strings, board_size_t, board_size_t, int8_t, int8_t>
    preparse_results_t;
  typedef tuple<char, board_size_t, board_size_t, int8_t, int8_t>
    text_cell_position_data_t;
  typedef tuple<bool, bool> text_cell_position_status_t;

public:
  pair<Strings, bool> convert_to_internal(const string &board_str) const {
    Strings parsed;
    board_size_t height, width;
    int8_t even_row_x_parity, odd_row_x_parity;

    tie(parsed, width, height, even_row_x_parity, odd_row_x_parity) =
      preparse_board(board_str);

    Strings internal_list;

    // Handle empty board
    if (width == 0 || height == 0) {
      return make_pair(Strings(), true);
    } else if (even_row_x_parity < 0 || odd_row_x_parity < 0) {
      for (board_size_t i = 0; i < height; ++i) {
        internal_list.push_back(string(width / 2, io::Puzzle::VISIBLE_FLOOR));
      }
      return make_pair(internal_list, true);
    }

    bool layout_ok = true;

    for (board_size_t y = 0; y < height && layout_ok; ++y) {
      string internal_line;
      for (board_size_t x = 0; x < width && layout_ok; ++x) {
        bool should_copy_cell;

        tie(layout_ok, should_copy_cell) = analyze_text_cell_position(
          make_tuple(parsed[y][x], x, y, odd_row_x_parity, even_row_x_parity));

        if (layout_ok && should_copy_cell) internal_line += parsed[y][x];
      }
      if (layout_ok) internal_list.push_back(internal_line);
    }

    if (layout_ok) HexobanBoardParser::normalize_width(internal_list);

    return make_pair(internal_list, layout_ok);
  }

  string convert_to_string(const VariantBoard &board, bool use_visible_floor = false) {
    char floor_character = BoardCell(io::Puzzle::FLOOR).to_str(use_visible_floor);
    Strings retv_list;
    const board_size_t height = board.height();
    const board_size_t width = board.width();
    for (position_t row = 0; row < height; ++row) {
      string tmp;
      if (row % 2 != 0) {
        tmp += floor_character; // beginning half hex for odd rows
      }
      for (position_t col = 0; col < width; ++col) {
        tmp += floor_character;
        tmp += board[index_1d(col, row, width)].to_str(use_visible_floor);
      }
      retv_list.push_back(tmp);
    }
    retv_list = HexobanBoardParser::normalize_width(retv_list, floor_character);
    if (is_type1(retv_list)) { remove_column_right(retv_list); }

    string retv = join(retv_list, "\n");

    return retv;
  }

  bool is_type1(const VariantBoard &board) const {
    Strings tmp = HexobanBoardParser::cleaned_board_lines(board.str());
    return is_type1(tmp);
  }

private:
  text_cell_position_status_t
  analyze_text_cell_position(text_cell_position_data_t position) const {
    char cell;
    board_size_t x, y;
    int8_t odd_row_x_parity, even_row_x_parity;
    tie(cell, x, y, odd_row_x_parity, even_row_x_parity) = position;

    int8_t y_parity = y % 2;
    int8_t x_parity = x % 2;

    bool layout_ok = true;
    bool is_cell_for_layout; // Is current cell part of board or only part of
                             // textual layout?
    bool should_copy_cell;

    // Check if textual encoding (layout) is legal. Positions of all board elements in
    // textual layout depend on position of first non floor element. If that element is
    // (odd column, even row) than all other elements in even rows must be in odd
    // columns. Other cells in even rows must be empty cells and their purpose is to
    // define board textual layout (they are not board elements).
    if (y_parity == 0) { // even rows
      if (x_parity == even_row_x_parity) {
        is_cell_for_layout = false;
      } else {
        // Cell is part of layout, it must be empty
        layout_ok = io::Puzzle::is_empty_floor(cell);
        is_cell_for_layout = true;
      }
    } else {        // odd rows
      if (x == 0) { // row start half hexes are always layout cells
        layout_ok = io::Puzzle::is_empty_floor(cell);
        is_cell_for_layout = true;
      } else {
        if (x_parity == odd_row_x_parity) {
          is_cell_for_layout = false;
        } else {
          // Cell is part of layout, it must be empty
          layout_ok = io::Puzzle::is_empty_floor(cell);
          is_cell_for_layout = true;
        }
      }
    }

    should_copy_cell = layout_ok && !is_cell_for_layout;

    // cout << "cell[" << y << "][" << x << "](" << cell << "): layout_ok: " <<
    // layout_ok << " should_copy: " << should_copy_cell; cout << " x_parity: " <<
    // x_parity << " y_parity: " << y_parity << " is_cell_for_layout: " <<
    // is_cell_for_layout << endl;

    return make_tuple(layout_ok, should_copy_cell);
  }

  preparse_results_t preparse_board(const string &board_string) const {
    Strings parsed;
    board_size_t height = 0, width = 0;

    parsed = HexobanBoardParser::cleaned_board_lines(board_string);
    height = parsed.size();
    width = height > 0 ? parsed.front().size() : 0;
    int8_t even_row_x_parity = -1, odd_row_x_parity = -1;

    if (height == 0 || width == 0)
      return make_tuple(parsed, width, height, even_row_x_parity, odd_row_x_parity);

    // Compensate for scheme2
    bool has_non_floor_left_in_odd_row = false;
    for (board_size_t i = 0; i < height && !has_non_floor_left_in_odd_row; ++i) {
      has_non_floor_left_in_odd_row =
        has_non_floor_left_in_odd_row ||
        (i % 2 == 1 && !io::Puzzle::is_empty_floor(parsed[i][0]));
    }
    if (has_non_floor_left_in_odd_row) {
      for (string &line : parsed)
        line.insert(line.begin(), io::Puzzle::FLOOR);
      width += 1;
    }

    position_t first_cell = find_first_non_floor(parsed);
    if (first_cell <= MAX_POS) {
      int8_t first_cell_x_parity = X(first_cell, width) % 2;
      int8_t first_cell_y_parity = Y(first_cell, width) % 2;

      if (first_cell_y_parity == 0) {
        even_row_x_parity = first_cell_x_parity;
      } else {
        even_row_x_parity = (first_cell_x_parity + 1) % 2;
      }
      odd_row_x_parity = (even_row_x_parity + 1) % 2;
    }

    // cout << "Source: " << endl << board_string << endl << "Parsed: " << endl;
    // copy(parsed.begin(), parsed.end(), ostream_iterator<string>(cout, "\n"));
    // cout << "\nParams: w:" << width << " h:" << height << " erxp:" <<
    // even_row_x_parity << " orxp:" << odd_row_x_parity << endl << endl;

    return make_tuple(parsed, width, height, even_row_x_parity, odd_row_x_parity);
  }

  void remove_column_right(Strings &list) const {
    for (string &line : list)
      line.pop_back();
  }

  position_t find_first_non_floor(const Strings &list) const {
    position_t retv = numeric_limits<position_t>::max();
    Strings normalized = HexobanBoardParser::normalize_width(list);
    board_size_t height = normalized.size();
    board_size_t width = height > 0 ? normalized.front().size() : 0;
    if (height == 0 || width == 0) return retv;

    position_t x = 0, y = 0;
    bool non_floor_found = false;
    for (position_t row = 0; row < height && !non_floor_found; ++row) {
      for (position_t col = 0; col < width && !non_floor_found; ++col) {
        if (!io::Puzzle::is_empty_floor(normalized[row][col]) && (col > x || row > y)) {
          x = col;
          y = row;
          non_floor_found = true;
        }
      }
    }
    if (non_floor_found) {
      retv = index_1d(x, y, width);
    } else {
      retv = index_1d(1, 0, width); // Empty board, assuming scheme1
    }
    return retv;
  }

  position_t find_rightmost_non_floor(const Strings &list) const {
    auto rightmost_finder = [](const Strings &list,
                               int8_t row_parity) -> position_t {
      position_t retv = numeric_limits<position_t>::max();
      bool cell_found = false;
      board_size_t height = list.size();
      board_size_t width = list.front().size();
      position_t x = 0, y = 0;
      for (position_t row = row_parity % 2; row < height; row += 2) {
        for (position_t col = 0; col < width; ++col) {
          if (!io::Puzzle::is_empty_floor(list[row][col])) {
            cell_found = true;
            if (col > x || (col >= x && row > y)) {
              x = col;
              y = row;
            }
          }
        }
      }
      if (cell_found) { retv = index_1d(x, y, width); }
      return retv;
    };

    Strings normalized = HexobanBoardParser::normalize_width(list);
    board_size_t height = normalized.size();
    board_size_t width = height > 0 ? normalized.front().size() : 0;
    if (height == 0 || width == 0) { return numeric_limits<position_t>::max(); }

    position_t rightmost_in_even_rows = rightmost_finder(normalized, 0);
    position_t rightmost_in_odd_rows = rightmost_finder(normalized, 1);

    if (rightmost_in_even_rows < 0 || rightmost_in_odd_rows < 0) { // Empty board
      return index_1d(0, 0, width);
    }

    position_t retv;
    position_t odd_x = X(rightmost_in_odd_rows, width);
    position_t odd_y = Y(rightmost_in_odd_rows, width);
    position_t even_x = X(rightmost_in_even_rows, width);
    position_t even_y = Y(rightmost_in_even_rows, width);

    if (odd_x > even_x) {
      retv = rightmost_in_odd_rows;
    } else if (even_x > odd_x) {
      retv = rightmost_in_even_rows;
    } else {
      retv = odd_y >= even_y ? rightmost_in_odd_rows : rightmost_in_even_rows;
    }
    return retv;
  }

  bool is_type1(const Strings &list) const {
    position_t rmnf = find_rightmost_non_floor(list);
    if (rmnf <= MAX_POS) {
      board_size_t y = Y(rmnf, HexobanBoardParser::calculate_width(list));
      return y % 2 == 0;
    }
    return false;
  }

  bool is_type2(const Strings &list) const { return !is_type1(list); }
};

void HexobanBoardResizer::reverse_columns(VariantBoard &board,
                                          bool reconfigure_edges) const {
  HexobanTextConverter converter;
  SokobanBoard tmp(converter.convert_to_string(board));

  auto resizer = tmp.tessellation().resizer();
  if (converter.is_type1(board))
    resizer.add_column_left(tmp, false);
  else
    resizer.add_column_right(tmp, false);

  resizer.reverse_columns(tmp, false);
  resizer.remove_column_right(tmp, false);

  reinit(board, tmp.str(), reconfigure_edges);
}

void HexobanBoardResizer::add_row_top(VariantBoard &board,
                                      bool reconfigure_edges) const {
  HexobanTextConverter converter;
  SokobanBoard tmp(converter.convert_to_string(board));
  tmp.tessellation().resizer().add_row_top(tmp, false);
  reinit(board, tmp.str(), reconfigure_edges);
}

void HexobanBoardResizer::remove_row_top(VariantBoard &board,
                                         bool reconfigure_edges) const {
  HexobanTextConverter converter;
  SokobanBoard tmp(converter.convert_to_string(board));
  tmp.tessellation().resizer().remove_row_top(tmp, false);
  reinit(board, tmp.str(), reconfigure_edges);
}

void HexobanBoardResizer::remove_row_bottom(VariantBoard &board,
                                            bool reconfigure_edges) const {
  HexobanTextConverter converter;
  SokobanBoard tmp(converter.convert_to_string(board));
  tmp.tessellation().resizer().remove_row_bottom(tmp, false);
  reinit(board, tmp.str(), reconfigure_edges);
}

Strings HexobanBoardParser::parse(const string &board_str) const {
  auto result = HexobanTextConverter().convert_to_internal(board_str);
  if (result.second) return result.first;
  throw std::invalid_argument(
    "String can't be converted to HexobanBoard. Probable cause is invalid text layout"
    "meaning either missing or misaligned filler spaces.");
}

string HexobanBoardPrinter::print(const VariantBoard &board,
                                  bool use_visible_floor) const {
  return HexobanTextConverter().convert_to_string(board, use_visible_floor);
}

} // namespace implementation

} // namespace game
} // namespace sokoengine
