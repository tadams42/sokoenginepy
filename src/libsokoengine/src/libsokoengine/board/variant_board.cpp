#include "variant_board.hpp"
#include "board_cell.hpp"
#include "hexoban_board.hpp"
#include "octoban_board.hpp"
#include "sokoban_board.hpp"
#include "tessellation.hpp"
#include "trioban_board.hpp"

#include <boost/algorithm/string.hpp>
#include <boost/tokenizer.hpp>

using namespace std;
using namespace boost;

namespace sokoengine {

class LIBSOKOENGINE_LOCAL VariantBoard::PIMPL {
public:
  BoardGraph m_graph;
  // non owned ptr
  const Tessellation *m_tessellation;

  PIMPL(const Tessellation &tessellation, board_size_t board_width,
        board_size_t board_height)
      : m_graph(board_width, board_height, tessellation.graph_type()),
        m_tessellation(&tessellation) {
    m_graph.reconfigure_edges(*m_tessellation);
  }

  PIMPL(const Tessellation &tessellation, const string &board_str)
      : m_graph(0, 0, tessellation.graph_type()), m_tessellation(&tessellation) {
    if (TextUtils::is_blank(board_str))
      m_graph.reconfigure_edges(*m_tessellation);
    else
      reinit(board_str, true);
  }

  PIMPL(const PIMPL &rv) = default;
  PIMPL &operator=(const PIMPL &rv) = default;
  PIMPL(PIMPL &&rv) = default;
  PIMPL &operator=(PIMPL &&rv) = default;

  void reinit(board_size_t board_width, board_size_t board_height, bool reconf_edges) {
    m_graph = BoardGraph(board_width, board_height, m_tessellation->graph_type());
    if (reconf_edges)
      m_graph.reconfigure_edges(*m_tessellation);
  }

  void reinit(const string &board_str, bool reconf_edges) {
    if (!TextUtils::is_blank(board_str)) {
      StringList board_rows = m_tessellation->parser().parse(board_str);
      board_size_t height = board_rows.size();
      board_size_t width = 0;
      if (height > 0) {
        width = board_rows.front().size();
      }
      reinit(width, height, reconf_edges);
      auto y_end = board_rows.end();
      board_size_t y = 0;
      auto row = board_rows.begin();
      for (; row != y_end; y++, row++) {
        auto x_end = (*row).end();
        board_size_t x = 0;
        auto character = (*row).begin();
        for (; character != x_end; x++, character++)
          m_graph.cell(index_1d(x, y, m_graph.board_width())) = BoardCell(*character);
      }
    }
  }
};

VariantBoard::unique_ptr_t VariantBoard::instance_from(const Tessellation &tessellation,
                                                       board_size_t board_width,
                                                       board_size_t board_height) {
  return instance_from(tessellation.str(), board_width, board_height);
}

VariantBoard::unique_ptr_t VariantBoard::instance_from(const string &tessellation_name,
                                                       board_size_t board_width,
                                                       board_size_t board_height) {
  if (tessellation_name == "sokoban")
    return make_unique<SokobanBoard>(board_width, board_height);
  else if (tessellation_name == "trioban")
    return make_unique<TriobanBoard>(board_width, board_height);
  else if (tessellation_name == "octoban")
    return make_unique<OctobanBoard>(board_width, board_height);
  else if (tessellation_name == "hexoban")
    return make_unique<HexobanBoard>(board_width, board_height);

  throw UnknownTessellationError(string() +
                                 "Don't know about tessellation: " + tessellation_name);
}

VariantBoard::unique_ptr_t VariantBoard::instance_from(const Tessellation &tessellation,
                                                       const string &board_str) {
  return instance_from(tessellation.str(), board_str);
}

VariantBoard::unique_ptr_t VariantBoard::instance_from(const string &tessellation_name,
                                                       const string &board_str) {
  if (tessellation_name == "sokoban")
    return make_unique<SokobanBoard>(board_str);
  else if (tessellation_name == "trioban")
    return make_unique<TriobanBoard>(board_str);
  else if (tessellation_name == "octoban")
    return make_unique<OctobanBoard>(board_str);
  else if (tessellation_name == "hexoban")
    return make_unique<HexobanBoard>(board_str);
  throw UnknownTessellationError(string() +
                                 "Don't know about tessellation: " + tessellation_name);
}

bool VariantBoard::is_board_string(const string &line) {
  return !TextUtils::contains_only_digits_and_spaces(line) &&
         all_of(line.begin(), line.end(), [](char c) -> bool {
           return isspace(c) || isdigit(c) || BoardCell::is_pusher_chr(c) ||
                  BoardCell::is_box_chr(c) || BoardCell::is_goal_chr(c) ||
                  BoardCell::is_empty_floor_chr(c) || BoardCell::is_wall_chr(c) ||
                  c == TextUtils::RLE_ROW_SEPARATOR;
         });
}

StringList VariantBoard::parse_board_string(const string &source) {
  if (TextUtils::is_blank(source)) {
    return StringList();
  }
  if (!is_board_string(source)) {
    throw BoardConversionError("Illegal characters found in board string");
  }

  string line = source;
  if (!TextUtils::rle_decode(line)) {
    throw BoardConversionError("Illegal characters found in board string");
  }

  StringList retv;
  boost::split(retv, line, boost::is_any_of("\n"));
  retv = TextUtils::normalize_width(retv);
  return retv;
}

VariantBoard::VariantBoard(const Tessellation &tessellation, board_size_t board_width,
                           board_size_t board_height)
    : m_impl(make_unique<PIMPL>(tessellation, board_width, board_height)) {}

VariantBoard::VariantBoard(const Tessellation &tessellation, const string &board_str)
    : m_impl(make_unique<PIMPL>(tessellation, board_str)) {}

VariantBoard::VariantBoard(const VariantBoard &rv)
    : m_impl(make_unique<PIMPL>(*rv.m_impl)) {}

VariantBoard &VariantBoard::operator=(const VariantBoard &rv) {
  if (this != &rv)
    m_impl = make_unique<PIMPL>(*rv.m_impl);
  return *this;
}

VariantBoard::VariantBoard(VariantBoard &&) = default;

VariantBoard &VariantBoard::operator=(VariantBoard &&) = default;

VariantBoard::~VariantBoard() = default;

const Tessellation &VariantBoard::tessellation() const {
  return *(m_impl->m_tessellation);
}

void VariantBoard::reinit(board_size_t board_width, board_size_t board_height,
                          bool reconf_edges) {
  m_impl->reinit(board_width, board_height, reconf_edges);
}

void VariantBoard::reinit(const string &board_str, bool reconf_edges) {
  m_impl->reinit(board_str, reconf_edges);
}

bool VariantBoard::operator==(const VariantBoard &rv) const {
  if (width() == rv.width() && height() == rv.height() && typeid(*this) == typeid(rv)) {
    bool non_equal_found = false;
    position_t position;
    board_size_t s = size();
    for (position = 0; position < s && !non_equal_found; ++position)
      non_equal_found = (cell(position) != rv.cell(position));
    return !non_equal_found;
  }
  return false;
}

bool VariantBoard::operator!=(const VariantBoard &rv) const { return !(*this == rv); }

const BoardCell &VariantBoard::cell_at(position_t position) const {
  return m_impl->m_graph.cell_at(position);
}

BoardCell &VariantBoard::cell_at(position_t position) {
  return m_impl->m_graph.cell_at(position);
}

const BoardCell &VariantBoard::cell(position_t position) const {
  return m_impl->m_graph.cell(position);
}

BoardCell &VariantBoard::cell(position_t position) {
  return m_impl->m_graph.cell(position);
}

const BoardCell VariantBoard::operator[](position_t position) const {
  return m_impl->m_graph[position];
}

BoardCell &VariantBoard::operator[](position_t position) {
  return m_impl->m_graph[position];
}

bool VariantBoard::contains(position_t position) const {
  return m_impl->m_graph.contains(position);
}

string VariantBoard::to_str(bool use_visible_floor, bool rle_encode) const {
  return m_impl->m_tessellation->printer().print(*this, use_visible_floor, rle_encode);
}

string VariantBoard::str() const { return to_str(false, false); }

string VariantBoard::repr() const {
  string class_name = "VariantBoard";
  if (typeid(*this) == typeid(const SokobanBoard &))
    class_name = "SokobanBoard";
  if (typeid(*this) == typeid(const TriobanBoard &))
    class_name = "TriobanBoard";
  if (typeid(*this) == typeid(const OctobanBoard &))
    class_name = "OctobanBoard";
  if (typeid(*this) == typeid(const HexobanBoard &))
    class_name = "HexobanBoard";

  StringList board_lines;
  string tmp = to_str(false, false);
  boost::split(board_lines, tmp, boost::is_any_of("\n"));

  for (string &line : board_lines)
    line = "    '" + line + "'";

  return class_name + "(board_str='\\n'.join([\n" + join(board_lines, ",\n") + "\n]))";
}

board_size_t VariantBoard::width() const { return m_impl->m_graph.board_width(); }

board_size_t VariantBoard::height() const { return m_impl->m_graph.board_height(); }

board_size_t VariantBoard::size() const { return width() * height(); }

position_t VariantBoard::neighbor(position_t from_position,
                                  const Direction &direction) const {
  return m_impl->m_graph.neighbor(from_position, direction);
}

position_t VariantBoard::neighbor_at(position_t from_position,
                                     const Direction &direction) const {
  return m_impl->m_graph.neighbor_at(from_position, direction);
}

Positions VariantBoard::wall_neighbors(position_t from_position) const {
  return m_impl->m_graph.wall_neighbors(from_position);
}

Positions VariantBoard::all_neighbors(position_t from_position) const {
  return m_impl->m_graph.all_neighbors(from_position);
}

void VariantBoard::clear() {
  board_size_t s = size();
  for (position_t position = 0; position < s; ++position) {
    cell(position).clear();
  }
}

void VariantBoard::mark_play_area() { m_impl->m_graph.mark_play_area(); }

Positions
VariantBoard::positions_reachable_by_pusher(position_t pusher_position,
                                            const Positions &excluded_positions) const {
  return m_impl->m_graph.positions_reachable_by_pusher(pusher_position,
                                                       excluded_positions);
}

position_t
VariantBoard::normalized_pusher_position(position_t pusher_position,
                                         const Positions &excluded_positions) const {
  return m_impl->m_graph.normalized_pusher_position(pusher_position,
                                                    excluded_positions);
}

position_t VariantBoard::path_destination(position_t start_position,
                                          const Directions &directions_path) const {
  return m_impl->m_graph.path_destination(start_position, directions_path);
}

Positions VariantBoard::find_jump_path(position_t start_position,
                                       position_t end_position) const {
  return m_impl->m_graph.find_jump_path(start_position, end_position);
}

Positions VariantBoard::find_move_path(position_t start_position,
                                       position_t end_position) const {
  return m_impl->m_graph.find_move_path(start_position, end_position);
}

CellOrientation VariantBoard::cell_orientation(position_t position) const {
  return m_impl->m_tessellation->cell_orientation(position, width(), height());
}

Directions
VariantBoard::positions_path_to_directions_path(const Positions &positions_path) const {
  return m_impl->m_graph.positions_path_to_directions_path(positions_path);
}

void VariantBoard::add_row_top() {
  m_impl->m_tessellation->resizer().add_row_top(*this, true);
}

void VariantBoard::add_row_bottom() {
  m_impl->m_tessellation->resizer().add_row_bottom(*this, true);
}

void VariantBoard::add_column_left() {
  m_impl->m_tessellation->resizer().add_column_left(*this, true);
}

void VariantBoard::add_column_right() {
  m_impl->m_tessellation->resizer().add_column_right(*this, true);
}

void VariantBoard::remove_row_top() {
  m_impl->m_tessellation->resizer().remove_row_top(*this, true);
}

void VariantBoard::remove_row_bottom() {
  m_impl->m_tessellation->resizer().remove_row_bottom(*this, true);
}

void VariantBoard::remove_column_left() {
  m_impl->m_tessellation->resizer().remove_column_left(*this, true);
}

void VariantBoard::remove_column_right() {
  m_impl->m_tessellation->resizer().remove_column_right(*this, true);
}

void VariantBoard::trim_left() {
  m_impl->m_tessellation->resizer().trim_left(*this, true);
}

void VariantBoard::trim_right() {
  m_impl->m_tessellation->resizer().trim_right(*this, true);
}

void VariantBoard::trim_top() {
  m_impl->m_tessellation->resizer().trim_top(*this, true);
}

void VariantBoard::trim_bottom() {
  m_impl->m_tessellation->resizer().trim_bottom(*this, true);
}

void VariantBoard::reverse_rows() {
  m_impl->m_tessellation->resizer().reverse_rows(*this, true);
}

void VariantBoard::reverse_columns() {
  m_impl->m_tessellation->resizer().reverse_columns(*this, true);
}

void VariantBoard::resize(board_size_t new_width, board_size_t new_height) {
  board_size_t old_width = width();
  board_size_t old_height = height();

  if (new_height != old_height) {
    if (new_height > old_height) {
      board_size_t amount = new_height - old_height;
      for (board_size_t i = 0; i < amount; i++)
        m_impl->m_tessellation->resizer().add_row_bottom(*this, false);
    } else {
      board_size_t amount = old_height - new_height;
      for (board_size_t i = 0; i < amount; i++)
        m_impl->m_tessellation->resizer().remove_row_bottom(*this, false);
    }
  }

  if (new_width != old_width) {
    if (new_width > old_width) {
      board_size_t amount = new_width - old_width;
      for (board_size_t i = 0; i < amount; i++)
        m_impl->m_tessellation->resizer().add_column_right(*this, false);
    } else {
      board_size_t amount = old_width - new_width;
      for (board_size_t i = 0; i < amount; i++)
        m_impl->m_tessellation->resizer().remove_column_right(*this, false);
    }
  }

  if (old_width != width() || old_height != height())
    m_impl->m_graph.reconfigure_edges(tessellation());
}

void VariantBoard::resize_and_center(board_size_t new_width, board_size_t new_height) {
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
      m_impl->m_tessellation->resizer().add_column_left(*this, false);
    for (board_size_t i = 0; i < top; i++)
      m_impl->m_tessellation->resizer().add_row_top(*this, false);

    if (right != 0 && bottom != 0)
      resize(width() + right, height() + bottom);
    else
      m_impl->m_graph.reconfigure_edges(tessellation());
  }
}

void VariantBoard::trim() {
  board_size_t old_width = width();
  board_size_t old_height = height();

  m_impl->m_tessellation->resizer().trim_top(*this, false);
  m_impl->m_tessellation->resizer().trim_bottom(*this, false);
  m_impl->m_tessellation->resizer().trim_left(*this, false);
  m_impl->m_tessellation->resizer().trim_right(*this, false);

  if (old_width != width() || old_height != height())
    m_impl->m_graph.reconfigure_edges(tessellation());
}

const BoardGraph &VariantBoard::graph() const { return m_impl->m_graph; }

namespace implementation {

void VariantBoardResizer::reinit(VariantBoard &board, board_size_t board_width,
                                 board_size_t board_height, bool reconf_edges) const {
  board.reinit(board_width, board_height, reconf_edges);
}

void VariantBoardResizer::reinit(VariantBoard &board, const string &src,
                                 bool reconf_edges) const {
  board.reinit(src, reconf_edges);
}

void VariantBoardResizer::reconfigure_edges(VariantBoard &board) const {
  board.m_impl->m_graph.reconfigure_edges(board.tessellation());
}

void VariantBoardResizer::add_row_top(VariantBoard &board, bool reconf_edges) const {
  BoardGraph old_body = board.graph();
  board_size_t old_height = board.height();

  board.reinit(board.width(), board.height() + 1, reconf_edges);

  for (board_size_t x = 0; x < board.width(); x++)
    for (board_size_t y = 0; y < old_height; y++)
      board[index_1d(x, y + 1, board.width())] =
          old_body[index_1d(x, y, board.width())];
}

void VariantBoardResizer::add_row_bottom(VariantBoard &board, bool reconf_edges) const {
  BoardGraph old_body = board.graph();
  board_size_t old_height = board.height();

  board.reinit(board.width(), board.height() + 1, reconf_edges);

  for (board_size_t x = 0; x < board.width(); x++)
    for (board_size_t y = 0; y < old_height; y++)
      board[index_1d(x, y, board.width())] = old_body[index_1d(x, y, board.width())];
}

void VariantBoardResizer::add_column_left(VariantBoard &board,
                                          bool reconf_edges) const {
  BoardGraph old_body = board.graph();
  board_size_t old_width = board.width();

  board.reinit(board.width() + 1, board.height(), reconf_edges);

  for (board_size_t x = 0; x < old_width; x++)
    for (board_size_t y = 0; y < board.height(); y++)
      board[index_1d(x + 1, y, board.width())] = old_body[index_1d(x, y, old_width)];
}

void VariantBoardResizer::add_column_right(VariantBoard &board,
                                           bool reconf_edges) const {
  BoardGraph old_body = board.graph();
  board_size_t old_width = board.width();

  board.reinit(board.width() + 1, board.height(), reconf_edges);

  for (board_size_t x = 0; x < old_width; x++)
    for (board_size_t y = 0; y < board.height(); y++)
      board[index_1d(x, y, board.width())] = old_body[index_1d(x, y, old_width)];
}

void VariantBoardResizer::remove_row_top(VariantBoard &board, bool reconf_edges) const {
  BoardGraph old_body = board.graph();

  board.reinit(board.width(), board.height() - 1, reconf_edges);

  for (board_size_t x = 0; x < board.width(); x++)
    for (board_size_t y = 0; y < board.height(); y++)
      board[index_1d(x, y, board.width())] =
          old_body[index_1d(x, y + 1, board.width())];
}

void VariantBoardResizer::remove_row_bottom(VariantBoard &board,
                                            bool reconf_edges) const {
  BoardGraph old_body = board.graph();

  board.reinit(board.width(), board.height() - 1, reconf_edges);

  for (board_size_t x = 0; x < board.width(); x++)
    for (board_size_t y = 0; y < board.height(); y++)
      board[index_1d(x, y, board.width())] = old_body[index_1d(x, y, board.width())];
}

void VariantBoardResizer::remove_column_left(VariantBoard &board,
                                             bool reconf_edges) const {
  BoardGraph old_body = board.graph();
  board_size_t old_width = board.width();

  board.reinit(board.width() - 1, board.height(), reconf_edges);

  for (board_size_t x = 0; x < board.width(); x++)
    for (board_size_t y = 0; y < board.height(); y++)
      board[index_1d(x, y, board.width())] = old_body[index_1d(x + 1, y, old_width)];
}

void VariantBoardResizer::remove_column_right(VariantBoard &board,
                                              bool reconf_edges) const {
  BoardGraph old_body = board.graph();
  board_size_t old_width = board.width();

  board.reinit(board.width() - 1, board.height(), reconf_edges);

  for (board_size_t x = 0; x < board.width(); x++)
    for (board_size_t y = 0; y < board.height(); y++)
      board[index_1d(x, y, board.width())] = old_body[index_1d(x, y, old_width)];
}

void VariantBoardResizer::trim_left(VariantBoard &board, bool reconf_edges) const {
  board_size_t amount = board.width();
  for (board_size_t y = 0; y < board.height(); y++) {
    for (board_size_t x = 0; x < board.width(); x++) {
      bool border_found = board[index_1d(x, y, board.width())].is_border_element();
      if (border_found) {
        if (x < amount)
          amount = x;
        break;
      }
    }
  }
  for (board_size_t i = 0; i < amount; i++)
    remove_column_left(board, false);
  if (reconf_edges)
    reconfigure_edges(board);
}

void VariantBoardResizer::trim_right(VariantBoard &board, bool reconf_edges) const {
  reverse_columns(board, false);
  trim_left(board, false);
  reverse_columns(board, false);
  if (reconf_edges)
    reconfigure_edges(board);
}

void VariantBoardResizer::trim_top(VariantBoard &board, bool reconf_edges) const {
  board_size_t amount = board.height();
  for (board_size_t x = 0; x < board.width(); x++) {
    bool border_found = false;
    for (board_size_t y = 0; y < board.height() && !border_found; y++) {
      border_found = board[index_1d(x, y, board.width())].is_border_element();
      if (border_found && y < amount)
        amount = y;
    }
  }
  for (board_size_t i = 0; i < amount; i++)
    remove_row_top(board, false);
  if (reconf_edges)
    reconfigure_edges(board);
}

void VariantBoardResizer::trim_bottom(VariantBoard &board, bool reconf_edges) const {
  reverse_rows(board, false);
  trim_top(board, false);
  reverse_rows(board, false);
  if (reconf_edges)
    reconfigure_edges(board);
}

void VariantBoardResizer::reverse_rows(VariantBoard &board, bool reconf_edges) const {
  BoardGraph old_body = board.graph();

  board.reinit(board.width(), board.height(), false);

  for (board_size_t x = 0; x < board.width(); x++)
    for (board_size_t y = 0; y < board.height(); y++)
      board[index_1d(x, y, board.width())] =
          old_body[index_1d(x, board.height() - y - 1, board.width())];

  if (reconf_edges)
    reconfigure_edges(board);
}

void VariantBoardResizer::reverse_columns(VariantBoard &board,
                                          bool reconf_edges) const {
  BoardGraph old_body = board.graph();

  board.reinit(board.width(), board.height(), false);

  for (board_size_t x = 0; x < board.width(); x++)
    for (board_size_t y = 0; y < board.height(); y++)
      board[index_1d(x, y, board.width())] =
          old_body[index_1d(board.width() - x - 1, y, board.width())];

  if (reconf_edges)
    reconfigure_edges(board);
}

StringList VariantBoardParser::parse(const string &board_str) const {
  return VariantBoard::parse_board_string(board_str);
}

string VariantBoardPrinter::print(const VariantBoard &board, bool use_visible_floor,
                                  bool rle_encode) const {
  StringList retv_list;

  auto height = board.height();
  auto width = board.width();

  for (position_t y = 0; y < height; ++y) {
    string tmp;
    for (position_t x = 0; x != width; ++x) {
      tmp += board[index_1d(x, y, width)].to_str(use_visible_floor);
    }
    retv_list.push_back(tmp);
  }

  string retv = join(retv_list, "\n");
  if (rle_encode)
    TextUtils::rle_encode(retv);

  return retv;
}

} // namespace implementation

} // namespace sokoengine
