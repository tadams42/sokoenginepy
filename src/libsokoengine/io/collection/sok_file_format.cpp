/// @file
#include "sok_file_format.hpp"

#include "SOK_format_specification.h"
#include "characters.hpp"
#include "collection.hpp"
#include "tessellation_impl.hpp"

#include <algorithm>
#include <boost/algorithm/string.hpp>

using sokoengine::implementation::strings_t;
using std::endl;
using std::ios_base;
using std::istream;
using std::ostream;
using std::string;
using std::vector;

namespace sokoengine {
namespace implementation {

struct LIBSOKOENGINE_LOCAL SnapshotData {
  string    moves_data;
  string    title;
  string    solver;
  strings_t notes;
};

typedef vector<SnapshotData> SnapshotsData;

struct LIBSOKOENGINE_LOCAL PuzzleData {
  string        board;
  Tessellation  tessellation = Tessellation::SOKOBAN;
  string        title;
  string        author;
  string        boxorder;
  string        goalorder;
  strings_t     notes;
  SnapshotsData snapshots;
};

typedef vector<PuzzleData> PuzzlesData;

struct LIBSOKOENGINE_LOCAL CollectionData {
  string       title;
  string       author;
  string       created_at;
  string       updated_at;
  strings_t    notes;
  Tessellation header_tessellation_hint        = Tessellation::SOKOBAN;
  bool         was_tessellation_hint_in_header = false;
  PuzzlesData  puzzles;
};

class LIBSOKOENGINE_LOCAL SOKTags {
public:
  static const string AUTHOR;
  static const string TITLE;
  static const string COLLECTION;
  static const string GOALORDER;
  static const string BOXORDER;
  static const string SOLVER;
  static const string VARIANT;
  static const string DATE_CREATED;
  static const string DATE_OF_LAST_CHANGE;
  static const string RAW_FILE_NOTES;
  static const string TAG_DELIMITERS;

  static Tessellation tessellation_from_string(const string &line) {
    string tessellation = line;
    boost::trim(tessellation);
    boost::to_lower(tessellation);
    if (tessellation == "sokoban") {
      return Tessellation::SOKOBAN;
    } else if (tessellation == "trioban") {
      return Tessellation::TRIOBAN;
    } else if (tessellation == "hexoban") {
      return Tessellation::HEXOBAN;
    } else if (tessellation == "octoban") {
      return Tessellation::OCTOBAN;
    } else {
      throw std::invalid_argument("Unknown Tessellation \"" + tessellation + "\"!");
    }
  }

  static strings_t
  extract_collection_attributes(CollectionData &dest, const strings_t &notes) {
    strings_t remaining_lines;
    string    tessellation;
    bool      tessellation_found = false;

    for (const string &line : notes) {
      bool   was_tagged = is_raw_file_notes_line(line);
      string value;

      if (!was_tagged) {
        value = get_tag_data(TITLE, line, was_tagged);
        if (was_tagged) {
          dest.title = value;
        }
      }

      if (!was_tagged) {
        value = get_tag_data(AUTHOR, line, was_tagged);
        if (was_tagged) {
          dest.author = value;
        }
      }

      if (!was_tagged) {
        value = get_tag_data(COLLECTION, line, was_tagged);
        if (was_tagged) {
          dest.title = value;
        }
      }

      if (!was_tagged) {
        value = get_tag_data(VARIANT, line, was_tagged);
        if (was_tagged) {
          tessellation       = value;
          tessellation_found = true;
          break;
        }
      }

      if (!was_tagged) {
        value = get_tag_data(DATE_CREATED, line, was_tagged);
        if (was_tagged) {
          dest.created_at = value;
        }
      }

      if (!was_tagged) {
        value = get_tag_data(DATE_OF_LAST_CHANGE, line, was_tagged);
        if (was_tagged) {
          dest.updated_at = value;
        }
      }

      if (!was_tagged) {
        remaining_lines.push_back(line);
      }
    }

    if (tessellation_found && !is_blank(tessellation)) {
      dest.was_tessellation_hint_in_header = tessellation_found;
      dest.header_tessellation_hint        = tessellation_from_string(tessellation);
    }

    return remaining_lines;
  }

  static strings_t extract_puzzle_attributes(
    PuzzleData      &dest,
    const strings_t &notes,
    bool             has_tessellation_header,
    Tessellation     collection_header_tessellation_hint,
    bool             has_supplied_tessellation,
    Tessellation     supplied_tessellation
  ) {
    strings_t remaining_lines;
    string    tessellation;
    bool      tessellation_found = false;

    for (const string &line : notes) {
      bool   was_tagged = false;
      string value;

      value = get_tag_data(TITLE, line, was_tagged);
      if (was_tagged) {
        dest.title = value;
      }

      if (!was_tagged) {
        value = get_tag_data(AUTHOR, line, was_tagged);
        if (was_tagged) {
          dest.author = value;
        }
      }

      if (!was_tagged) {
        value = get_tag_data(VARIANT, line, was_tagged);
        if (was_tagged) {
          tessellation       = value;
          tessellation_found = true;
          break;
        }
      }

      if (!was_tagged) {
        value = get_tag_data(BOXORDER, line, was_tagged);
        if (was_tagged) {
          dest.boxorder = value;
        }
      }

      if (!was_tagged) {
        value = get_tag_data(GOALORDER, line, was_tagged);
        if (was_tagged) {
          dest.goalorder = value;
        }
      }

      if (!was_tagged) {
        remaining_lines.push_back(line);
      }
    }

    if (tessellation_found && !is_blank(tessellation)) {
      dest.tessellation = tessellation_from_string(tessellation);
    } else if (has_tessellation_header) {
      dest.tessellation = collection_header_tessellation_hint;
    } else if (has_supplied_tessellation) {
      dest.tessellation = supplied_tessellation;
    } else {
      dest.tessellation = Tessellation::SOKOBAN;
    }

    return remaining_lines;
  }

  static strings_t
  extract_snapshot_attributes(SnapshotData &dest, const strings_t &notes) {
    strings_t remaining_lines;

    for (const string &line : notes) {
      bool   was_tagged = false;
      string value;

      value = get_tag_data(TITLE, line, was_tagged);
      if (was_tagged) {
        dest.title = value;
      }

      if (!was_tagged) {
        value = get_tag_data(AUTHOR, line, was_tagged);
        if (was_tagged) {
          dest.solver = value;
        }
      }

      if (!was_tagged) {
        value = get_tag_data(SOLVER, line, was_tagged);
        if (was_tagged) {
          dest.solver = value;
        }
      }

      if (!was_tagged) {
        remaining_lines.push_back(line);
      }
    }

    return remaining_lines;
  }

  static string get_tag_data(const string &tag, const string &line, bool &tag_found) {
    tag_found = false;
    string retv;
    size_t delimit_pos = line.find_first_of(TAG_DELIMITERS);
    if (delimit_pos != string::npos) {
      string found_tag = line.substr(0, delimit_pos);

      string looking_for_tag = boost::trim_copy(boost::to_lower_copy(tag));
      boost::trim(found_tag);
      boost::to_lower(found_tag);

      if (looking_for_tag == found_tag) {
        retv = line.substr(delimit_pos + 1, line.length());
        boost::trim(retv);
        tag_found = true;
      }
    }
    return retv;
  }

  static bool is_raw_file_notes_line(const string &line) {
    return boost::starts_with(line, RAW_FILE_NOTES);
  }

  static bool write_tagged(ostream &dest, const string &tag, const string &data) {
    if (!is_blank(data) && !is_blank(tag)) {
      dest << tag << ": " << boost::trim_right_copy(data) << endl;
      return true;
    }
    return false;
  }
};

const string SOKTags::AUTHOR              = "Author";
const string SOKTags::TITLE               = "Title";
const string SOKTags::COLLECTION          = "Collection";
const string SOKTags::GOALORDER           = "goalorder";
const string SOKTags::BOXORDER            = "boxorder";
const string SOKTags::SOLVER              = "Solver";
const string SOKTags::VARIANT             = "Game";
const string SOKTags::DATE_CREATED        = "Date Created";
const string SOKTags::DATE_OF_LAST_CHANGE = "Date of Last Change";
const string SOKTags::RAW_FILE_NOTES      = "::";
const string SOKTags::TAG_DELIMITERS      = "=:";

class LIBSOKOENGINE_LOCAL SOKReader {
  istream       &m_src;
  Collection    &m_dest;
  Tessellation   m_supplied_tessellation_hint;
  CollectionData m_data;

public:
  SOKReader(istream &src, Collection &dest, Tessellation tessellation_hint)
    : m_src(src)
    , m_dest(dest)
    , m_supplied_tessellation_hint(tessellation_hint) {}

  void read() {
    parse();
    consume();
  }

private:
  void consume() {
    m_dest.title().swap(m_data.title);
    m_dest.author().swap(m_data.author);
    m_dest.created_at().swap(m_data.created_at);
    m_dest.updated_at().swap(m_data.updated_at);
    m_dest.notes() = boost::join(m_data.notes, "\n");

    for (PuzzleData &puzzle_data : m_data.puzzles) {
      Puzzle &puzzle =
        m_dest.puzzles().emplace_back(puzzle_data.tessellation, puzzle_data.board);

      puzzle.title().swap(puzzle_data.title);
      puzzle.author().swap(puzzle_data.author);
      puzzle.boxorder().swap(puzzle_data.boxorder);
      puzzle.goalorder().swap(puzzle_data.goalorder);
      puzzle.notes() = boost::join(puzzle_data.notes, "\n");

      for (auto &snapshot_data : puzzle_data.snapshots) {
        Snapshot &snapshot = puzzle.snapshots().emplace_back(
          puzzle_data.tessellation, snapshot_data.moves_data
        );
        snapshot.title().swap(snapshot_data.title);
        snapshot.solver().swap(snapshot_data.solver);
        snapshot.notes() = boost::join(snapshot_data.notes, "\n");
      }
    }
  }

  void parse() {
    if (m_src.fail()) {
      throw std::runtime_error("Unknown input stream error!");
    }
    m_data = CollectionData();
    m_src.clear();
    m_src.seekg(0, ios_base::beg);
    split_input();
    parse_title_lines();
    parse_notes();
  }

  void split_input() {
    string    line;
    strings_t lines;
    while (getline(m_src, line)) {
      lines.push_back(line + '\n');
    }

    auto first_board_line =
      std::find_if(lines.cbegin(), lines.cend(), [](const string &line) {
        return Characters::is_board(line);
      });

    strings_t remaining_lines;
    if (first_board_line != lines.cend()) {
      std::copy(lines.cbegin(), first_board_line, std::back_inserter(m_data.notes));
      std::copy(first_board_line, lines.cend(), std::back_inserter(remaining_lines));
      lines.clear();
    } else {
      m_data.notes.swap(lines);
    }

    split_puzzle_chunks(remaining_lines);
    split_snapshot_chunks();
  }

  void split_puzzle_chunks(strings_t &remaining_lines) {
    while (remaining_lines.size() > 0) {
      m_data.puzzles.push_back(PuzzleData());
      PuzzleData &puzzle = m_data.puzzles.back();

      auto first_note_line = std::find_if(
        remaining_lines.cbegin(),
        remaining_lines.cend(),
        [](const string &line) {
          return !Characters::is_board(line);
        }
      );

      if (first_note_line != remaining_lines.cend()) {
        strings_t board;
        std::copy(remaining_lines.cbegin(), first_note_line, std::back_inserter(board));
        puzzle.board = boost::join(board, "");
        remaining_lines.erase(remaining_lines.cbegin(), first_note_line);
      } else {
        puzzle.board = boost::join(remaining_lines, "");
        remaining_lines.clear();
      }

      if (remaining_lines.size() > 0) {
        auto first_board_line = std::find_if(
          remaining_lines.cbegin(),
          remaining_lines.cend(),
          [](const string &line) {
            return Characters::is_board(line);
          }
        );

        if (first_board_line != remaining_lines.cend()) {
          std::copy(
            remaining_lines.cbegin(), first_board_line, std::back_inserter(puzzle.notes)
          );
          remaining_lines.erase(remaining_lines.cbegin(), first_board_line);
        } else {
          puzzle.notes.swap(remaining_lines);
        }
      }
    }
  }

  void split_snapshot_chunks() {
    for (PuzzleData &puzzle : m_data.puzzles) {
      strings_t remaining_lines;
      remaining_lines.swap(puzzle.notes);

      auto first_moves_line = std::find_if(
        remaining_lines.cbegin(),
        remaining_lines.cend(),
        [](const string &line) {
          return Characters::is_snapshot(line);
        }
      );
      if (first_moves_line != remaining_lines.cend()) {
        std::copy(
          remaining_lines.cbegin(), first_moves_line, std::back_inserter(puzzle.notes)
        );
        remaining_lines.erase(remaining_lines.cbegin(), first_moves_line);
      } else {
        remaining_lines.swap(puzzle.notes);
      }

      puzzle.snapshots.clear();

      while (remaining_lines.size() > 0) {
        puzzle.snapshots.push_back(SnapshotData());
        SnapshotData &snapshot = puzzle.snapshots.back();

        auto first_note_line = std::find_if(
          remaining_lines.cbegin(),
          remaining_lines.cend(),
          [](const string &line) {
            return !Characters::is_snapshot(line);
          }
        );

        if (first_note_line != remaining_lines.cend()) {
          strings_t moves_lines;
          std::copy(
            remaining_lines.cbegin(), first_note_line, std::back_inserter(moves_lines)
          );
          for (string &ln : moves_lines) {
            boost::trim(ln);
          }
          snapshot.moves_data = boost::join(moves_lines, "");
          remaining_lines.erase(remaining_lines.cbegin(), first_note_line);
        } else {
          for (string &ln : remaining_lines) {
            boost::trim(ln);
          }
          snapshot.moves_data = boost::join(remaining_lines, "");
          remaining_lines.clear();
        }

        if (remaining_lines.size() > 0) {
          first_moves_line = std::find_if(
            remaining_lines.cbegin(),
            remaining_lines.cend(),
            [](const string &line) {
              return Characters::is_snapshot(line);
            }
          );

          if (first_moves_line != remaining_lines.cend()) {
            std::copy(
              remaining_lines.cbegin(),
              first_moves_line,
              std::back_inserter(snapshot.notes)
            );
            remaining_lines.erase(remaining_lines.cbegin(), first_moves_line);
          } else {
            snapshot.notes.swap(remaining_lines);
          }
        }
      }
    }
  }

  strings_t &notes_before_puzzle(size_t puzzle_index) {
    if (puzzle_index == 0) {
      return m_data.notes;
    }
    PuzzleData &previous_puzzle = m_data.puzzles[puzzle_index - 1];
    if (previous_puzzle.snapshots.size() > 0) {
      return previous_puzzle.snapshots.back().notes;
    }
    return previous_puzzle.notes;
  }

  strings_t &notes_before_snapshot(size_t puzzle_index, size_t snapshot_index) {
    PuzzleData &puzzle = m_data.puzzles[puzzle_index];
    if (snapshot_index == 0) {
      return puzzle.notes;
    }
    return puzzle.snapshots[snapshot_index - 1].notes;
  }

  string get_and_remove_title_line(strings_t &notes) {
    // :: Titles                                                 ::
    // ::   A title line is the last non-blank text line before  ::
    // ::   a board, a saved game, or a solution, provided the   ::
    // ::   line is preceded by a blank line or it is the only   ::
    // ::   text line at this position in the file.              ::
    // ::                                                        ::
    // ::   Title lines are optional unless a single or a last   ::
    // ::   text line from a preceding puzzle, saved game,       ::
    // ::   solution, or file header can be mistaken for a title ::
    // ::   line.                                                ::
    // if (notes.size() == 0) return "";

    // auto b = notes.rbegin();
    // auto e = notes.rend();
    // auto f = [](const string &s) { return !is_blank(s); };
    // strings_t::const_reverse_iterator candidate = find_if(b, e, f);

    strings_t::const_reverse_iterator candidate =
      find_if(notes.rbegin(), notes.rend(), [](const string &s) {
        return !is_blank(s);
      });

    if (candidate == notes.rend()) {
      return "";
    }

    strings_t::const_reverse_iterator preceding_line = candidate;
    if (preceding_line != notes.rend())
      ++preceding_line;
    strings_t::const_reverse_iterator following_line = candidate;
    if (following_line != notes.rbegin())
      --following_line;

    bool preceding_ok =
      preceding_line == notes.rend() ? true : is_blank(*preceding_line);
    bool following_ok  = following_line == candidate ? true : is_blank(*following_line);
    bool is_title_line = preceding_ok && following_ok;

    if (is_title_line) {
      string title_line = *candidate;
      boost::trim(title_line);
      notes.erase((++candidate).base());
      return title_line;
    }
    return "";
  }

  void parse_title_lines() {
    for (size_t puzzle_index = 0; puzzle_index < m_data.puzzles.size();
         puzzle_index++) {
      PuzzleData &puzzle   = m_data.puzzles[puzzle_index];
      strings_t  &notes_bp = notes_before_puzzle(puzzle_index);
      puzzle.title         = get_and_remove_title_line(notes_bp);

      for (size_t snapshot_index = 0; snapshot_index < puzzle.snapshots.size();
           snapshot_index++) {
        SnapshotData &snapshot = puzzle.snapshots[snapshot_index];
        strings_t    &notes_bs = notes_before_snapshot(puzzle_index, snapshot_index);
        snapshot.title         = get_and_remove_title_line(notes_bs);
      }
    }
  }

  void parse_notes() {
    strings_t remaining_lines =
      SOKTags::extract_collection_attributes(m_data, m_data.notes);
    m_data.notes.swap(cleanup_whitespace(remaining_lines));

    for (PuzzleData &puzzle : m_data.puzzles) {
      remaining_lines = SOKTags::extract_puzzle_attributes(
        puzzle,
        puzzle.notes,
        m_data.was_tessellation_hint_in_header,
        m_data.header_tessellation_hint,
        true,
        m_supplied_tessellation_hint
      );
      puzzle.notes.swap(cleanup_whitespace(remaining_lines));

      for (SnapshotData &snapshot : puzzle.snapshots) {
        remaining_lines =
          SOKTags::extract_snapshot_attributes(snapshot, snapshot.notes);
        snapshot.notes.swap(cleanup_whitespace(remaining_lines));
      }
    }
  }

  strings_t &cleanup_whitespace(strings_t &notes) {
    strings_t::iterator tit;
    tit = unique(notes.begin(), notes.end(), [](const string &l, const string &r) {
      return is_blank(l) && is_blank(r);
    });
    notes.erase(tit, notes.end());

    if (notes.size() > 0 && is_blank(notes.back()))
      notes.pop_back();
    if (notes.size() > 0 && is_blank(notes.front()))
      notes.erase(notes.begin());

    for (string &line : notes) {
      boost::trim_right(line);
    }

    return notes;
  }
};

class LIBSOKOENGINE_LOCAL SOKWriter {
  ostream &m_stream;

public:
  explicit SOKWriter(ostream &dest)
    : m_stream(dest) {
    if (dest.fail()) {
      throw std::runtime_error("Unknown output stream error!");
    }
  }

  bool write(const Collection &collection) {
    bool retv = write_collection_header(collection);
    for (const auto &puzzle : collection.puzzles()) {
      if (retv) {
        retv = write_puzzle(puzzle);
        for (size_t i = 0; i < puzzle.snapshots().size(); ++i) {
          if (retv) {
            const Snapshot &snapshot = puzzle.snapshots()[i];
            retv                     = write_snapshot(snapshot);
          }
        }
      }
    }
    return retv;
  }

private:
  string to_str(Tessellation tessellation) {
    switch (tessellation) {
      case Tessellation::SOKOBAN:
        return "sokoban";
        break;
      case Tessellation::HEXOBAN:
        return "hexoban";
        break;
      case Tessellation::TRIOBAN:
        return "trioban";
        break;
      case Tessellation::OCTOBAN:
        return "octoban";
        break;
        // Do not handle default, let compiler generate warning when another
        // tessellation is added...
    }
    throw std::invalid_argument("Unknown tessellation!");
  }

  bool write_puzzle(const Puzzle &puzzle) {
    if (is_blank(puzzle.board()))
      return true;

    if (!is_blank(puzzle.title()))
      m_stream << boost::trim_copy(puzzle.title()) << endl << endl;

    m_stream << boost::trim_right_copy(puzzle.board()) << endl << endl;

    bool written = false;

    if (puzzle.tessellation() != Tessellation::SOKOBAN)
      written =
        SOKTags::write_tagged(m_stream, SOKTags::VARIANT, to_str(puzzle.tessellation()))
        || written;

    if (!is_blank(puzzle.boxorder()) && !is_blank(puzzle.goalorder())) {
      written = SOKTags::write_tagged(m_stream, SOKTags::BOXORDER, puzzle.boxorder())
             || written;
      written = SOKTags::write_tagged(m_stream, SOKTags::GOALORDER, puzzle.goalorder())
             || written;
    }

    written =
      SOKTags::write_tagged(m_stream, SOKTags::AUTHOR, puzzle.author()) || written;

    string non_blank = boost::trim_copy(puzzle.notes());
    if (non_blank.length() > 0) {
      m_stream << non_blank << endl;
      written = true;
    }

    if (written)
      m_stream << endl;

    return (bool)m_stream;
  }

  bool write_snapshot(const Snapshot &snapshot) {
    if (is_blank(snapshot.moves_data()))
      return true;

    if (!is_blank(snapshot.title()))
      m_stream << boost::trim_copy(snapshot.title()) << endl;

    // TODO: wrap at 70
    string moves_data  = boost::trim_copy(snapshot.moves_data());
    size_t write_count = 0;
    for (auto c : moves_data) {
      m_stream << c;
      write_count++;
      if (write_count % 70 == 0) {
        m_stream << endl;
      }
    }
    m_stream << endl << endl;

    bool written = SOKTags::write_tagged(m_stream, SOKTags::SOLVER, snapshot.solver());

    string non_blank = boost::trim_copy(snapshot.notes());
    if (non_blank.length() > 0) {
      m_stream << non_blank << endl;
      written = true;
    }

    if (written)
      m_stream << endl;

    return (bool)m_stream;
  }

  bool write_collection_header(const Collection &collection) {
    m_stream << SOK_format_specification << endl;

    bool write_created_at =
      SOKTags::write_tagged(m_stream, SOKTags::DATE_CREATED, collection.created_at());
    bool write_updated_at = SOKTags::write_tagged(
      m_stream, SOKTags::DATE_OF_LAST_CHANGE, collection.updated_at()
    );

    if (write_created_at || write_updated_at) {
      m_stream << "::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::" << endl
               << endl;
    } else {
      m_stream << endl;
    }

    bool written = false;
    written = SOKTags::write_tagged(m_stream, SOKTags::COLLECTION, collection.title())
           || written;
    written =
      SOKTags::write_tagged(m_stream, SOKTags::AUTHOR, collection.author()) || written;

    string non_blank = boost::trim_copy(collection.notes());
    if (non_blank.length() > 0) {
      m_stream << non_blank << endl;
      written = true;
    }

    if (written)
      m_stream << endl;

    return (bool)m_stream;
  }
};

SOKFileFormat::~SOKFileFormat() {}

void SOKFileFormat::read(
  istream &src, Collection &dest, Tessellation tessellation_hint
) {
  SOKReader reader(src, dest, tessellation_hint);
  reader.read();
}

bool SOKFileFormat::write(const Collection &collection, std::ostream &dest) {
  SOKWriter writer(dest);
  return writer.write(collection);
}

} // namespace implementation
} // namespace sokoengine
