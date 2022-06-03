#include "puzzle.hpp"
#include "puzzle_types.hpp"
#include "rle.hpp"
#include "snapshot.hpp"
#include "utilities.hpp"

#include <boost/algorithm/string.hpp>

using namespace std;

namespace sokoengine {
namespace io {

using namespace implementation;

class LIBSOKOENGINE_LOCAL Puzzle::PIMPL {
public:
  size_t m_id;
  string m_board;
  PuzzleTypes m_puzzle_type;
  string m_title;
  string m_author;
  string m_boxorder;
  string m_goalorder;
  string m_notes;
  string m_created_at;
  string m_updated_at;
  Snapshots m_snapshots;

  PIMPL(size_t id, const std::string &board, const std::string &title,
        const std::string &author, const std::string &boxorder,
        const std::string &goalorder, const std::string &notes,
        const std::string &created_at, const std::string &updated_at,
        const PuzzleTypes &puzzle_type)
    : m_id(id),
      m_board(board),
      m_puzzle_type(puzzle_type),
      m_title(title),
      m_author(author),
      m_boxorder(boxorder),
      m_goalorder(goalorder),
      m_notes(notes),
      m_created_at(created_at),
      m_updated_at(updated_at) {}
};

Puzzle::Puzzle(size_t id, const std::string &board, const std::string &title,
               const std::string &author, const std::string &boxorder,
               const std::string &goalorder, const std::string &notes,
               const std::string &created_at, const std::string &updated_at,
               const PuzzleTypes &puzzle_type)
  : m_impl(std::make_unique<Puzzle::PIMPL>(id, board, title, author, boxorder,
                                           goalorder, notes, created_at, updated_at,
                                           puzzle_type)) {}

Puzzle::Puzzle(const Puzzle &rv)
  : m_impl(std::make_unique<Puzzle::PIMPL>(
      rv.m_impl->m_id, rv.m_impl->m_board, rv.m_impl->m_title, rv.m_impl->m_author,
      rv.m_impl->m_boxorder, rv.m_impl->m_goalorder, rv.m_impl->m_notes,
      rv.m_impl->m_created_at, rv.m_impl->m_updated_at, rv.m_impl->m_puzzle_type)) {}

Puzzle &Puzzle::operator=(const Puzzle &rv) {
  m_impl->m_id = rv.m_impl->m_id;
  m_impl->m_board = rv.m_impl->m_board;
  m_impl->m_title = rv.m_impl->m_title;
  m_impl->m_created_at = rv.m_impl->m_created_at;
  m_impl->m_updated_at = rv.m_impl->m_updated_at;
  m_impl->m_author = rv.m_impl->m_author;
  m_impl->m_boxorder = rv.m_impl->m_boxorder;
  m_impl->m_goalorder = rv.m_impl->m_goalorder;
  m_impl->m_notes = rv.m_impl->m_notes;
  m_impl->m_puzzle_type = rv.m_impl->m_puzzle_type;
  m_impl->m_snapshots = rv.m_impl->m_snapshots;

  return *this;
}

Puzzle::~Puzzle() = default;

const string &Puzzle::board() const { return m_impl->m_board; }
string &Puzzle::board() { return m_impl->m_board; }

const PuzzleTypes &Puzzle::puzzle_type() const { return m_impl->m_puzzle_type; }
PuzzleTypes &Puzzle::puzzle_type() { return m_impl->m_puzzle_type; }

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

size_t Puzzle::id() const { return m_impl->m_id; }
size_t &Puzzle::id() { return m_impl->m_id; }

const string &Puzzle::created_at() const { return m_impl->m_created_at; }
string &Puzzle::created_at() { return m_impl->m_created_at; }

const string &Puzzle::updated_at() const { return m_impl->m_updated_at; }
string &Puzzle::updated_at() { return m_impl->m_updated_at; }

void Puzzle::clear() {
  m_impl->m_board = m_impl->m_author = m_impl->m_title = m_impl->m_created_at =
    m_impl->m_updated_at = m_impl->m_boxorder = m_impl->m_goalorder = m_impl->m_notes =
      "";
  m_impl->m_snapshots.clear();
  m_impl->m_id = 1;
  m_impl->m_puzzle_type = PuzzleTypes::SOKOBAN;
}

size_t Puzzle::pushers_count() const {
  return count_if(m_impl->m_board.begin(), m_impl->m_board.end(),
                  [](char c) { return Puzzle::is_pusher(c); });
}

size_t Puzzle::boxes_count() const {
  return count_if(m_impl->m_board.begin(), m_impl->m_board.end(),
                  [](char c) { return Puzzle::is_box(c); });
}

size_t Puzzle::goals_count() const {
  return count_if(m_impl->m_board.begin(), m_impl->m_board.end(),
                  [](char c) { return Puzzle::is_goal(c); });
}

std::string Puzzle::reformatted(bool use_visible_floor, uint8_t break_long_lines_at,
                                bool rle_encode) {
  return m_impl->m_board;
}

bool Puzzle::is_board(const std::string &line) {
  return !contains_only_digits_and_spaces(line) &&
         all_of(line.begin(), line.end(), [](char c) -> bool {
           return isspace(c) || isdigit(c) || Puzzle::is_pusher(c) ||
                  Puzzle::is_box(c) || Puzzle::is_goal(c) ||
                  Puzzle::is_empty_floor(c) || Puzzle::is_wall(c) || c == Rle::EOL ||
                  c == Rle::GROUP_START || c == Rle::GROUP_END;
         });
}

bool Puzzle::is_sokoban_plus(const std::string &line) {
  return contains_only_digits_and_spaces(line) && !is_blank(line);
}

} // namespace io
} // namespace sokoengine
