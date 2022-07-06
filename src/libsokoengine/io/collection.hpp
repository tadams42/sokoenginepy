#ifndef COLLECTION_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define COLLECTION_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "tessellation.hpp"

#include <filesystem>
#include <variant>

namespace sokoengine {
namespace io {

class SokobanPuzzle;
class HexobanPuzzle;
class TriobanPuzzle;
class OctobanPuzzle;

typedef std::variant<SokobanPuzzle, HexobanPuzzle, TriobanPuzzle, OctobanPuzzle>
  AnyPuzzle;

///
/// Default type for sequence of Puzzle
///
typedef std::vector<AnyPuzzle> Puzzles;

///
/// Collection of one or more game puzzles.
///
class LIBSOKOENGINE_API Collection {
public:
  explicit Collection(
    const std::string &title      = "",
    const std::string &author     = "",
    const std::string &created_at = "",
    const std::string &updated_at = "",
    const std::string &notes      = ""
  );
  Collection(const Collection &rv);
  Collection &operator=(const Collection &rv);
  Collection(Collection &&rv);
  Collection &operator=(Collection &&rv);
  virtual ~Collection();

  const std::string &title() const;
  std::string       &title();
  const std::string &author() const;
  std::string       &author();
  const std::string &created_at() const;
  std::string       &created_at();
  const std::string &updated_at() const;
  std::string       &updated_at();
  const std::string &notes() const;
  std::string       &notes();
  const Puzzles     &puzzles() const;
  Puzzles           &puzzles();

  ///
  /// Loads collection from `path`.
  ///
  /// Loader supports SokobanYASC .sok format, but will happily try to load older,
  /// similar textual sokoban files (usually with extensions `.txt`, `.tsb` or `.hsb`).
  ///
  /// @param path source file path
  /// @param tessellation_hint If puzzles in file don't specify their game
  ///   tessellation assume this value.
  ///
  void load(
    const std::filesystem::path &path,
    game::Tessellation           tessellation_hint = game::Tessellation::SOKOBAN
  );

  ///
  /// Loads collection from `path`.
  ///
  /// Loader supports SokobanYASC .sok format, but will happily try to load older,
  /// similar textual sokoban files (usually with extensions `.txt`, `.tsb` or `.hsb`).
  ///
  /// @param path source file path
  /// @param tessellation_hint If puzzles in file don't specify their game
  ///   tessellation assume this value.
  ///
  void load(
    const std::string &path,
    game::Tessellation tessellation_hint = game::Tessellation::SOKOBAN
  );

  ///
  /// Loads collection from `data`.
  ///
  /// Loader supports SokobanYASC .sok format, but will happily try to load older,
  /// similar textual sokoban files (usually with extensions `.txt`, `.tsb` or `.hsb`).
  ///
  /// @param data source stream of collection data
  /// @param tessellation_hint If puzzles in source don't specify their game
  ///   tessellation assume this value.
  ///
  void load(
    std::istream      &data,
    game::Tessellation tessellation_hint = game::Tessellation::SOKOBAN
  );

  ///
  /// Loads collection from `data`.
  ///
  /// Loader supports SokobanYASC .sok format, but will happily try to load older,
  /// similar textual sokoban files (usually with extensions `.txt`, `.tsb` or `.hsb`).
  ///
  /// @param data raw collection data
  /// @param tessellation_hint If puzzles in source don't specify their game
  ///   tessellation assume this value.
  ///
  void loads(
    const std::string &data,
    game::Tessellation tessellation_hint = game::Tessellation::SOKOBAN
  );

  ///
  /// Saves collection to file at `path` in SokobanYASC .sok format.
  ///
  /// @note
  /// Doesn't care about `path` file extension.
  ///
  void dump(const std::filesystem::path &path) const;

  ///
  /// Saves collection to file at `path` in SokobanYASC .sok format.
  ///
  /// @note
  /// Doesn't care about `path` file extension.
  ///
  void dump(const std::string &path) const;

  ///
  /// Saves collection to output stream.
  ///
  void dump(std::ostream &dest) const;

  ///
  /// Saves collection to string.
  ///
  std::string dumps() const;

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file

///
/// @page sok_fileformat SokobanYASC .sok file format
///
/// @include SOK_format_specification.txt
///
