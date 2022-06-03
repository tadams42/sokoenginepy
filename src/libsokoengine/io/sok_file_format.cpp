#include "sok_file_format.hpp"

#include "collection.hpp"
#include "puzzle.hpp"
#include "snapshot.hpp"
#include "utilities.hpp"

#include <boost/algorithm/string.hpp>

using namespace std;
using namespace boost;

namespace sokoengine {
namespace io {
namespace implementation {

constexpr static const char *TAG_AUTHOR = "author";
constexpr static const char *TAG_TITLE = "title";
constexpr static const char *TAG_GOALORDER = "goalorder";
constexpr static const char *TAG_BOXORDER = "boxorder";
constexpr static const char *TAG_SOLVER = "solver";
constexpr static const char *TAG_VARIANT = "game";
constexpr static const char *TAG_CREATED_AT = "date created";
constexpr static const char *TAG_SNAPSHOT_CREATED_AT = "date";
constexpr static const char *TAG_UPDATED_AT = "date of last change";
constexpr static const char *TAG_DURATION = "time";
constexpr static const char *MARKERS_RAW_FILE_NOTES = "::";
constexpr static const char *MARKERS_TAG_DELIMITERS = "=:";

LIBSOKOENGINE_LOCAL string &strip_and_downcase(string &line) {
  boost::trim(line);
  boost::to_lower(line);
  return line;
}

LIBSOKOENGINE_LOCAL PuzzleTypes puzzle_type_from_str(string &val) {
  strip_and_downcase(val);
  if (val == "sokoban") {
    return PuzzleTypes::SOKOBAN;
  } else if (val == "trioban") {
    return PuzzleTypes::TRIOBAN;
  } else if (val == "hexoban") {
    return PuzzleTypes::HEXOBAN;
  } else if (val == "octoban") {
    return PuzzleTypes::OCTOBAN;
  } else {
    throw invalid_argument("Unknown PuzzleType " + val + "!");
  }
}

LIBSOKOENGINE_LOCAL string puzzle_type_to_str(PuzzleTypes val) {
  switch (val) {
  case PuzzleTypes::OCTOBAN:
    return string("octoban");
    break;
  case PuzzleTypes::TRIOBAN:
    return string("trioban");
    break;
  case PuzzleTypes::HEXOBAN:
    return string("sokoban");
    break;
  case PuzzleTypes::SOKOBAN:
  default:
    return string("sokoban");
    break;
  }
}

class LIBSOKOENGINE_LOCAL SOKReader {
  istream &m_stream;
  Collection &m_collection;
  string m_supplied_variant_hint;
  string m_collection_header_variant_hint;
  string m_current_line;

public:
  SOKReader(istream &src, Collection &dest, const PuzzleTypes &variant_hint)
    : m_stream(src),
      m_collection(dest),
      m_supplied_variant_hint(puzzle_type_to_str(variant_hint)) {}

  void read() {
    if (m_stream.fail()) { throw runtime_error("Unknown input stream error!"); }
    m_stream.clear();
    m_stream.seekg(0, ios_base::beg);
    m_collection.clear();

    read_collection_notes();
    read_puzzles();
    parse_title_lines();
  }

private:
  void assign_to_blank(string &dest, const string &src) const {
    if (is_blank(dest)) dest = src;
  }

  bool is_tagged_as(const string &line, const string &tag_name) const {
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
        assign_to_blank(m_collection.title(), get_tag_data(m_current_line, TAG_TITLE));
        assign_to_blank(m_collection.author(),
                        get_tag_data(m_current_line, TAG_AUTHOR));
        assign_to_blank(m_collection.created_at(),
                        get_tag_data(m_current_line, TAG_CREATED_AT));
        assign_to_blank(m_collection.updated_at(),
                        get_tag_data(m_current_line, TAG_UPDATED_AT));
      } else {
        if (!is_raw_file_notes_line(m_current_line))
          m_collection.notes() += m_current_line + "\n";
      }
    }
    strip_and_downcase(m_collection_header_variant_hint);
  }

  bool is_collection_tag_line(const string &line) const {
    return is_tagged_as(line, TAG_VARIANT) || is_tagged_as(line, TAG_TITLE) ||
           is_tagged_as(line, TAG_AUTHOR) || is_tagged_as(line, TAG_CREATED_AT) ||
           is_tagged_as(line, TAG_UPDATED_AT);
  }

  string read_board() {
    string board;
    if (m_stream && Puzzle::is_board(m_current_line)) {
      board = boost::trim_right_copy(m_current_line) + "\n";
      while (getline(m_stream, m_current_line) && Puzzle::is_board(m_current_line)) {
        board += boost::trim_right_copy(m_current_line) + "\n";
      }
    }
    return board;
  }

  void read_puzzle_notes(Puzzle &puzzle) {
    string puzzle_variant;
    if (m_stream && !Puzzle::is_board(m_current_line) &&
        !Snapshot::is_snapshot(m_current_line)) {
      parse_puzzle_note_line(puzzle, m_current_line);
      puzzle_variant = get_tag_data(m_current_line, TAG_VARIANT);
      if (!is_puzzle_tag_line(m_current_line)) puzzle.notes() += m_current_line + "\n";

      while (getline(m_stream, m_current_line) && !Puzzle::is_board(m_current_line) &&
             !Snapshot::is_snapshot(m_current_line)) {
        if (is_puzzle_tag_line(m_current_line)) {
          parse_puzzle_note_line(puzzle, m_current_line);
          assign_to_blank(puzzle_variant, get_tag_data(m_current_line, TAG_VARIANT));
        } else {
          puzzle.notes() += m_current_line + "\n";
        }
      }
    }
    assign_to_blank(puzzle_variant, m_collection_header_variant_hint);
    assign_to_blank(puzzle_variant, m_supplied_variant_hint);
    assign_to_blank(puzzle_variant, "sokoban");
    puzzle.puzzle_type() = puzzle_type_from_str(strip_and_downcase(puzzle_variant));
  }

  void parse_puzzle_note_line(Puzzle &puzzle, const string &note_line) {
    assign_to_blank(puzzle.boxorder(), get_tag_data(note_line, TAG_BOXORDER));
    assign_to_blank(puzzle.goalorder(), get_tag_data(note_line, TAG_GOALORDER));
    assign_to_blank(puzzle.title(), get_tag_data(note_line, TAG_TITLE));
    assign_to_blank(puzzle.author(), get_tag_data(note_line, TAG_AUTHOR));
  }

  bool is_puzzle_tag_line(const string &line) const {
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

  void read_snapshot_notes(Snapshot &snapshot) {
    if (m_stream && !Puzzle::is_board(m_current_line) &&
        !Snapshot::is_snapshot(m_current_line)) {
      parse_snapshot_note_line(snapshot, m_current_line);
      if (is_snapshot_tag_line(m_current_line))
        snapshot.notes() += m_current_line + "\n";

      while (getline(m_stream, m_current_line) &&
             !Snapshot::is_snapshot(m_current_line) &&
             !Puzzle::is_board(m_current_line)) {
        if (is_snapshot_tag_line(m_current_line)) {
          parse_snapshot_note_line(snapshot, m_current_line);
        } else {
          snapshot.notes() += m_current_line + "\n";
        }
      }
    }
  }

  void parse_snapshot_note_line(Snapshot &snapshot, const string &note_line) {
    assign_to_blank(snapshot.title(), get_tag_data(note_line, TAG_TITLE));
    assign_to_blank(snapshot.solver(), get_tag_data(note_line, TAG_SOLVER));
    assign_to_blank(snapshot.solver(), get_tag_data(note_line, TAG_AUTHOR));
    assign_to_blank(snapshot.created_at(), get_tag_data(note_line, TAG_CREATED_AT));
    assign_to_blank(snapshot.created_at(),
                    get_tag_data(note_line, TAG_SNAPSHOT_CREATED_AT));
    assign_to_blank(snapshot.duration(), get_tag_data(note_line, TAG_DURATION));
  }

  bool is_snapshot_tag_line(const string &line) const {
    return is_tagged_as(line, TAG_TITLE) || is_tagged_as(line, TAG_AUTHOR) ||
           is_tagged_as(line, TAG_SOLVER) || is_tagged_as(line, TAG_CREATED_AT) ||
           is_tagged_as(line, TAG_SNAPSHOT_CREATED_AT) ||
           is_tagged_as(line, TAG_DURATION);
  }

  void read_puzzles() {
    bool puzzle_read = true;
    while (m_stream && puzzle_read) {
      Puzzle puzzle;
      puzzle.board() = read_board();
      read_puzzle_notes(puzzle);
      bool snapshot_read = true;
      while (m_stream && snapshot_read) {
        Snapshot snapshot;
        snapshot.moves() = read_moves();
        if (!is_blank(snapshot.moves())) {
          read_snapshot_notes(snapshot);
          puzzle.snapshots().push_back(snapshot);
        } else {
          snapshot_read = false;
        }
      }
      if (!is_blank(puzzle.board())) {
        m_collection.puzzles().push_back(puzzle);
      } else {
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
  bool is_raw_file_notes_line(const string &line) const {
    return (boost::starts_with(line, MARKERS_RAW_FILE_NOTES));
  }

  string get_tag_data(const string &line, const string &tag_name) const {
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
    size_t i, iend = m_collection.puzzles().size();
    for (i = 0; i < iend; ++i) {
      Puzzle &puzzle = m_collection.puzzles()[i];
      if (is_blank(puzzle.title()))
        puzzle.title() = remove_title_line(notes_before_puzzle(i));
      size_t j, jend = puzzle.snapshots().size();
      for (j = 0; j < jend; ++j) {
        Snapshot &snapshot = puzzle.snapshots()[j];
        if (is_blank(snapshot.title()))
          snapshot.title() = remove_title_line(notes_before_snapshot(i, j));
      }
    }

    cleanup_whitespace(m_collection.notes());
    for (Puzzle &puzzle : m_collection.puzzles()) {
      cleanup_whitespace(puzzle.notes());
      for (Snapshot &snapshot : puzzle.snapshots()) {
        cleanup_whitespace(snapshot.notes());
      }
    }
  }

  string &notes_before_puzzle(size_t puzzle_index) {
    if (puzzle_index == 0) return m_collection.notes();
    Puzzle &previous_puzzle = m_collection.puzzles()[puzzle_index - 1];
    if (previous_puzzle.snapshots().size() == 0) return previous_puzzle.notes();
    return previous_puzzle.snapshots().back().notes();
  }

  string &notes_before_snapshot(size_t puzzle_index, size_t snapshot_index) {
    Puzzle &puzzle = m_collection.puzzles()[puzzle_index];
    if (snapshot_index == 0) return puzzle.notes();
    return puzzle.snapshots()[snapshot_index - 1].notes();
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
  string remove_title_line(string &src_notes) {
    Strings notes;
    boost::split(notes, src_notes, boost::is_any_of("\n"));
    auto candidate = find_if(notes.rbegin(), notes.rend(), [](const string &s) {
      return !is_blank(s) && !Puzzle::is_board(s) && !Snapshot::is_snapshot(s);
    });

    bool is_title_line = false;
    if (candidate != notes.rend()) {
      Strings::const_reverse_iterator preceeding_line = candidate;
      if (preceeding_line != notes.rend()) ++preceeding_line;
      Strings::const_reverse_iterator following_line = candidate;
      if (following_line != notes.rbegin()) --following_line;

      bool preceeding_ok = preceeding_line == notes.rend()
                             ? true
                             : is_blank(*preceeding_line) ||
                                 Puzzle::is_board(*preceeding_line) ||
                                 Snapshot::is_snapshot(*preceeding_line);

      bool following_ok = following_line == candidate
                            ? true
                            : is_blank(*following_line) ||
                                Puzzle::is_board(*following_line) ||
                                Snapshot::is_snapshot(*following_line);

      is_title_line =
        preceeding_ok && following_ok && !is_collection_tag_line(*candidate) &&
        !is_puzzle_tag_line(*candidate) && !is_snapshot_tag_line(*candidate);
    }

    if (is_title_line) {
      string title_line = *candidate;
      boost::trim(title_line);
      notes.erase((++candidate).base());
      src_notes = join(notes, "\n");
      return title_line;
    }
    return "";
  }

  void cleanup_whitespace(string &notes) const {
    Strings lines;
    boost::split(lines, notes, boost::is_any_of("\n"));

    Strings::iterator tit;
    tit = unique(lines.begin(), lines.end(), [](const string &l, const string &r) {
      return is_blank(l) && is_blank(r);
    });
    lines.erase(tit, lines.end());

    if (lines.size() > 0 && is_blank(lines.back())) lines.pop_back();
    if (lines.size() > 0 && is_blank(lines.front())) lines.erase(lines.begin());

    for (string &line : lines) {
      boost::trim_right(line);
    }
    notes = join(lines, "\n");
    boost::trim_right(notes);
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
    if (retv) {
      for (const Puzzle &puzzle : collection.puzzles()) {
        retv = write(puzzle);
      }
    }
    return retv;
  }

  bool write(const Puzzle &puzzle) {
    if (is_blank(puzzle.board())) return true;

    if (!is_blank(puzzle.title()))
      m_stream << boost::trim_copy(puzzle.title()) << endl << endl;

    m_stream << boost::trim_right_copy(puzzle.board()) << endl << endl;

    bool written = false;

    if (puzzle.puzzle_type() != PuzzleTypes::SOKOBAN)
      written = write_tagged(TAG_VARIANT, puzzle_type_to_str(puzzle.puzzle_type())) ||
                written;

    written = write_tagged(TAG_AUTHOR, puzzle.author()) || written;
    if (!is_blank(puzzle.boxorder()) && !is_blank(puzzle.goalorder())) {
      written = write_tagged(TAG_BOXORDER, puzzle.boxorder()) || written;
      written = write_tagged(TAG_GOALORDER, puzzle.goalorder()) || written;
    }
    if (!is_blank(puzzle.notes())) {
      m_stream << boost::trim_copy(puzzle.notes()) << endl;
      written = true;
    }
    if (written) m_stream << endl;

    for (const Snapshot &snapshot : puzzle.snapshots()) {
      write_snapshot(snapshot);
    }
    return (bool)m_stream;
  }

private:
  bool write_tagged(string tag_name, string tag_data) {
    if (is_blank(tag_name) || is_blank(tag_data)) return false;
    tag_name[0] = toupper(tag_name[0]);
    boost::trim_right(tag_data);
    m_stream << tag_name << ": " << tag_data << endl;
    return (bool)m_stream;
  }

  bool write_collection_header(const Collection &collection) {
#include "SOK_format_specification.h"

    m_stream << SOK_format_specification_res;

    bool write_created_at = write_tagged(TAG_CREATED_AT, collection.created_at());
    bool write_updated_at = write_tagged(TAG_UPDATED_AT, collection.updated_at());

    if (write_created_at || write_updated_at) {
      m_stream << "::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::" << endl
               << endl;
    } else {
      m_stream << endl;
    }

    bool written = false;
    written = write_tagged(TAG_AUTHOR, collection.author()) || written;
    written = write_tagged(TAG_TITLE, collection.title()) || written;

    if (!is_blank(collection.notes())) {
      m_stream << boost::trim_copy(collection.notes()) << endl;
      written = true;
    }
    if (written) m_stream << endl;

    return (bool)m_stream;
  }

  bool write_snapshot(const Snapshot &snapshot) {
    if (is_blank(snapshot.moves())) return true;

    if (!is_blank(snapshot.title()))
      m_stream << boost::trim_copy(snapshot.title()) << endl;

    m_stream << boost::trim_copy(snapshot.moves()) << endl << endl;

    bool written = false;
    written = write_tagged(TAG_SOLVER, snapshot.solver()) || written;
    written = write_tagged(TAG_SNAPSHOT_CREATED_AT, snapshot.created_at()) || written;
    written = write_tagged(TAG_DURATION, snapshot.duration()) || written;
    if (!is_blank(snapshot.notes())) {
      m_stream << boost::trim_copy(snapshot.notes()) << endl;
      written = true;
    }
    if (written) m_stream << endl;

    return (bool)m_stream;
  }
};

SOKFileFormat::~SOKFileFormat() {}

void SOKFileFormat::read(istream &src, Collection &dest,
                         const PuzzleTypes &variant_hint) {
  SOKReader reader(src, dest, variant_hint);
  reader.read();
}

bool SOKFileFormat::write(const Puzzle &puzzle, std::ostream &dest) {
  SOKWriter writer(dest);
  return writer.write(puzzle);
}

bool SOKFileFormat::write(const Collection &collection, std::ostream &dest) {
  SOKWriter writer(dest);
  return writer.write(collection);
}

} // namespace implementation
} // namespace io
} // namespace sokoengine
