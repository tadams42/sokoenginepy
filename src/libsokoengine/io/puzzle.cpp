#include "puzzle.hpp"

#include "rle.hpp"
#include "tessellation.hpp"

#include "hexoban.hpp"
#include "octoban.hpp"
#include "sokoban.hpp"
#include "trioban.hpp"

#include <boost/algorithm/string.hpp>

using namespace std;

namespace sokoengine {
namespace io {

using game::BaseTessellation;
using game::index_1d;
using game::Tessellation;
using implementation::_copy;
using implementation::parsed_board_t;
using implementation::PuzzleParser;
using implementation::PuzzlePrinter;
using implementation::PuzzleResizer;

class LIBSOKOENGINE_LOCAL Puzzle::PIMPL {
public:
  string m_title;
  string m_author;
  string m_boxorder;
  string m_goalorder;
  Strings m_notes;

  board_size_t m_width = 0;
  board_size_t m_height = 0;
  bool m_was_parsed = false;
  string m_original_board;
  parsed_board_t m_parsed_board;

  Tessellation m_tessellation;

  // Non-owned ptr
  const PuzzleResizer *m_resizer = nullptr;
  // Non-owned ptr
  const PuzzleParser *m_parser = nullptr;
  // Non-owned ptr
  const PuzzlePrinter *m_printer = nullptr;

  PIMPL(const Tessellation &tessellation, const PuzzleResizer &resizer,
        const PuzzleParser &parser, const PuzzlePrinter &printer, const string &board)
    : m_width(0),
      m_height(0),
      m_was_parsed(false),
      m_original_board(board),
      m_tessellation(tessellation),
      m_resizer(&resizer),
      m_parser(&parser),
      m_printer(&printer) {
    if (!Puzzle::is_board(m_original_board)) {
      throw std::invalid_argument("Invalid characters in board string!");
    }
  }

  PIMPL(const Tessellation &tessellation, const PuzzleResizer &resizer,
        const PuzzleParser &parser, const PuzzlePrinter &printer, board_size_t width,
        board_size_t height)
    : m_width(width),
      m_height(height),
      m_was_parsed(true),
      m_parsed_board(width * height, Puzzle::VISIBLE_FLOOR),
      m_tessellation(tessellation),
      m_resizer(&resizer),
      m_parser(&parser),
      m_printer(&printer) {}

  PIMPL(const PIMPL &rv) = default;
  PIMPL &operator=(const PIMPL &rv) = default;
  PIMPL(PIMPL &&rv) = default;
  PIMPL &operator=(PIMPL &&rv) = default;
  ~PIMPL() = default;

  void reparse() {
    if (!is_blank(m_original_board)) {
      Strings board_rows = m_parser->parse(m_original_board);
      _copy(m_parsed_board, m_width, m_height, board_rows);
    } else {
      m_height = 0;
      m_width = 0;
      m_parsed_board = parsed_board_t(m_height * m_width, Puzzle::VISIBLE_FLOOR);
    }
    m_was_parsed = true;
  }

  void reparse_if_not_parsed() {
    if (!m_was_parsed) reparse();
  }
};

Puzzle::Puzzle(const Tessellation &tessellation, const PuzzleResizer &resizer,
               const PuzzleParser &parser, const PuzzlePrinter &printer,
               const string &board)
  : m_impl(make_unique<PIMPL>(tessellation, resizer, parser, printer, board)) {}

Puzzle::Puzzle(const Tessellation &tessellation, const PuzzleResizer &resizer,
               const PuzzleParser &parser, const PuzzlePrinter &printer,
               board_size_t width, board_size_t height)
  : m_impl(make_unique<PIMPL>(tessellation, resizer, parser, printer, width, height)) {}

Puzzle::Puzzle(const Puzzle &rv) : m_impl(make_unique<PIMPL>(*rv.m_impl)) {}

Puzzle &Puzzle::operator=(const Puzzle &rv) {
  if (this != &rv) m_impl = make_unique<PIMPL>(*rv.m_impl);
  return *this;
}

Puzzle::Puzzle(Puzzle &&rv) = default;

Puzzle &Puzzle::operator=(Puzzle &&rv) = default;

Puzzle::~Puzzle() = default;

const string &Puzzle::title() const { return m_impl->m_title; }
string &Puzzle::title() { return m_impl->m_title; }

const string &Puzzle::author() const { return m_impl->m_author; }
string &Puzzle::author() { return m_impl->m_author; }

const string &Puzzle::boxorder() const { return m_impl->m_boxorder; }
string &Puzzle::boxorder() { return m_impl->m_boxorder; }

const string &Puzzle::goalorder() const { return m_impl->m_goalorder; }
string &Puzzle::goalorder() { return m_impl->m_goalorder; }

const Strings &Puzzle::notes() const { return m_impl->m_notes; }
Strings &Puzzle::notes() { return m_impl->m_notes; }

Tessellation Puzzle::tessellation() const { return m_impl->m_tessellation; }

CellOrientation Puzzle::cell_orientation(position_t position) const {
  return BaseTessellation::instance(m_impl->m_tessellation)
    .cell_orientation(position, width(), height());
}

char Puzzle::at(position_t position) const {
  m_impl->reparse_if_not_parsed();
  return m_impl->m_parsed_board.at(position);
}

void Puzzle::set_at(position_t position, char c) {
  m_impl->reparse_if_not_parsed();
  if (!is_puzzle_element(c)) {
    throw std::invalid_argument(string("Not a game character: '") + c + "'!");
  }
  m_impl->m_parsed_board.at(position) = c;
}

char Puzzle::operator[](position_t position) const {
  m_impl->reparse_if_not_parsed();
  return m_impl->m_parsed_board[position];
}

void Puzzle::set(position_t position, char c) {
  m_impl->reparse_if_not_parsed();
  if (!is_puzzle_element(c)) {
    throw std::invalid_argument(string("Not a game character: '") + c + "'!");
  }
  m_impl->m_parsed_board[position] = c;
}

string Puzzle::to_board_str(bool use_visible_floor, bool rle_encode) const {
  m_impl->reparse_if_not_parsed();
  return m_impl->m_printer->print(m_impl->m_parsed_board, m_impl->m_width,
                                  m_impl->m_height, use_visible_floor, rle_encode);
}

const string &Puzzle::board() const { return m_impl->m_original_board; }

void Puzzle::set_board(const string &board) {
  if (!is_board(board))
    throw std::invalid_argument("Invalid characters in board string!");
  m_impl->m_original_board = board;
  m_impl->m_was_parsed = false;
}

string Puzzle::internal_board() const {
  m_impl->reparse_if_not_parsed();
  return string(m_impl->m_parsed_board.cbegin(), m_impl->m_parsed_board.cend());
}

string Puzzle::str() const { return to_board_str(true); }

string Puzzle::repr() const {
  string klass_name = "Puzzle";
  switch (m_impl->m_tessellation) {
  case Tessellation::SOKOBAN:
    klass_name = "SokobanPuzzle";
    break;
  case Tessellation::HEXOBAN:
    klass_name = "HexobanPuzzle";
    break;
  case Tessellation::TRIOBAN:
    klass_name = "TriobanPuzzle";
    break;
  case Tessellation::OCTOBAN:
    klass_name = "OctobanPuzzle";
    break;
    // Do not handle default, let compiler generate warning when another tessellation
    // is added...
  }

  Strings board_lines;
  string tmp = to_board_str(true);
  boost::split(board_lines, tmp, boost::is_any_of("\n"));

  for (string &line : board_lines)
    line = "    '" + line + "'";

  return klass_name + "(board='\\n'.join([\n" + boost::join(board_lines, ",\n") +
         "\n]))";
}

board_size_t Puzzle::width() const {
  m_impl->reparse_if_not_parsed();
  return m_impl->m_width;
}

board_size_t Puzzle::height() const {
  m_impl->reparse_if_not_parsed();
  return m_impl->m_height;
}

board_size_t Puzzle::size() const {
  m_impl->reparse_if_not_parsed();
  return m_impl->m_width * m_impl->m_height;
}

size_t Puzzle::pushers_count() const {
  return count_if(m_impl->m_original_board.begin(), m_impl->m_original_board.end(),
                  [](char c) { return Puzzle::is_pusher(c); });
}

size_t Puzzle::boxes_count() const {
  return count_if(m_impl->m_original_board.begin(), m_impl->m_original_board.end(),
                  [](char c) { return Puzzle::is_box(c); });
}

size_t Puzzle::goals_count() const {
  return count_if(m_impl->m_original_board.begin(), m_impl->m_original_board.end(),
                  [](char c) { return Puzzle::is_goal(c); });
}

void Puzzle::add_row_top() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->add_row_top(m_impl->m_parsed_board, m_impl->m_width,
                                 m_impl->m_height);
}

void Puzzle::add_row_bottom() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->add_row_bottom(m_impl->m_parsed_board, m_impl->m_width,
                                    m_impl->m_height);
}

void Puzzle::add_column_left() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->add_column_left(m_impl->m_parsed_board, m_impl->m_width,
                                     m_impl->m_height);
}

void Puzzle::add_column_right() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->add_column_right(m_impl->m_parsed_board, m_impl->m_width,
                                      m_impl->m_height);
}

void Puzzle::remove_row_top() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->remove_row_top(m_impl->m_parsed_board, m_impl->m_width,
                                    m_impl->m_height);
}

void Puzzle::remove_row_bottom() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->remove_row_bottom(m_impl->m_parsed_board, m_impl->m_width,
                                       m_impl->m_height);
}

void Puzzle::remove_column_left() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->remove_column_left(m_impl->m_parsed_board, m_impl->m_width,
                                        m_impl->m_height);
}

void Puzzle::remove_column_right() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->remove_column_right(m_impl->m_parsed_board, m_impl->m_width,
                                         m_impl->m_height);
}

void Puzzle::trim_left() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->trim_left(m_impl->m_parsed_board, m_impl->m_width,
                               m_impl->m_height);
}

void Puzzle::trim_right() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->trim_right(m_impl->m_parsed_board, m_impl->m_width,
                                m_impl->m_height);
}

void Puzzle::trim_top() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->trim_top(m_impl->m_parsed_board, m_impl->m_width,
                              m_impl->m_height);
}

void Puzzle::trim_bottom() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->trim_bottom(m_impl->m_parsed_board, m_impl->m_width,
                                 m_impl->m_height);
}

void Puzzle::reverse_rows() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->reverse_rows(m_impl->m_parsed_board, m_impl->m_width,
                                  m_impl->m_height);
}

void Puzzle::reverse_columns() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->reverse_columns(m_impl->m_parsed_board, m_impl->m_width,
                                     m_impl->m_height);
}

void Puzzle::resize(board_size_t new_width, board_size_t new_height) {
  board_size_t old_width = width();
  board_size_t old_height = height();

  if (new_height != old_height) {
    if (new_height > old_height) {
      board_size_t amount = new_height - old_height;
      for (board_size_t i = 0; i < amount; i++)
        m_impl->m_resizer->add_row_bottom(m_impl->m_parsed_board, m_impl->m_width,
                                          m_impl->m_height);
    } else {
      board_size_t amount = old_height - new_height;
      for (board_size_t i = 0; i < amount; i++)
        m_impl->m_resizer->remove_row_bottom(m_impl->m_parsed_board, m_impl->m_width,
                                             m_impl->m_height);
    }
  }

  if (new_width != old_width) {
    if (new_width > old_width) {
      board_size_t amount = new_width - old_width;
      for (board_size_t i = 0; i < amount; i++)
        m_impl->m_resizer->add_column_right(m_impl->m_parsed_board, m_impl->m_width,
                                            m_impl->m_height);
    } else {
      board_size_t amount = old_width - new_width;
      for (board_size_t i = 0; i < amount; i++)
        m_impl->m_resizer->remove_column_right(m_impl->m_parsed_board, m_impl->m_width,
                                               m_impl->m_height);
    }
  }
}

void Puzzle::resize_and_center(board_size_t new_width, board_size_t new_height) {
  board_size_t left = 0, right = 0, top = 0, bottom = 0;

  if (new_width > width()) {
    left = (new_width - width()) / 2;
    right = new_width - width() - left;
  }

  if (new_height > height()) {
    top = (new_height - height()) / 2;
    bottom = new_height - height() - top;
  }

  if (left != 0 && right != 0 && top != 0 && bottom != 0) {
    for (board_size_t i = 0; i < left; i++)
      m_impl->m_resizer->add_column_left(m_impl->m_parsed_board, m_impl->m_width,
                                         m_impl->m_height);
    for (board_size_t i = 0; i < top; i++)
      m_impl->m_resizer->add_row_top(m_impl->m_parsed_board, m_impl->m_width,
                                     m_impl->m_height);

    if (right != 0 && bottom != 0) resize(width() + right, height() + bottom);
  }
}

void Puzzle::trim() {
  m_impl->reparse_if_not_parsed();

  m_impl->m_resizer->trim_top(m_impl->m_parsed_board, m_impl->m_width,
                              m_impl->m_height);
  m_impl->m_resizer->trim_bottom(m_impl->m_parsed_board, m_impl->m_width,
                                 m_impl->m_height);
  m_impl->m_resizer->trim_left(m_impl->m_parsed_board, m_impl->m_width,
                               m_impl->m_height);
  m_impl->m_resizer->trim_right(m_impl->m_parsed_board, m_impl->m_width,
                                m_impl->m_height);
}

bool Puzzle::is_board(const string &line) {
  bool only_digits_and_spaces = all_of(line.cbegin(), line.cend(), [](char c) -> bool {
    return (isdigit(c) != 0) || (isspace(c) != 0);
  });

  return !only_digits_and_spaces &&
         all_of(line.begin(), line.end(), [](char c) -> bool {
           return isspace(c) || isdigit(c) || Puzzle::is_pusher(c) ||
                  Puzzle::is_box(c) || Puzzle::is_goal(c) ||
                  Puzzle::is_empty_floor(c) || Puzzle::is_wall(c) || c == Rle::EOL ||
                  c == Rle::GROUP_START || c == Rle::GROUP_END;
         });
}

bool Puzzle::is_sokoban_plus(const string &line) {
  bool only_digits_and_spaces = all_of(line.cbegin(), line.cend(), [](char c) -> bool {
    return (isdigit(c) != 0) || (isspace(c) != 0);
  });

  return only_digits_and_spaces && !is_blank(line);
}

Puzzle::unique_ptr_t Puzzle::instance_from(Tessellation tessellation,
                                           board_size_t width, board_size_t height) {
  switch (tessellation) {
  case Tessellation::SOKOBAN:
    return make_unique<SokobanPuzzle>(width, height);
    break;
  case Tessellation::HEXOBAN:
    return make_unique<HexobanPuzzle>(width, height);
    break;
  case Tessellation::TRIOBAN:
    return make_unique<TriobanPuzzle>(width, height);
    break;
  case Tessellation::OCTOBAN:
    return make_unique<OctobanPuzzle>(width, height);
    break;
    // Do not handle default, let compiler generate warning when another tessellation
    // is added...
  }
  throw invalid_argument("Unknown tessellation!");
}

Puzzle::unique_ptr_t Puzzle::instance_from(Tessellation tessellation,
                                           const string &board) {
  switch (tessellation) {
  case Tessellation::SOKOBAN:
    return make_unique<SokobanPuzzle>(board);
    break;
  case Tessellation::HEXOBAN:
    return make_unique<HexobanPuzzle>(board);
    break;
  case Tessellation::TRIOBAN:
    return make_unique<TriobanPuzzle>(board);
    break;
  case Tessellation::OCTOBAN:
    return make_unique<OctobanPuzzle>(board);
    break;
    // Do not handle default, let compiler generate warning when another tessellation
    // is added...
  }
  throw invalid_argument("Unknown tessellation!");
}

bool is_blank(const std::string &line) {
  return line.empty() || all_of(line.begin(), line.end(),
                                [](char c) -> bool { return isspace(c) != 0; });
}

namespace implementation {

void PuzzleResizer::add_row_top(parsed_board_t &parsed_board, board_size_t &width,
                                board_size_t &height) const {
  parsed_board_t old_body = parsed_board;
  board_size_t old_height = height;

  height = height + 1;
  parsed_board = parsed_board_t(width * height, Puzzle::VISIBLE_FLOOR);

  for (board_size_t x = 0; x < width; x++)
    for (board_size_t y = 0; y < old_height; y++)
      parsed_board[index_1d(x, y + 1, width)] = old_body[index_1d(x, y, width)];
}

void PuzzleResizer::add_row_bottom(parsed_board_t &parsed_board, board_size_t &width,
                                   board_size_t &height) const {
  parsed_board_t old_body = parsed_board;
  board_size_t old_height = height;

  height = height + 1;
  parsed_board = parsed_board_t(width * height, Puzzle::VISIBLE_FLOOR);

  for (board_size_t x = 0; x < width; x++)
    for (board_size_t y = 0; y < old_height; y++)
      parsed_board[index_1d(x, y, width)] = old_body[index_1d(x, y, width)];
}

void PuzzleResizer::add_column_left(parsed_board_t &parsed_board, board_size_t &width,
                                    board_size_t &height) const {
  parsed_board_t old_body = parsed_board;
  board_size_t old_width = width;

  width = width + 1;
  parsed_board = parsed_board_t(width * height, Puzzle::VISIBLE_FLOOR);

  for (board_size_t x = 0; x < old_width; x++)
    for (board_size_t y = 0; y < height; y++)
      parsed_board[index_1d(x + 1, y, width)] = old_body[index_1d(x, y, old_width)];
}

void PuzzleResizer::add_column_right(parsed_board_t &parsed_board, board_size_t &width,
                                     board_size_t &height) const {
  parsed_board_t old_body = parsed_board;
  board_size_t old_width = width;

  width = width + 1;
  parsed_board = parsed_board_t(width * height, Puzzle::VISIBLE_FLOOR);

  for (board_size_t x = 0; x < old_width; x++)
    for (board_size_t y = 0; y < height; y++)
      parsed_board[index_1d(x, y, width)] = old_body[index_1d(x, y, old_width)];
}

void PuzzleResizer::remove_row_top(parsed_board_t &parsed_board, board_size_t &width,
                                   board_size_t &height) const {
  parsed_board_t old_body = parsed_board;

  height = height - 1;
  parsed_board = parsed_board_t(width * height, Puzzle::VISIBLE_FLOOR);

  for (board_size_t x = 0; x < width; x++)
    for (board_size_t y = 0; y < height; y++)
      parsed_board[index_1d(x, y, width)] = old_body[index_1d(x, y + 1, width)];
}

void PuzzleResizer::remove_row_bottom(parsed_board_t &parsed_board, board_size_t &width,
                                      board_size_t &height) const {
  parsed_board_t old_body = parsed_board;

  height = height - 1;
  parsed_board = parsed_board_t(width * height, Puzzle::VISIBLE_FLOOR);

  for (board_size_t x = 0; x < width; x++)
    for (board_size_t y = 0; y < height; y++)
      parsed_board[index_1d(x, y, width)] = old_body[index_1d(x, y, width)];
}

void PuzzleResizer::remove_column_left(parsed_board_t &parsed_board,
                                       board_size_t &width,
                                       board_size_t &height) const {
  parsed_board_t old_body = parsed_board;
  board_size_t old_width = width;

  width = width - 1;
  parsed_board = parsed_board_t(width * height, Puzzle::VISIBLE_FLOOR);

  for (board_size_t x = 0; x < width; x++)
    for (board_size_t y = 0; y < height; y++)
      parsed_board[index_1d(x, y, width)] = old_body[index_1d(x + 1, y, old_width)];
}

void PuzzleResizer::remove_column_right(parsed_board_t &parsed_board,
                                        board_size_t &width,
                                        board_size_t &height) const {
  parsed_board_t old_body = parsed_board;
  board_size_t old_width = width;

  width = width - 1;
  parsed_board = parsed_board_t(width * height, Puzzle::VISIBLE_FLOOR);

  for (board_size_t x = 0; x < width; x++)
    for (board_size_t y = 0; y < height; y++)
      parsed_board[index_1d(x, y, width)] = old_body[index_1d(x, y, old_width)];
}

void PuzzleResizer::trim_left(parsed_board_t &parsed_board, board_size_t &width,
                              board_size_t &height) const {
  board_size_t amount = width;
  for (board_size_t y = 0; y < height; y++) {
    for (board_size_t x = 0; x < width; x++) {
      bool border_found =
        Puzzle::is_border_element(parsed_board[index_1d(x, y, width)]);
      if (border_found) {
        if (x < amount) amount = x;
        break;
      }
    }
  }
  for (board_size_t i = 0; i < amount; i++) {
    remove_column_left(parsed_board, width, height);
  }
}

void PuzzleResizer::trim_right(parsed_board_t &parsed_board, board_size_t &width,
                               board_size_t &height) const {
  reverse_columns(parsed_board, width, height);
  trim_left(parsed_board, width, height);
  reverse_columns(parsed_board, width, height);
}

void PuzzleResizer::trim_top(parsed_board_t &parsed_board, board_size_t &width,
                             board_size_t &height) const {
  board_size_t amount = height;
  for (board_size_t x = 0; x < width; x++) {
    bool border_found = false;
    for (board_size_t y = 0; y < height && !border_found; y++) {
      border_found = Puzzle::is_border_element(parsed_board[index_1d(x, y, width)]);
      if (border_found && y < amount) amount = y;
    }
  }
  for (board_size_t i = 0; i < amount; i++) {
    remove_row_top(parsed_board, width, height);
  }
}

void PuzzleResizer::trim_bottom(parsed_board_t &parsed_board, board_size_t &width,
                                board_size_t &height) const {
  reverse_rows(parsed_board, width, height);
  trim_top(parsed_board, width, height);
  reverse_rows(parsed_board, width, height);
}

void PuzzleResizer::reverse_rows(parsed_board_t &parsed_board, board_size_t &width,
                                 board_size_t &height) const {
  parsed_board_t old_body = parsed_board;

  for (board_size_t x = 0; x < width; x++)
    for (board_size_t y = 0; y < height; y++)
      parsed_board[index_1d(x, y, width)] =
        old_body[index_1d(x, height - y - 1, width)];
}

void PuzzleResizer::reverse_columns(parsed_board_t &parsed_board, board_size_t &width,
                                    board_size_t &height) const {
  parsed_board_t old_body = parsed_board;

  for (board_size_t x = 0; x < width; x++)
    for (board_size_t y = 0; y < height; y++)
      parsed_board[index_1d(x, y, width)] = old_body[index_1d(width - x - 1, y, width)];
}

size_t PuzzleParser::calculate_width(const Strings &strings) {
  size_t width = 0;
  for (auto line : strings)
    if (line.length() > width) width = line.length();
  return width;
}

Strings PuzzleParser::normalize_width(const Strings &strings, char fill_chr) {
  size_t width = calculate_width(strings);
  Strings retv = strings;
  for (string &line : retv) {
    if (line.length() < width) { line.append(width - line.length(), fill_chr); }
  }
  return retv;
}

Strings PuzzleParser::cleaned_board_lines(const std::string &line) {
  if (is_blank(line)) { return Strings(); }
  if (!io::Puzzle::is_board(line)) {
    throw std::invalid_argument("Illegal characters found in board string");
  }
  string data = io::Rle::decode(line);

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

string PuzzlePrinter::print(const parsed_board_t &parsed_board, board_size_t width,
                            board_size_t height, bool use_visible_floor,
                            bool rle_encode) const {
  Strings retv_list;
  char floor = use_visible_floor ? Puzzle::VISIBLE_FLOOR : Puzzle::FLOOR;

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

  if (rle_encode) { retv = Rle::encode(retv); }

  return retv;
}

void LIBSOKOENGINE_LOCAL _copy(parsed_board_t &parsed_board, board_size_t &width,
                               board_size_t &height, const Strings &strings) {
  width = strings.size() > 0 ? strings.front().size() : 0;
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
