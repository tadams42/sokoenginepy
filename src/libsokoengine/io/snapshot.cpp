#include "snapshot.hpp"
#include "puzzle_types.hpp"
#include "rle.hpp"
#include "utilities.hpp"

#include <algorithm>

using namespace std;

namespace sokoengine {
namespace io {

using namespace implementation;

class LIBSOKOENGINE_LOCAL Snapshot::PIMPL {
public:
  size_t m_id;
  string m_moves;
  string m_title;
  string m_created_at;
  string m_updated_at;
  string m_duration;
  string m_solver;
  string m_notes;
  PuzzleTypes m_puzzle_type;

  PIMPL(size_t id, const std::string &moves, const std::string &title,
        const std::string &created_at, const std::string &updated_at,
        const std::string &duration, const std::string &solver,
        const std::string &notes, const PuzzleTypes &puzzle_type)
    : m_id(id),
      m_moves(moves),
      m_title(title),
      m_created_at(created_at),
      m_updated_at(updated_at),
      m_duration(duration),
      m_solver(solver),
      m_notes(notes),
      m_puzzle_type(puzzle_type) {}
};

Snapshot::Snapshot(size_t id, const std::string &moves, const std::string &title,
                   const std::string &created_at, const std::string &updated_at,
                   const std::string &duration, const std::string &solver,
                   const std::string &notes, const PuzzleTypes &puzzle_type)
  : m_impl(std::make_unique<Snapshot::PIMPL>(id, moves, title, created_at, updated_at,
                                             duration, solver, notes, puzzle_type)) {}

Snapshot::Snapshot(const Snapshot &rv)
  : m_impl(std::make_unique<Snapshot::PIMPL>(
      rv.m_impl->m_id, rv.m_impl->m_moves, rv.m_impl->m_title, rv.m_impl->m_created_at,
      rv.m_impl->m_updated_at, rv.m_impl->m_duration, rv.m_impl->m_solver,
      rv.m_impl->m_notes, rv.m_impl->m_puzzle_type)) {}

Snapshot &Snapshot::operator=(const Snapshot &rv) {
  m_impl->m_id = rv.m_impl->m_id;
  m_impl->m_moves = rv.m_impl->m_moves;
  m_impl->m_title = rv.m_impl->m_title;
  m_impl->m_created_at = rv.m_impl->m_created_at;
  m_impl->m_updated_at = rv.m_impl->m_updated_at;
  m_impl->m_duration = rv.m_impl->m_duration;
  m_impl->m_solver = rv.m_impl->m_solver;
  m_impl->m_notes = rv.m_impl->m_notes;
  m_impl->m_puzzle_type = rv.m_impl->m_puzzle_type;

  return *this;
}

Snapshot::~Snapshot() = default;

const string &Snapshot::moves() const { return m_impl->m_moves; }
string &Snapshot::moves() { return m_impl->m_moves; }

const string &Snapshot::title() const { return m_impl->m_title; }
string &Snapshot::title() { return m_impl->m_title; }

const string &Snapshot::created_at() const { return m_impl->m_created_at; }
string &Snapshot::created_at() { return m_impl->m_created_at; }

const string &Snapshot::updated_at() const { return m_impl->m_updated_at; }
string &Snapshot::updated_at() { return m_impl->m_updated_at; }

const string &Snapshot::duration() const { return m_impl->m_duration; }
string &Snapshot::duration() { return m_impl->m_duration; }

const string &Snapshot::solver() const { return m_impl->m_solver; }
string &Snapshot::solver() { return m_impl->m_solver; }

const string &Snapshot::notes() const { return m_impl->m_notes; }
string &Snapshot::notes() { return m_impl->m_notes; }

size_t Snapshot::id() const { return m_impl->m_id; }
size_t &Snapshot::id() { return m_impl->m_id; }

PuzzleTypes Snapshot::puzzle_type() const { return m_impl->m_puzzle_type; }
PuzzleTypes &Snapshot::puzzle_type() { return m_impl->m_puzzle_type; }

void Snapshot::clear() {
  m_impl->m_moves = m_impl->m_title = m_impl->m_created_at = m_impl->m_updated_at =
    m_impl->m_duration = m_impl->m_solver = m_impl->m_notes = "";
  m_impl->m_id = 1;
  m_impl->m_puzzle_type = PuzzleTypes::SOKOBAN;
}

size_t Snapshot::pushes_count() const {
  return count_if(m_impl->m_moves.cbegin(), m_impl->m_moves.cend(),
                  [](char c) { return isupper(c); });
}

///
/// This is just an approximation. Since snapshot is not fully parsed, this method may
/// also count pusher steps that are part of jumps and / or pusher selections.
///
size_t Snapshot::moves_count() const {
  return count_if(m_impl->m_moves.cbegin(), m_impl->m_moves.cend(),
                  [](char c) { return islower(c); });
}

bool Snapshot::is_reverse() const {
  return any_of(m_impl->m_moves.cbegin(), m_impl->m_moves.cend(), [](char c) {
    return c == Snapshot::JUMP_BEGIN || c == Snapshot::JUMP_END;
  });
}

std::string Snapshot::reformatted(uint8_t break_long_lines_at, bool rle_encode) const {
  return m_impl->m_moves;
}

bool Snapshot::is_snapshot(const std::string &line) {
  return !contains_only_digits_and_spaces(line) &&
         all_of(line.begin(), line.end(), [](char c) -> bool {
           return isdigit(c) || Snapshot::is_pusher_step(c) || c == Rle::EOL ||
                  c == Rle::GROUP_START || c == Rle::GROUP_END;
         });
}

string Snapshot::cleaned_moves(const std::string& line) {
  if (!Snapshot::is_snapshot(line)) {
    throw std::invalid_argument("Illegal characters found in snapshot string");
  }

  return Rle::decode(line);
}

} // namespace io
} // namespace sokoengine
