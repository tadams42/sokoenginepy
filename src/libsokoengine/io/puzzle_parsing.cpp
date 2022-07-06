#include "puzzle_parsing.hpp"

#include "puzzle.hpp"
#include "rle.hpp"
#include "tessellation.hpp"

#include <boost/algorithm/string.hpp>

using sokoengine::game::BaseTessellation;
using sokoengine::game::index_1d;
using sokoengine::game::Tessellation;
using sokoengine::implementation::Strings;
using std::string;

namespace sokoengine {
namespace io {
namespace implementation {

void PuzzleResizer::add_row_top(
  parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
) const {
  parsed_board_t old_body   = parsed_board;
  board_size_t   old_height = height;

  height       = height + 1;
  parsed_board = parsed_board_t(width * height, Puzzle::VISIBLE_FLOOR);

  for (board_size_t x = 0; x < width; x++)
    for (board_size_t y = 0; y < old_height; y++)
      parsed_board[index_1d(x, y + 1, width)] = old_body[index_1d(x, y, width)];
}

void PuzzleResizer::add_row_bottom(
  parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
) const {
  parsed_board_t old_body   = parsed_board;
  board_size_t   old_height = height;

  height       = height + 1;
  parsed_board = parsed_board_t(width * height, Puzzle::VISIBLE_FLOOR);

  for (board_size_t x = 0; x < width; x++)
    for (board_size_t y = 0; y < old_height; y++)
      parsed_board[index_1d(x, y, width)] = old_body[index_1d(x, y, width)];
}

void PuzzleResizer::add_column_left(
  parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
) const {
  parsed_board_t old_body  = parsed_board;
  board_size_t   old_width = width;

  width        = width + 1;
  parsed_board = parsed_board_t(width * height, Puzzle::VISIBLE_FLOOR);

  for (board_size_t x = 0; x < old_width; x++)
    for (board_size_t y = 0; y < height; y++)
      parsed_board[index_1d(x + 1, y, width)] = old_body[index_1d(x, y, old_width)];
}

void PuzzleResizer::add_column_right(
  parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
) const {
  parsed_board_t old_body  = parsed_board;
  board_size_t   old_width = width;

  width        = width + 1;
  parsed_board = parsed_board_t(width * height, Puzzle::VISIBLE_FLOOR);

  for (board_size_t x = 0; x < old_width; x++)
    for (board_size_t y = 0; y < height; y++)
      parsed_board[index_1d(x, y, width)] = old_body[index_1d(x, y, old_width)];
}

void PuzzleResizer::remove_row_top(
  parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
) const {
  parsed_board_t old_body = parsed_board;

  height       = height - 1;
  parsed_board = parsed_board_t(width * height, Puzzle::VISIBLE_FLOOR);

  for (board_size_t x = 0; x < width; x++)
    for (board_size_t y = 0; y < height; y++)
      parsed_board[index_1d(x, y, width)] = old_body[index_1d(x, y + 1, width)];
}

void PuzzleResizer::remove_row_bottom(
  parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
) const {
  parsed_board_t old_body = parsed_board;

  height       = height - 1;
  parsed_board = parsed_board_t(width * height, Puzzle::VISIBLE_FLOOR);

  for (board_size_t x = 0; x < width; x++)
    for (board_size_t y = 0; y < height; y++)
      parsed_board[index_1d(x, y, width)] = old_body[index_1d(x, y, width)];
}

void PuzzleResizer::remove_column_left(
  parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
) const {
  parsed_board_t old_body  = parsed_board;
  board_size_t   old_width = width;

  width        = width - 1;
  parsed_board = parsed_board_t(width * height, Puzzle::VISIBLE_FLOOR);

  for (board_size_t x = 0; x < width; x++)
    for (board_size_t y = 0; y < height; y++)
      parsed_board[index_1d(x, y, width)] = old_body[index_1d(x + 1, y, old_width)];
}

void PuzzleResizer::remove_column_right(
  parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
) const {
  parsed_board_t old_body  = parsed_board;
  board_size_t   old_width = width;

  width        = width - 1;
  parsed_board = parsed_board_t(width * height, Puzzle::VISIBLE_FLOOR);

  for (board_size_t x = 0; x < width; x++)
    for (board_size_t y = 0; y < height; y++)
      parsed_board[index_1d(x, y, width)] = old_body[index_1d(x, y, old_width)];
}

void PuzzleResizer::trim_left(
  parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
) const {
  board_size_t amount = width;
  for (board_size_t y = 0; y < height; y++) {
    for (board_size_t x = 0; x < width; x++) {
      bool border_found =
        Puzzle::is_border_element(parsed_board[index_1d(x, y, width)]);
      if (border_found) {
        if (x < amount)
          amount = x;
        break;
      }
    }
  }
  for (board_size_t i = 0; i < amount; i++) {
    remove_column_left(parsed_board, width, height);
  }
}

void PuzzleResizer::trim_right(
  parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
) const {
  reverse_columns(parsed_board, width, height);
  trim_left(parsed_board, width, height);
  reverse_columns(parsed_board, width, height);
}

void PuzzleResizer::trim_top(
  parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
) const {
  board_size_t amount = height;
  for (board_size_t x = 0; x < width; x++) {
    bool border_found = false;
    for (board_size_t y = 0; y < height && !border_found; y++) {
      border_found = Puzzle::is_border_element(parsed_board[index_1d(x, y, width)]);
      if (border_found && y < amount)
        amount = y;
    }
  }
  for (board_size_t i = 0; i < amount; i++) {
    remove_row_top(parsed_board, width, height);
  }
}

void PuzzleResizer::trim_bottom(
  parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
) const {
  reverse_rows(parsed_board, width, height);
  trim_top(parsed_board, width, height);
  reverse_rows(parsed_board, width, height);
}

void PuzzleResizer::reverse_rows(
  parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
) const {
  parsed_board_t old_body = parsed_board;

  for (board_size_t x = 0; x < width; x++)
    for (board_size_t y = 0; y < height; y++)
      parsed_board[index_1d(x, y, width)] =
        old_body[index_1d(x, height - y - 1, width)];
}

void PuzzleResizer::reverse_columns(
  parsed_board_t &parsed_board, board_size_t &width, board_size_t &height
) const {
  parsed_board_t old_body = parsed_board;

  for (board_size_t x = 0; x < width; x++)
    for (board_size_t y = 0; y < height; y++)
      parsed_board[index_1d(x, y, width)] = old_body[index_1d(width - x - 1, y, width)];
}

size_t PuzzleParser::calculate_width(const Strings &strings) {
  size_t width = 0;
  for (auto line : strings)
    if (line.length() > width)
      width = line.length();
  return width;
}

Strings PuzzleParser::normalize_width(const Strings &strings, char fill_chr) {
  size_t  width = calculate_width(strings);
  Strings retv  = strings;
  for (string &line : retv) {
    if (line.length() < width) {
      line.append(width - line.length(), fill_chr);
    }
  }
  return retv;
}

static void trim_R_newlines(std::string &s) {
  s.erase(s.begin(), std::find_if(s.begin(), s.end(), [](unsigned char ch) {
            return ch != '\n';
          }));
  s.erase(
    std::find_if(
      s.rbegin(),
      s.rend(),
      [](unsigned char ch) {
        return ch != '\n';
      }
    ).base(),
    s.end()
  );
}

Strings PuzzleParser::cleaned_board_lines(const std::string &line) {
  if (is_blank(line)) {
    return Strings();
  }
  if (!io::Puzzle::is_board(line)) {
    throw std::invalid_argument("Illegal characters found in board string");
  }
  string data = io::Rle::decode(line);
  trim_R_newlines(data);

  Strings board_lines;
  if (!is_blank(data)) {
    boost::split(board_lines, data, boost::is_any_of("\n"));
    return normalize_width(board_lines);
  }

  return board_lines;
}

Strings PuzzleParser::parse(const string &board) const {
  return cleaned_board_lines(board);
}

string PuzzlePrinter::print(
  const parsed_board_t &parsed_board,
  board_size_t          width,
  board_size_t          height,
  bool                  use_visible_floor,
  bool                  rle_encode
) const {
  Strings retv_list;
  char    floor = use_visible_floor ? Puzzle::VISIBLE_FLOOR : Puzzle::FLOOR;

  for (position_t y = 0; y < height; ++y) {
    string tmp;
    for (position_t x = 0; x != width; ++x) {
      char c = parsed_board[index_1d(x, y, width)];
      if (Puzzle::is_empty_floor(c)) {
        tmp += floor;
      } else {
        tmp += c;
      }
    }
    retv_list.push_back(tmp);
  }

  string retv = boost::join(retv_list, "\n");

  if (rle_encode) {
    retv = Rle::encode(retv);
  }

  return retv;
}

void LIBSOKOENGINE_LOCAL _copy(
  parsed_board_t &parsed_board,
  board_size_t   &width,
  board_size_t   &height,
  const Strings  &strings
) {
  width  = strings.size() > 0 ? strings.front().size() : 0;
  height = strings.size();
  parsed_board.resize(width * height);
  size_t i = 0;
  for (auto row : strings) {
    for (auto c : row) {
      parsed_board[i++] = Puzzle::is_empty_floor(c) ? Puzzle::VISIBLE_FLOOR : c;
    }
  }
}

} // namespace implementation
} // namespace io
} // namespace sokoengine
