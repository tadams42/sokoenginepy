#include "collection.hpp"

#include "hexoban.hpp"
#include "octoban.hpp"
#include "sokoban.hpp"
#include "trioban.hpp"

#include "sok_file_format.hpp"

#include <boost/algorithm/string.hpp>
#include <fstream>
#include <sstream>

namespace sokoengine {
namespace io {

using game::Tessellation;
using implementation::SOKFileFormat;
using std::ifstream;
using std::ios_base;
using std::istream;
using std::istringstream;
using std::make_unique;
using std::ofstream;
using std::ostream;
using std::ostringstream;
using std::string;
using std::filesystem::path;

class LIBSOKOENGINE_LOCAL Collection::PIMPL {
public:
  string  m_title;
  string  m_author;
  string  m_created_at;
  string  m_updated_at;
  string  m_notes;
  Puzzles m_puzzles;

  PIMPL(
    const string &title,
    const string &author,
    const string &notes,
    const string &created_at,
    const string &updated_at
  )
    : m_title(title)
    , m_author(author)
    , m_created_at(created_at)
    , m_updated_at(updated_at)
    , m_notes(notes) {}
};

Collection::Collection(
  const string &title,
  const string &author,
  const string &created_at,
  const string &updated_at,
  const string &notes
)
  : m_impl(make_unique<Collection::PIMPL>(title, author, notes, created_at, updated_at)
  ) {}

Collection::Collection(const Collection &rv)
  : m_impl(make_unique<PIMPL>(*rv.m_impl)) {}

Collection &Collection::operator=(const Collection &rv) {
  if (this != &rv) {
    m_impl = make_unique<PIMPL>(*rv.m_impl);
  }
  return *this;
}

Collection::Collection(Collection &&rv) = default;

Collection &Collection::operator=(Collection &&rv) = default;

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

void Collection::load(const path &p, Tessellation tessellation_hint) {
  load(p.string(), tessellation_hint);
}

void Collection::load(const string &path, Tessellation tessellation_hint) {
  ifstream input(path, ios_base::binary);
  load(input, tessellation_hint);
}

void Collection::load(istream &data, Tessellation tessellation_hint) {
  SOKFileFormat reader;
  reader.read(data, *this, tessellation_hint);
}

void Collection::loads(const string &data, Tessellation tessellation_hint) {
  istringstream input(data);
  load(input, tessellation_hint);
}

void Collection::dump(const path &p) const { return dump(p.string()); }

void Collection::dump(const string &path) const {
  ofstream output(path, ios_base::binary);
  dump(output);
}

void Collection::dump(std::ostream &dest) const {
  SOKFileFormat writer;
  writer.write(*this, dest);
}

string Collection::dumps() const {
  ostringstream out;
  dump(out);
  return out.str();
}

} // namespace io
} // namespace sokoengine
