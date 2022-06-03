#include "collection.hpp"
#include "puzzle.hpp"
#include "puzzle_types.hpp"
#include "snapshot.hpp"
#include "sok_file_format.hpp"

#include <fstream>

using namespace std;

namespace sokoengine {
namespace io {

using namespace implementation;

class LIBSOKOENGINE_LOCAL Collection::PIMPL {
public:
  string m_title;
  string m_author;
  string m_created_at;
  string m_updated_at;
  string m_notes;
  Puzzles m_puzzles;

  PIMPL(const std::string &title, const std::string &author, const std::string &notes,
        const std::string &created_at, const std::string &updated_at)
    : m_title(title),
      m_author(author),
      m_created_at(created_at),
      m_updated_at(updated_at),
      m_notes(notes) {}

  PuzzleTypes extension_to_tessellation_hint(const string &path) {
    string file_extension = path.substr(path.length() - 4, 4);
    if (file_extension == ".sok" || file_extension == ".txt" ||
        file_extension == ".xsb") {
      return PuzzleTypes::SOKOBAN;
    } else if (file_extension == ".tsb") {
      return PuzzleTypes::TRIOBAN;
    } else if (file_extension == ".hsb") {
      return PuzzleTypes::HEXOBAN;
    }
    return PuzzleTypes::SOKOBAN;
  }
};

Collection::Collection(const std::string &title, const std::string &author,
                       const std::string &notes, const std::string &created_at,
                       const std::string &updated_at)
  : m_impl(std::make_unique<Collection::PIMPL>(title, author, created_at, updated_at,
                                               notes)) {}

Collection::~Collection() = default;

const string &Collection::title() const { return m_impl->m_title; }
string &Collection::title() { return m_impl->m_title; }

const string &Collection::author() const { return m_impl->m_author; }
string &Collection::author() { return m_impl->m_author; }

const string &Collection::created_at() const { return m_impl->m_created_at; }
string &Collection::created_at() { return m_impl->m_created_at; }

const string &Collection::updated_at() const { return m_impl->m_updated_at; }
string &Collection::updated_at() { return m_impl->m_updated_at; }

const string &Collection::notes() const { return m_impl->m_notes; }
string &Collection::notes() { return m_impl->m_notes; }

const Puzzles &Collection::puzzles() const { return m_impl->m_puzzles; }
Puzzles &Collection::puzzles() { return m_impl->m_puzzles; }

void Collection::clear() {
  m_impl->m_title = m_impl->m_author = m_impl->m_created_at = m_impl->m_updated_at =
    m_impl->m_notes = "";
  m_impl->m_puzzles.clear();
}

void Collection::reformat(bool use_visible_floor, uint8_t break_long_lines_at,
                          bool rle_encode) {
  for (Puzzle &puzzle : m_impl->m_puzzles) {
    puzzle.board() =
      puzzle.reformatted(use_visible_floor, break_long_lines_at, rle_encode);
    for (Snapshot &snapshot : puzzle.snapshots()) {
      snapshot.moves() = snapshot.reformatted(break_long_lines_at, rle_encode);
    }
  }
}

bool Collection::load(const std::filesystem::path &path) {
  return load(path, m_impl->extension_to_tessellation_hint(path));
}

bool Collection::load(const std::filesystem::path &path,
                      const PuzzleTypes &puzzle_type_hint) {
  return load(path.string(), puzzle_type_hint);
}

bool Collection::load(const string &path) {
  return load(path, m_impl->extension_to_tessellation_hint(path));
}

bool Collection::load(const std::string &path, const PuzzleTypes &puzzle_type_hint) {
  ifstream input(path, ios_base::binary);
  SOKFileFormat reader;
  reader.read(input, *this, puzzle_type_hint);
  size_t id = 1;
  for (Puzzle &puzzle : m_impl->m_puzzles) {
    puzzle.id() = id++;
    size_t snapshot_id = 1;
    for (Snapshot &snapshot : puzzle.snapshots()) {
      snapshot.id() = snapshot_id++;
    }
  }
  return true;
}

bool Collection::save(const filesystem::path &path) const {
  return save(path.string());
}

bool Collection::save(const string &path) const {
  ofstream output(path, ios_base::binary);
  SOKFileFormat writer;
  return writer.write(*this, output);
}

} // namespace io
} // namespace sokoengine
