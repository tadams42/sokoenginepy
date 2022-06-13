#include "sok_file_format.hpp"

#include "collection.hpp"
#include "utilities.hpp"

#include "hexoban.hpp"
#include "octoban.hpp"
#include "sokoban.hpp"
#include "trioban.hpp"

#include <boost/algorithm/string.hpp>

using namespace std;
using namespace boost;

namespace sokoengine {
namespace io {
namespace implementation {

enum class LIBSOKOENGINE_LOCAL PuzzleTypeHints : unsigned short {
  SOKOBAN = 0,
  TRIOBAN,
  HEXOBAN,
  OCTOBAN,
  BLANK,
};

struct LIBSOKOENGINE_LOCAL SnapshotData {
  string title;
  string duration;
  string solver;
  Strings notes;
  string created_at;
  string updated_at;
  string moves_data;
};

typedef vector<SnapshotData> SnapshotsData;

struct LIBSOKOENGINE_LOCAL PuzzleData {
  string title;
  string board;
  string author;
  string boxorder;
  string goalorder;
  Strings notes;
  string created_at;
  string updated_at;
  PuzzleTypeHints puzzle_type;
  SnapshotsData snapshots;
};

typedef vector<PuzzleData> CollectionData;

static constexpr const char *TAG_AUTHOR = "author";
static constexpr const char *TAG_TITLE = "title";
static constexpr const char *TAG_GOALORDER = "goalorder";
static constexpr const char *TAG_BOXORDER = "boxorder";
static constexpr const char *TAG_SOLVER = "solver";
static constexpr const char *TAG_VARIANT = "game";
static constexpr const char *TAG_CREATED_AT = "date created";
static constexpr const char *TAG_SNAPSHOT_CREATED_AT = "date";
static constexpr const char *TAG_UPDATED_AT = "date of last change";
static constexpr const char *TAG_DURATION = "time";
static constexpr const char *MARKERS_RAW_FILE_NOTES = "::";
static constexpr const char *MARKERS_TAG_DELIMITERS = "=:";

LIBSOKOENGINE_LOCAL string &strip_and_downcase(string &line) {
  boost::trim(line);
  boost::to_lower(line);
  return line;
}

LIBSOKOENGINE_LOCAL PuzzleTypeHints puzzle_type_from_str(const string &val) {
  string vval = val;
  strip_and_downcase(vval);
  if (is_blank(val)) { return PuzzleTypeHints::BLANK; }
  if (vval == "sokoban") {
    return PuzzleTypeHints::SOKOBAN;
  } else if (vval == "trioban") {
    return PuzzleTypeHints::TRIOBAN;
  } else if (vval == "hexoban") {
    return PuzzleTypeHints::HEXOBAN;
  } else if (vval == "octoban") {
    return PuzzleTypeHints::OCTOBAN;
  } else {
    throw invalid_argument("Unknown PuzzleTypeHints " + val + "!");
  }
}

LIBSOKOENGINE_LOCAL string puzzle_type_to_str(PuzzleTypeHints val) {
  switch (val) {
  case PuzzleTypeHints::OCTOBAN:
    return string("octoban");
    break;
  case PuzzleTypeHints::TRIOBAN:
    return string("trioban");
    break;
  case PuzzleTypeHints::HEXOBAN:
    return string("hexoban");
    break;
  case PuzzleTypeHints::BLANK:
    return "";
    break;
    ;
  case PuzzleTypeHints::SOKOBAN:
  default:
    return string("sokoban");
    break;
  }
}

class LIBSOKOENGINE_LOCAL PuzzleVisitor {
  const PuzzleData &m_puzzle_data;

  void copy_puzzle_metadata(Puzzle &puzzle) {
    puzzle.title() = m_puzzle_data.title;
    puzzle.author() = m_puzzle_data.author;
    puzzle.boxorder() = m_puzzle_data.boxorder;
    puzzle.goalorder() = m_puzzle_data.goalorder;
    puzzle.notes() = m_puzzle_data.notes;
    puzzle.created_at() = m_puzzle_data.created_at;
    puzzle.updated_at() = m_puzzle_data.updated_at;
  }

  void copy_snapshot_metadata(Snapshot &snapshot, const SnapshotData &data) {
    snapshot.title() = data.title;
    snapshot.duration() = data.duration;
    snapshot.solver() = data.solver;
    snapshot.notes() = data.notes;
    snapshot.created_at() = data.created_at;
    snapshot.updated_at() = data.updated_at;
  }

public:
  PuzzleVisitor(const PuzzleData &puzzle_data) : m_puzzle_data(puzzle_data) {}
  void operator()(SokobanPuzzle &puzzle) {
    copy_puzzle_metadata(puzzle);
    for (auto &snapshot_data : m_puzzle_data.snapshots) {
      puzzle.snapshots().push_back(SokobanSnapshot(snapshot_data.moves_data));
      copy_snapshot_metadata(puzzle.snapshots().back(), snapshot_data);
    }
  }
  void operator()(TriobanPuzzle &puzzle) {
    copy_puzzle_metadata(puzzle);
    for (auto &snapshot_data : m_puzzle_data.snapshots) {
      puzzle.snapshots().push_back(TriobanSnapshot(snapshot_data.moves_data));
      copy_snapshot_metadata(puzzle.snapshots().back(), snapshot_data);
    }
  }
  void operator()(OctobanPuzzle &puzzle) {
    copy_puzzle_metadata(puzzle);
    for (auto &snapshot_data : m_puzzle_data.snapshots) {
      puzzle.snapshots().push_back(OctobanSnapshot(snapshot_data.moves_data));
      copy_snapshot_metadata(puzzle.snapshots().back(), snapshot_data);
    }
  }
  void operator()(HexobanPuzzle &puzzle) {
    copy_puzzle_metadata(puzzle);
    for (auto &snapshot_data : m_puzzle_data.snapshots) {
      puzzle.snapshots().push_back(HexobanSnapshot(snapshot_data.moves_data));
      copy_snapshot_metadata(puzzle.snapshots().back(), snapshot_data);
    }
  }
};

class LIBSOKOENGINE_LOCAL SOKReader {
  istream &m_stream;
  Collection &m_destination;
  CollectionData m_data;
  PuzzleTypeHints m_supplied_variant_hint;
  PuzzleTypeHints m_collection_header_variant_hint = PuzzleTypeHints::BLANK;
  string m_current_line;

public:
  SOKReader(istream &src, Collection &dest, const string &variant_hint)
    : m_stream(src),
      m_destination(dest),
      m_supplied_variant_hint(puzzle_type_from_str(variant_hint)) {}

  void read() {
    if (m_stream.fail()) { throw runtime_error("Unknown input stream error!"); }
    m_stream.clear();
    m_stream.seekg(0, ios_base::beg);

    m_destination.title() = m_destination.author() = m_destination.created_at() =
      m_destination.updated_at() = "";
    m_destination.notes() = Strings();
    m_destination.puzzles().clear();
    m_data.clear();

    read_collection_notes();
    read_puzzles();
    parse_title_lines();

    for (auto &puzzle_data : m_data) {
      switch (puzzle_data.puzzle_type) {
      case PuzzleTypeHints::SOKOBAN:
        m_destination.puzzles().emplace_back(SokobanPuzzle(puzzle_data.board));
        break;
      case PuzzleTypeHints::HEXOBAN:
        m_destination.puzzles().emplace_back(HexobanPuzzle(puzzle_data.board));
        break;
      case PuzzleTypeHints::TRIOBAN:
        m_destination.puzzles().emplace_back(TriobanPuzzle(puzzle_data.board));
        break;
      case PuzzleTypeHints::OCTOBAN:
        m_destination.puzzles().emplace_back(OctobanPuzzle(puzzle_data.board));
        break;
      default:
        throw std::invalid_argument("Unknown puzzle type!");
      }

      auto &puzzle_variant = m_destination.puzzles().back();
      std::visit(PuzzleVisitor(puzzle_data), puzzle_variant);
    }
  }

private:
  static void assign_to_blank(string &dest, const string &src) {
    if (is_blank(dest)) dest = src;
  }

  static void assign_to_blank(PuzzleTypeHints &dest, const string &src) {
    if (dest == PuzzleTypeHints::BLANK) { dest = puzzle_type_from_str(src); }
  }

  static bool is_tagged_as(const string &line, const string &tag_name) {
    bool contains_sokoban_tag = boost::istarts_with(boost::trim_copy(line), tag_name);
    bool contains_tag_separator =
      (line.find_first_of(MARKERS_TAG_DELIMITERS) != string::npos);
    return (contains_sokoban_tag && contains_tag_separator);
  }

  void read_collection_notes() {
    while (getline(m_stream, m_current_line) && !Puzzle::is_board(m_current_line)) {
      if (is_collection_tag_line(m_current_line)) {
        assign_to_blank(m_collection_header_variant_hint,
                        get_tag_data(m_current_line, TAG_VARIANT));
        assign_to_blank(m_destination.title(), get_tag_data(m_current_line, TAG_TITLE));
        assign_to_blank(m_destination.author(),
                        get_tag_data(m_current_line, TAG_AUTHOR));
        assign_to_blank(m_destination.created_at(),
                        get_tag_data(m_current_line, TAG_CREATED_AT));
        assign_to_blank(m_destination.updated_at(),
                        get_tag_data(m_current_line, TAG_UPDATED_AT));
      } else {
        if (!is_raw_file_notes_line(m_current_line))
          m_destination.notes().push_back(m_current_line);
      }
    }
  }

  static bool is_collection_tag_line(const string &line) {
    return is_tagged_as(line, TAG_VARIANT) || is_tagged_as(line, TAG_TITLE) ||
           is_tagged_as(line, TAG_AUTHOR) || is_tagged_as(line, TAG_CREATED_AT) ||
           is_tagged_as(line, TAG_UPDATED_AT);
  }

  string read_board() {
    Strings lines;
    if (m_stream && Puzzle::is_board(m_current_line)) {
      lines.push_back(boost::trim_right_copy(m_current_line));
      while (getline(m_stream, m_current_line) && Puzzle::is_board(m_current_line)) {
        lines.push_back(boost::trim_right_copy(m_current_line));
      }
    }
    return boost::join(lines, "\n");
  }

  void read_puzzle_notes(PuzzleData &puzzle) {
    string puzzle_variant;
    if (m_stream && !Puzzle::is_board(m_current_line) &&
        !Snapshot::is_snapshot(m_current_line)) {
      parse_puzzle_note_line(puzzle, m_current_line);
      puzzle_variant = get_tag_data(m_current_line, TAG_VARIANT);
      if (!is_puzzle_tag_line(m_current_line)) puzzle.notes.push_back(m_current_line);

      while (getline(m_stream, m_current_line) && !Puzzle::is_board(m_current_line) &&
             !Snapshot::is_snapshot(m_current_line)) {
        if (is_puzzle_tag_line(m_current_line)) {
          parse_puzzle_note_line(puzzle, m_current_line);
          assign_to_blank(puzzle_variant, get_tag_data(m_current_line, TAG_VARIANT));
        } else {
          puzzle.notes.push_back(m_current_line);
        }
      }
    }

    assign_to_blank(puzzle_variant,
                    puzzle_type_to_str(m_collection_header_variant_hint));
    assign_to_blank(puzzle_variant, puzzle_type_to_str(m_supplied_variant_hint));
    assign_to_blank(puzzle_variant, "sokoban");
    puzzle.puzzle_type = puzzle_type_from_str(puzzle_variant);
  }

  static void parse_puzzle_note_line(PuzzleData &puzzle, const string &note_line) {
    assign_to_blank(puzzle.boxorder, get_tag_data(note_line, TAG_BOXORDER));
    assign_to_blank(puzzle.goalorder, get_tag_data(note_line, TAG_GOALORDER));
    assign_to_blank(puzzle.title, get_tag_data(note_line, TAG_TITLE));
    assign_to_blank(puzzle.author, get_tag_data(note_line, TAG_AUTHOR));
  }

  static bool is_puzzle_tag_line(const string &line) {
    return is_tagged_as(line, TAG_TITLE) || is_tagged_as(line, TAG_AUTHOR) ||
           is_tagged_as(line, TAG_VARIANT) || is_tagged_as(line, TAG_BOXORDER) ||
           is_tagged_as(line, TAG_GOALORDER);
  }

  string read_moves() {
    string moves;
    if (m_stream && Snapshot::is_snapshot(m_current_line)) {
      moves = boost::trim_right_copy(m_current_line);
      while (getline(m_stream, m_current_line) &&
             Snapshot::is_snapshot(m_current_line)) {
        moves += boost::trim_right_copy(m_current_line);
      }
      boost::trim_right(moves);
    }
    return moves;
  }

  void read_snapshot_notes(SnapshotData &snapshot) {
    if (m_stream && !Puzzle::is_board(m_current_line) &&
        !Snapshot::is_snapshot(m_current_line)) {
      parse_snapshot_note_line(snapshot, m_current_line);
      if (is_snapshot_tag_line(m_current_line))
        snapshot.notes.push_back(m_current_line);

      while (getline(m_stream, m_current_line) &&
             !Snapshot::is_snapshot(m_current_line) &&
             !Puzzle::is_board(m_current_line)) {
        if (is_snapshot_tag_line(m_current_line)) {
          parse_snapshot_note_line(snapshot, m_current_line);
        } else {
          snapshot.notes.push_back(m_current_line);
        }
      }
    }
  }

  static void parse_snapshot_note_line(SnapshotData &snapshot,
                                       const string &note_line) {
    assign_to_blank(snapshot.title, get_tag_data(note_line, TAG_TITLE));
    assign_to_blank(snapshot.solver, get_tag_data(note_line, TAG_SOLVER));
    assign_to_blank(snapshot.solver, get_tag_data(note_line, TAG_AUTHOR));
    assign_to_blank(snapshot.created_at, get_tag_data(note_line, TAG_CREATED_AT));
    assign_to_blank(snapshot.created_at,
                    get_tag_data(note_line, TAG_SNAPSHOT_CREATED_AT));
    assign_to_blank(snapshot.duration, get_tag_data(note_line, TAG_DURATION));
  }

  static bool is_snapshot_tag_line(const string &line) {
    return is_tagged_as(line, TAG_TITLE) || is_tagged_as(line, TAG_AUTHOR) ||
           is_tagged_as(line, TAG_SOLVER) || is_tagged_as(line, TAG_CREATED_AT) ||
           is_tagged_as(line, TAG_SNAPSHOT_CREATED_AT) ||
           is_tagged_as(line, TAG_DURATION);
  }

  void read_puzzles() {
    bool puzzle_read = true;
    while (m_stream && puzzle_read) {
      m_data.push_back(PuzzleData());
      PuzzleData &puzzle_data = m_data.back();
      puzzle_data.board = read_board();
      read_puzzle_notes(puzzle_data);
      bool snapshot_read = true;
      while (m_stream && snapshot_read) {
        SnapshotData snapshot;
        snapshot.moves_data = read_moves();
        if (!is_blank(snapshot.moves_data)) {
          read_snapshot_notes(snapshot);
          puzzle_data.snapshots.push_back(snapshot);
        } else {
          snapshot_read = false;
        }
      }

      if (is_blank(puzzle_data.board)) {
        m_data.pop_back();
        puzzle_read = false;
      }
    }
  }

  // @verbatim
  // :: Raw File Notes                                         ::
  // ::   Raw file notes are only intended for someone looking ::
  // ::   at the raw file in a text editor. These lines begin  ::
  // ::   with "::".                                           ::
  // @endverbatim
  static bool is_raw_file_notes_line(const string &line) {
    return (boost::starts_with(line, MARKERS_RAW_FILE_NOTES));
  }

  static string get_tag_data(const string &line, const string &tag_name) {
    string retv;
    size_t delimit_pos = line.find_first_of(MARKERS_TAG_DELIMITERS);
    if (delimit_pos != string::npos) {
      string found_tag_name = line.substr(0, delimit_pos);
      if (tag_name == strip_and_downcase(found_tag_name)) {
        retv = line.substr(delimit_pos + 1, line.length());
        boost::trim(retv);
      }
    }
    return retv;
  }

  void parse_title_lines() {
    size_t i, iend = m_data.size();
    for (i = 0; i < iend; ++i) {
      auto &puzzle = m_data[i];
      if (is_blank(puzzle.title))
        puzzle.title = remove_title_line(notes_before_puzzle(i));

      size_t j, jend = puzzle.snapshots.size();
      for (j = 0; j < jend; ++j) {
        auto &snapshot = puzzle.snapshots[j];
        if (is_blank(snapshot.title))
          snapshot.title = remove_title_line(notes_before_snapshot(i, j));
      }
    }

    cleanup_whitespace(m_destination.notes());
    for (auto &puzzle : m_data) {
      cleanup_whitespace(puzzle.notes);
      for (auto &snapshot : puzzle.snapshots) {
        cleanup_whitespace(snapshot.notes);
      }
    }
  }

  Strings &notes_before_puzzle(size_t puzzle_index) {
    if (puzzle_index == 0) return m_destination.notes();
    auto &previous_puzzle = m_data[puzzle_index - 1];
    if (previous_puzzle.snapshots.size() == 0) {
      return previous_puzzle.notes;
    } else {
      return previous_puzzle.snapshots.back().notes;
    }
  }

  Strings &notes_before_snapshot(size_t puzzle_index, size_t snapshot_index) {
    auto &puzzle = m_data[puzzle_index];
    if (snapshot_index == 0) {
      return puzzle.notes;
    } else {
      return puzzle.snapshots[snapshot_index - 1].notes;
    }
  }

  // @verbatim
  // ::   Titles                                               ::
  // ::   A title line is the last non-blank text line before  ::
  // ::   a puzzle or a game, provided the line is preceded     ::
  // ::   by a blank line or it is the only text line at this  ::
  // ::   position in the file.                                ::
  // ::                                                        ::
  // ::   Title lines are optional unless a single or a last   ::
  // ::   text line from a preceding puzzle, game, or file      ::
  // ::   header can be mistaken for a title line.             ::
  // @endverbatim
  static string remove_title_line(Strings &notes) {
    auto candidate = find_if(notes.rbegin(), notes.rend(), [](const string &s) {
      return !is_blank(s) && !Puzzle::is_board(s) && !Snapshot::is_snapshot(s);
    });

    bool is_title_line = false;
    if (candidate != notes.rend()) {
      Strings::const_reverse_iterator preceding_line = candidate;
      if (preceding_line != notes.rend()) ++preceding_line;
      Strings::const_reverse_iterator following_line = candidate;
      if (following_line != notes.rbegin()) --following_line;

      bool preceding_ok = preceding_line == notes.rend()
                            ? true
                            : is_blank(*preceding_line) ||
                                Puzzle::is_board(*preceding_line) ||
                                Snapshot::is_snapshot(*preceding_line);

      bool following_ok = following_line == candidate
                            ? true
                            : is_blank(*following_line) ||
                                Puzzle::is_board(*following_line) ||
                                Snapshot::is_snapshot(*following_line);

      is_title_line =
        preceding_ok && following_ok && !is_collection_tag_line(*candidate) &&
        !is_puzzle_tag_line(*candidate) && !is_snapshot_tag_line(*candidate);
    }

    if (is_title_line) {
      string title_line = *candidate;
      boost::trim(title_line);
      notes.erase((++candidate).base());
      return title_line;
    }
    return "";
  }

  static void cleanup_whitespace(Strings &notes) {
    Strings::iterator tit;
    tit = unique(notes.begin(), notes.end(), [](const string &l, const string &r) {
      return is_blank(l) && is_blank(r);
    });
    notes.erase(tit, notes.end());

    if (notes.size() > 0 && is_blank(notes.back())) notes.pop_back();
    if (notes.size() > 0 && is_blank(notes.front())) notes.erase(notes.begin());

    for (string &line : notes) {
      boost::trim_right(line);
    }
  }
};

LIBSOKOENGINE_LOCAL static bool write_tagged(ostream &dest, string tag_name,
                                             string tag_data) {
  if (is_blank(tag_name) || is_blank(tag_data)) return false;
  tag_name[0] = toupper(tag_name[0]);
  boost::trim_right(tag_data);
  dest << tag_name << ": " << tag_data << endl;
  return (bool)dest;
}

class LIBSOKOENGINE_LOCAL PuzzleWriteVisitor {
public:
  PuzzleWriteVisitor(ostream &dest, bool &success) : m_stream(dest), retv(success) {}

  void operator()(const SokobanPuzzle &puzzle) {
    retv = write_puzzle(puzzle);
    for (const auto &snapshot : puzzle.snapshots()) {
      if (retv) { retv = write_snapshot(snapshot); }
    }
  }
  void operator()(const TriobanPuzzle &puzzle) {
    retv = write_puzzle(puzzle);
    for (const auto &snapshot : puzzle.snapshots()) {
      if (retv) { retv = write_snapshot(snapshot); }
    }
  }
  void operator()(const OctobanPuzzle &puzzle) {
    retv = write_puzzle(puzzle);
    for (const auto &snapshot : puzzle.snapshots()) {
      if (retv) { retv = write_snapshot(snapshot); }
    }
  }
  void operator()(const HexobanPuzzle &puzzle) {
    retv = write_puzzle(puzzle);
    for (const auto &snapshot : puzzle.snapshots()) {
      if (retv) { retv = write_snapshot(snapshot); }
    }
  }

private:
  ostream &m_stream;
  bool &retv;

  bool write_puzzle(const Puzzle &puzzle) {
    if (puzzle.size() == 0) return true;

    if (!is_blank(puzzle.title()))
      m_stream << boost::trim_copy(puzzle.title()) << endl << endl;

    m_stream << boost::trim_right_copy(puzzle.board()) << endl << endl;

    bool written = false;

    if (puzzle.tessellation().str() != "sokoban")
      written =
        write_tagged(m_stream, TAG_VARIANT, puzzle.tessellation().str()) || written;

    written = write_tagged(m_stream, TAG_AUTHOR, puzzle.author()) || written;
    if (!is_blank(puzzle.boxorder()) && !is_blank(puzzle.goalorder())) {
      written = write_tagged(m_stream, TAG_BOXORDER, puzzle.boxorder()) || written;
      written = write_tagged(m_stream, TAG_GOALORDER, puzzle.goalorder()) || written;
    }

    bool non_blank_found = false;
    for (const string &line : puzzle.notes()) {
      non_blank_found = non_blank_found || is_blank(line);
    }
    if (non_blank_found) {
      for (const string &line : puzzle.notes()) {
        m_stream << boost::trim_copy(line) << endl;
      }
      written = true;
    }
    if (written) m_stream << endl;

    return (bool)m_stream;
  }

  bool write_snapshot(const Snapshot &snapshot) {
    if (is_blank(snapshot.moves_data())) return true;

    if (!is_blank(snapshot.title()))
      m_stream << boost::trim_copy(snapshot.title()) << endl;

    m_stream << boost::trim_copy(snapshot.moves_data()) << endl << endl;

    bool written = false;
    written = write_tagged(m_stream, TAG_SOLVER, snapshot.solver()) || written;
    written =
      write_tagged(m_stream, TAG_SNAPSHOT_CREATED_AT, snapshot.created_at()) || written;
    written = write_tagged(m_stream, TAG_DURATION, snapshot.duration()) || written;

    bool non_blank_found = false;
    for (const string &line : snapshot.notes()) {
      non_blank_found = non_blank_found || is_blank(line);
    }
    if (non_blank_found) {
      for (const string &line : snapshot.notes()) {
        m_stream << boost::trim_copy(line) << endl;
      }
      written = true;
    }
    if (written) m_stream << endl;

    return (bool)m_stream;
  }
};

class LIBSOKOENGINE_LOCAL SOKWriter {
  ostream &m_stream;

public:
  SOKWriter(ostream &dest) : m_stream(dest) {
    if (dest.fail()) { throw runtime_error("Unknown output stream error!"); }
  }

  bool write(const Collection &collection) {
    bool retv = write_collection_header(collection);
    for (const auto &puzzle_variant : collection.puzzles()) {
      if (retv) { std::visit(PuzzleWriteVisitor(m_stream, retv), puzzle_variant); }
    }
    return retv;
  }

private:
  bool write_collection_header(const Collection &collection) {
#include "SOK_format_specification.h"

    m_stream << SOK_format_specification_res;

    bool write_created_at =
      write_tagged(m_stream, TAG_CREATED_AT, collection.created_at());
    bool write_updated_at =
      write_tagged(m_stream, TAG_UPDATED_AT, collection.updated_at());

    if (write_created_at || write_updated_at) {
      m_stream << "::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::" << endl
               << endl;
    } else {
      m_stream << endl;
    }

    bool written = false;
    written = write_tagged(m_stream, TAG_AUTHOR, collection.author()) || written;
    written = write_tagged(m_stream, TAG_TITLE, collection.title()) || written;

    bool non_blank_found = false;
    for (const string &line : collection.notes()) {
      non_blank_found = non_blank_found || is_blank(line);
    }
    if (non_blank_found) {
      for (const string &line : collection.notes()) {
        m_stream << boost::trim_copy(line) << endl;
      }
      written = true;
    }

    if (written) m_stream << endl;

    return (bool)m_stream;
  }
};

SOKFileFormat::~SOKFileFormat() {}

void SOKFileFormat::read(istream &src, Collection &dest, const string &variant_hint) {
  SOKReader reader(src, dest, variant_hint);
  reader.read();
}

bool SOKFileFormat::write(const Collection &collection, std::ostream &dest) {
  SOKWriter writer(dest);
  return writer.write(collection);
}

} // namespace implementation
} // namespace io
} // namespace sokoengine
