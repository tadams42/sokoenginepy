#include "sok_file_format.hpp"

#include "collection.hpp"
#include "puzzle.hpp"
#include "snapshot.hpp"
#include "utilities.hpp"

#include <boost/algorithm/string.hpp>
#include <vector>

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

struct LIBSOKOENGINE_LOCAL PuzzleData {
  size_t id;
  string title;
  string board;
  string author;
  string boxorder;
  string goalorder;
  Strings notes;
  string created_at;
  string updated_at;
  PuzzleTypeHints puzzle_type;
  Snapshots snapshots;
};

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

class LIBSOKOENGINE_LOCAL SOKReader {
  istream &m_stream;
  Collection &m_collection;
  PuzzleTypeHints m_supplied_variant_hint;
  PuzzleTypeHints m_collection_header_variant_hint = PuzzleTypeHints::BLANK;
  string m_current_line;

public:
  SOKReader(istream &src, Collection &dest, const string &variant_hint)
    : m_stream(src),
      m_collection(dest),
      m_supplied_variant_hint(puzzle_type_from_str(variant_hint)) {}

  void read() {
    if (m_stream.fail()) { throw runtime_error("Unknown input stream error!"); }
    m_stream.clear();
    m_stream.seekg(0, ios_base::beg);

    m_collection.title() = m_collection.author() = m_collection.created_at() =
      m_collection.updated_at() = "";
    m_collection.notes() = Strings();
    m_collection.puzzles().clear();

    read_collection_notes();
    read_puzzles();
    parse_title_lines();
  }

private:
  void assign_to_blank(string &dest, const string &src) const {
    if (is_blank(dest)) dest = src;
  }

  void assign_to_blank(PuzzleTypeHints &dest, const string &src) const {
    if (dest == PuzzleTypeHints::BLANK) { dest = puzzle_type_from_str(src); }
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
          m_collection.notes().push_back(m_current_line);
      }
    }
  }

  bool is_collection_tag_line(const string &line) const {
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

  void parse_puzzle_note_line(PuzzleData &puzzle, const string &note_line) {
    assign_to_blank(puzzle.boxorder, get_tag_data(note_line, TAG_BOXORDER));
    assign_to_blank(puzzle.goalorder, get_tag_data(note_line, TAG_GOALORDER));
    assign_to_blank(puzzle.title, get_tag_data(note_line, TAG_TITLE));
    assign_to_blank(puzzle.author, get_tag_data(note_line, TAG_AUTHOR));
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
        snapshot.notes().push_back(m_current_line);

      while (getline(m_stream, m_current_line) &&
             !Snapshot::is_snapshot(m_current_line) &&
             !Puzzle::is_board(m_current_line)) {
        if (is_snapshot_tag_line(m_current_line)) {
          parse_snapshot_note_line(snapshot, m_current_line);
        } else {
          snapshot.notes().push_back(m_current_line);
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
      PuzzleData puzzle_data;
      puzzle_data.board = read_board();
      read_puzzle_notes(puzzle_data);
      bool snapshot_read = true;
      while (m_stream && snapshot_read) {
        Snapshot snapshot;
        snapshot.moves() = read_moves();
        if (!is_blank(snapshot.moves())) {
          read_snapshot_notes(snapshot);
          puzzle_data.snapshots.push_back(snapshot);
        } else {
          snapshot_read = false;
        }
      }
      if (!is_blank(puzzle_data.board)) {
        switch (puzzle_data.puzzle_type) {
        case PuzzleTypeHints::SOKOBAN:
          m_collection.puzzles().emplace_back(SokobanPuzzle(puzzle_data.board));
          break;
        case PuzzleTypeHints::HEXOBAN:
          m_collection.puzzles().emplace_back(HexobanPuzzle(puzzle_data.board));
          break;
        case PuzzleTypeHints::TRIOBAN:
          m_collection.puzzles().emplace_back(TriobanPuzzle(puzzle_data.board));
          break;
        case PuzzleTypeHints::OCTOBAN:
          m_collection.puzzles().emplace_back(OctobanPuzzle(puzzle_data.board));
          break;
        default:
          throw std::invalid_argument("Unknown puzzle type!");
        }

        auto &puzzle_variant = m_collection.puzzles().back();
        std::visit(
          [&puzzle_data](auto &puzzle) {
            puzzle.id() = puzzle_data.id;
            puzzle.title() = puzzle_data.title;
            puzzle.author() = puzzle_data.author;
            puzzle.boxorder() = puzzle_data.boxorder;
            puzzle.goalorder() = puzzle_data.goalorder;
            puzzle.notes() = puzzle_data.notes;
            puzzle.created_at() = puzzle_data.created_at;
            puzzle.updated_at() = puzzle_data.updated_at;
            puzzle.snapshots() = puzzle_data.snapshots;
          },
          puzzle_variant);
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
      auto &puzzle_variant = m_collection.puzzles()[i];

      std::visit(
        [this, i](auto &puzzle) {
          if (is_blank(puzzle.title()))
            puzzle.title() = remove_title_line(notes_before_puzzle(i));
          size_t j, jend = puzzle.snapshots().size();
          for (j = 0; j < jend; ++j) {
            Snapshot &snapshot = puzzle.snapshots()[j];
            if (is_blank(snapshot.title()))
              snapshot.title() = remove_title_line(notes_before_snapshot(i, j));
          }
        },
        puzzle_variant);
    }

    cleanup_whitespace(m_collection.notes());

    for (auto &puzzle_variant : m_collection.puzzles()) {
      std::visit(
        [this](auto &puzzle) {
          cleanup_whitespace(puzzle.notes());
          for (Snapshot &snapshot : puzzle.snapshots()) {
            cleanup_whitespace(snapshot.notes());
          }
        },
        puzzle_variant);
    }
  }

  Strings &notes_before_puzzle(size_t puzzle_index) {
    if (puzzle_index == 0) return m_collection.notes();

    auto &previous_puzzle_variant = m_collection.puzzles()[puzzle_index - 1];

    Strings *retv = nullptr;
    std::visit(
      [&retv](auto &previous_puzzle) {
        if (previous_puzzle.snapshots().size() == 0)
          retv = &(previous_puzzle.notes());
        else
          retv = &(previous_puzzle.snapshots().back().notes());
      },
      previous_puzzle_variant);

    return *retv;
  }

  Strings &notes_before_snapshot(size_t puzzle_index, size_t snapshot_index) {
    auto &puzzle_variant = m_collection.puzzles()[puzzle_index];

    Strings *retv;
    std::visit(
      [&retv, snapshot_index](auto &puzzle) {
        if (snapshot_index == 0)
          retv = &(puzzle.notes());
        else
          retv = &(puzzle.snapshots()[snapshot_index - 1].notes());
      },
      puzzle_variant);

    return *retv;
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
  string remove_title_line(Strings &notes) {
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

  void cleanup_whitespace(Strings &notes) const {
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

class LIBSOKOENGINE_LOCAL SOKWriter {
  ostream &m_stream;

public:
  SOKWriter(ostream &dest) : m_stream(dest) {
    if (dest.fail()) { throw runtime_error("Unknown output stream error!"); }
  }

  bool write(const Collection &collection) {
    bool retv = write_collection_header(collection);
    if (retv) {
      for (const auto &puzzle_variant : collection.puzzles()) {
        std::visit([this, &retv](auto &puzzle) { retv = write(puzzle); },
                   puzzle_variant);
      }
    }
    return retv;
  }

  bool write(const Puzzle &puzzle) {
    if (puzzle.size() == 0) return true;

    if (!is_blank(puzzle.title()))
      m_stream << boost::trim_copy(puzzle.title()) << endl << endl;

    m_stream << boost::trim_right_copy(puzzle.board()) << endl << endl;

    bool written = false;

    if (puzzle.tessellation().str() != "sokoban")
      written = write_tagged(TAG_VARIANT, puzzle.tessellation().str()) || written;

    written = write_tagged(TAG_AUTHOR, puzzle.author()) || written;
    if (!is_blank(puzzle.boxorder()) && !is_blank(puzzle.goalorder())) {
      written = write_tagged(TAG_BOXORDER, puzzle.boxorder()) || written;
      written = write_tagged(TAG_GOALORDER, puzzle.goalorder()) || written;
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

  bool write_snapshot(const Snapshot &snapshot) {
    if (is_blank(snapshot.moves())) return true;

    if (!is_blank(snapshot.title()))
      m_stream << boost::trim_copy(snapshot.title()) << endl;

    m_stream << boost::trim_copy(snapshot.moves()) << endl << endl;

    bool written = false;
    written = write_tagged(TAG_SOLVER, snapshot.solver()) || written;
    written = write_tagged(TAG_SNAPSHOT_CREATED_AT, snapshot.created_at()) || written;
    written = write_tagged(TAG_DURATION, snapshot.duration()) || written;

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

SOKFileFormat::~SOKFileFormat() {}

void SOKFileFormat::read(istream &src, Collection &dest, const string &variant_hint) {
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
