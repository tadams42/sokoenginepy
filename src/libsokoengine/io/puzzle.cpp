/// @file
#include "puzzle.hpp"

#include "hexoban_io.hpp"
#include "octoban_io.hpp"
#include "puzzle_parsing.hpp"
#include "sokoban_io.hpp"
#include "tessellation_impl.hpp"
#include "trioban_io.hpp"

#include <boost/algorithm/string.hpp>

using sokoengine::implementation::_copy;
using sokoengine::implementation::Characters;
using sokoengine::implementation::HexobanIo;
using sokoengine::implementation::is_blank;
using sokoengine::implementation::OctobanIo;
using sokoengine::implementation::parsed_board_t;
using sokoengine::implementation::PuzzleParser;
using sokoengine::implementation::PuzzlePrinter;
using sokoengine::implementation::PuzzleResizer;
using sokoengine::implementation::SokobanIo;
using sokoengine::implementation::Strings;
using sokoengine::implementation::TessellationImpl;
using sokoengine::implementation::TriobanIo;
using std::invalid_argument;
using std::make_unique;
using std::string;

namespace sokoengine {
namespace io {

class LIBSOKOENGINE_LOCAL Puzzle::PIMPL {
public:
  string    m_title;
  string    m_author;
  string    m_boxorder;
  string    m_goalorder;
  string    m_notes;
  Snapshots m_snapshots;

  board_size_t   m_width      = 0;
  board_size_t   m_height     = 0;
  bool           m_was_parsed = false;
  string         m_original_board;
  parsed_board_t m_parsed_board;

  Tessellation m_tessellation;

  // Non-owned ptr
  const PuzzleResizer *m_resizer = nullptr;
  // Non-owned ptr
  const PuzzleParser *m_parser = nullptr;
  // Non-owned ptr
  const PuzzlePrinter *m_printer = nullptr;

  PIMPL(const Tessellation &tessellation, board_size_t width, board_size_t height)
    : m_width(width)
    , m_height(height)
    , m_was_parsed(true)
    , m_parsed_board(width * height, Puzzle::VISIBLE_FLOOR)
    , m_tessellation(tessellation) {
    bool tessellation_found = false;
    switch (m_tessellation) {
      case Tessellation::SOKOBAN:
        m_resizer          = (&SokobanIo::resizer());
        m_parser           = (&SokobanIo::parser());
        m_printer          = (&SokobanIo::printer());
        tessellation_found = true;
        break;
      case Tessellation::TRIOBAN:
        m_resizer          = (&TriobanIo::resizer());
        m_parser           = (&TriobanIo::parser());
        m_printer          = (&TriobanIo::printer());
        tessellation_found = true;
        break;
      case Tessellation::HEXOBAN:
        m_resizer          = (&HexobanIo::resizer());
        m_parser           = (&HexobanIo::parser());
        m_printer          = (&HexobanIo::printer());
        tessellation_found = true;
        break;
      case Tessellation::OCTOBAN:
        m_resizer          = (&OctobanIo::resizer());
        m_parser           = (&OctobanIo::parser());
        m_printer          = (&OctobanIo::printer());
        tessellation_found = true;
        break;
        // Don't handle default here so we get compiler warning if some new Tessellation
        // was not selected
    }
    if (!tessellation_found) {
      throw std::invalid_argument("Unknown tessellation!");
    }
  }

  PIMPL(const Tessellation &tessellation, const string &board)
    : PIMPL(tessellation, 0, 0) {
    m_was_parsed     = false;
    m_original_board = board;
    if (!Characters::is_board(m_original_board)) {
      throw invalid_argument("Invalid characters in board string!");
    }
  }

  PIMPL(const PIMPL &rv)            = default;
  PIMPL &operator=(const PIMPL &rv) = default;
  PIMPL(PIMPL &&rv)                 = default;
  PIMPL &operator=(PIMPL &&rv)      = default;
  ~PIMPL()                          = default;

  void reparse() {
    if (!is_blank(m_original_board)) {
      Strings board_rows = m_parser->parse(m_original_board);
      _copy(m_parsed_board, m_width, m_height, board_rows);
    } else {
      m_height = 0;
      m_width  = 0;
      m_parsed_board =
        parsed_board_t(static_cast<size_t>(m_height) * m_width, Puzzle::VISIBLE_FLOOR);
    }
    m_was_parsed = true;
  }

  void reparse_if_not_parsed() {
    if (!m_was_parsed)
      reparse();
  }
};

Puzzle::Puzzle(const Tessellation &tessellation, const string &board)
  : m_impl(make_unique<PIMPL>(tessellation, board)) {}

Puzzle::Puzzle(
  const Tessellation &tessellation, board_size_t width, board_size_t height
)
  : m_impl(make_unique<PIMPL>(tessellation, width, height)) {}

Puzzle::Puzzle(const Puzzle &rv)
  : m_impl(make_unique<PIMPL>(*rv.m_impl)) {}

Puzzle &Puzzle::operator=(const Puzzle &rv) {
  if (this != &rv)
    m_impl = make_unique<PIMPL>(*rv.m_impl);
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

const string &Puzzle::notes() const { return m_impl->m_notes; }

string &Puzzle::notes() { return m_impl->m_notes; }

const Snapshots &Puzzle::snapshots() const { return m_impl->m_snapshots; }

Snapshots &Puzzle::snapshots() { return m_impl->m_snapshots; }

Tessellation Puzzle::tessellation() const { return m_impl->m_tessellation; }

CellOrientation Puzzle::cell_orientation(position_t position) const {
  return TessellationImpl::instance(m_impl->m_tessellation)
    .cell_orientation(position, width(), height());
}

char Puzzle::at(position_t position) const {
  m_impl->reparse_if_not_parsed();
  return m_impl->m_parsed_board.at(position);
}

void Puzzle::set_at(position_t position, char c) {
  if (!Characters::is_puzzle_element(c)) {
    throw invalid_argument(string("Not a board character: '") + c + "'!");
  }
  m_impl->reparse_if_not_parsed();
  m_impl->m_parsed_board.at(position) = c;
}

char Puzzle::operator[](position_t position) const {
  m_impl->reparse_if_not_parsed();
  return m_impl->m_parsed_board[position];
}

void Puzzle::set(position_t position, char c) {
  if (!Characters::is_puzzle_element(c)) {
    throw invalid_argument(string("Not a board character: '") + c + "'!");
  }
  m_impl->reparse_if_not_parsed();
  m_impl->m_parsed_board[position] = c;
}

string Puzzle::to_board_str(bool use_visible_floor, bool rle_encode) const {
  m_impl->reparse_if_not_parsed();
  return m_impl->m_printer->print(
    m_impl->m_parsed_board,
    m_impl->m_width,
    m_impl->m_height,
    use_visible_floor,
    rle_encode
  );
}

const string &Puzzle::board() const { return m_impl->m_original_board; }

void Puzzle::set_board(const string &board) {
  if (!Characters::is_board(board))
    throw invalid_argument("Invalid characters in board string!");
  m_impl->m_original_board = board;
  m_impl->m_was_parsed     = false;
}

string Puzzle::internal_board() const {
  m_impl->reparse_if_not_parsed();
  return string(m_impl->m_parsed_board.cbegin(), m_impl->m_parsed_board.cend());
}

string Puzzle::str() const { return to_board_str(false); }

string Puzzle::repr() const {
  string klass_name = "Puzzle";

  Strings board_lines;
  string  tmp = to_board_str(true);
  boost::split(board_lines, tmp, boost::is_any_of("\n"));

  for (string &line : board_lines)
    line = "    '" + line + "'";

  return klass_name + "(" + sokoengine::implementation::to_str(m_impl->m_tessellation)
       + ", board='\\n'.join([\n" + boost::join(board_lines, ",\n") + "\n]))";
}

bool Puzzle::has_sokoban_plus() const {
  return (!is_blank(m_impl->m_boxorder) || !is_blank(m_impl->m_goalorder));
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
  return count_if(
    m_impl->m_original_board.begin(),
    m_impl->m_original_board.end(),
    [](char c) {
      return Characters::is_pusher(c);
    }
  );
}

size_t Puzzle::boxes_count() const {
  return count_if(
    m_impl->m_original_board.begin(),
    m_impl->m_original_board.end(),
    [](char c) {
      return Characters::is_box(c);
    }
  );
}

size_t Puzzle::goals_count() const {
  return count_if(
    m_impl->m_original_board.begin(),
    m_impl->m_original_board.end(),
    [](char c) {
      return Characters::is_goal(c);
    }
  );
}

void Puzzle::add_row_top() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->add_row_top(
    m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
  );
}

void Puzzle::add_row_bottom() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->add_row_bottom(
    m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
  );
}

void Puzzle::add_column_left() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->add_column_left(
    m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
  );
}

void Puzzle::add_column_right() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->add_column_right(
    m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
  );
}

void Puzzle::remove_row_top() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->remove_row_top(
    m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
  );
}

void Puzzle::remove_row_bottom() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->remove_row_bottom(
    m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
  );
}

void Puzzle::remove_column_left() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->remove_column_left(
    m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
  );
}

void Puzzle::remove_column_right() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->remove_column_right(
    m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
  );
}

void Puzzle::trim_left() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->trim_left(
    m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
  );
}

void Puzzle::trim_right() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->trim_right(
    m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
  );
}

void Puzzle::trim_top() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->trim_top(
    m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
  );
}

void Puzzle::trim_bottom() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->trim_bottom(
    m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
  );
}

void Puzzle::reverse_rows() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->reverse_rows(
    m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
  );
}

void Puzzle::reverse_columns() {
  m_impl->reparse_if_not_parsed();
  m_impl->m_resizer->reverse_columns(
    m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
  );
}

void Puzzle::resize(board_size_t new_width, board_size_t new_height) {
  board_size_t old_width  = width();
  board_size_t old_height = height();

  if (new_height != old_height) {
    if (new_height > old_height) {
      board_size_t amount = new_height - old_height;
      for (board_size_t i = 0; i < amount; i++)
        m_impl->m_resizer->add_row_bottom(
          m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
        );
    } else {
      board_size_t amount = old_height - new_height;
      for (board_size_t i = 0; i < amount; i++)
        m_impl->m_resizer->remove_row_bottom(
          m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
        );
    }
  }

  if (new_width != old_width) {
    if (new_width > old_width) {
      board_size_t amount = new_width - old_width;
      for (board_size_t i = 0; i < amount; i++)
        m_impl->m_resizer->add_column_right(
          m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
        );
    } else {
      board_size_t amount = old_width - new_width;
      for (board_size_t i = 0; i < amount; i++)
        m_impl->m_resizer->remove_column_right(
          m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
        );
    }
  }
}

void Puzzle::resize_and_center(board_size_t new_width, board_size_t new_height) {
  board_size_t left = 0, right = 0, top = 0, bottom = 0;

  if (new_width > width()) {
    left  = (new_width - width()) / 2;
    right = new_width - width() - left;
  }

  if (new_height > height()) {
    top    = (new_height - height()) / 2;
    bottom = new_height - height() - top;
  }

  if (left != 0 && right != 0 && top != 0 && bottom != 0) {
    for (board_size_t i = 0; i < left; i++)
      m_impl->m_resizer->add_column_left(
        m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
      );
    for (board_size_t i = 0; i < top; i++)
      m_impl->m_resizer->add_row_top(
        m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
      );

    if (right != 0 && bottom != 0)
      resize(width() + right, height() + bottom);
  }
}

void Puzzle::trim() {
  m_impl->reparse_if_not_parsed();

  m_impl->m_resizer->trim_top(
    m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
  );
  m_impl->m_resizer->trim_bottom(
    m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
  );
  m_impl->m_resizer->trim_left(
    m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
  );
  m_impl->m_resizer->trim_right(
    m_impl->m_parsed_board, m_impl->m_width, m_impl->m_height
  );
}

} // namespace io
} // namespace sokoengine
