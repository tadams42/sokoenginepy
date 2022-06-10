#include "collection.hpp"

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
  Strings m_notes;
  Puzzles m_puzzles;

  PIMPL(const string &title, const string &author, const Strings &notes,
        const string &created_at, const string &updated_at)
    : m_title(title),
      m_author(author),
      m_created_at(created_at),
      m_updated_at(updated_at),
      m_notes(notes) {}

  string extension_to_tessellation_hint(const string &path) {
    string file_extension = path.substr(path.length() - 4, 4);
    if (file_extension == ".sok" || file_extension == ".txt" ||
        file_extension == ".xsb") {
      return "sokoban";
    } else if (file_extension == ".tsb") {
      return "trioban";
    } else if (file_extension == ".hsb") {
      return "hexoban";
    }
    return "sokoban";
  }
};

Collection::Collection(const string &title, const string &author,
                       const string &created_at, const string &updated_at,
                       const Strings &notes)
  : m_impl(
      make_unique<Collection::PIMPL>(title, author, notes, created_at, updated_at)) {}

Collection::~Collection() = default;

const string &Collection::title() const { return m_impl->m_title; }
string &Collection::title() { return m_impl->m_title; }

const string &Collection::author() const { return m_impl->m_author; }
string &Collection::author() { return m_impl->m_author; }

const string &Collection::created_at() const { return m_impl->m_created_at; }
string &Collection::created_at() { return m_impl->m_created_at; }

const string &Collection::updated_at() const { return m_impl->m_updated_at; }
string &Collection::updated_at() { return m_impl->m_updated_at; }

const Strings &Collection::notes() const { return m_impl->m_notes; }
Strings &Collection::notes() { return m_impl->m_notes; }

const Puzzles &Collection::puzzles() const { return m_impl->m_puzzles; }
Puzzles &Collection::puzzles() { return m_impl->m_puzzles; }

bool Collection::load(const filesystem::path &path) {
  return load(path, m_impl->extension_to_tessellation_hint(path));
}

bool Collection::load(const filesystem::path &path, const string &puzzle_type_hint) {
  return load(path.string(), puzzle_type_hint);
}

bool Collection::load(const string &path) {
  return load(path, m_impl->extension_to_tessellation_hint(path));
}

bool Collection::load(const string &path, const string &puzzle_type_hint) {
  ifstream input(path, ios_base::binary);
  SOKFileFormat reader;
  reader.read(input, *this, puzzle_type_hint);
  size_t id = 1;

  for (auto &puzzle_variant : m_impl->m_puzzles) {
    visit(
      [&id](auto &puzzle) {
        puzzle.id() = id++;

        size_t snapshot_id = 1;
        for (Snapshot &snapshot : puzzle.snapshots()) {
          snapshot.id() = snapshot_id++;
        }
      },
      puzzle_variant);
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
