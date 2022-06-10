#ifndef COLLECTION_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define COLLECTION_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

#include "hexoban_puzzle.hpp"
#include "octoban_puzzle.hpp"
#include "sokoban_puzzle.hpp"
#include "trioban_puzzle.hpp"

#include <filesystem>
#include <memory>
#include <variant>

namespace sokoengine {

/// Namespace for I/O part of sokoengine
///
namespace io {

typedef std::variant<HexobanPuzzle, TriobanPuzzle, OctobanPuzzle, SokobanPuzzle>
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
  explicit Collection(const std::string &title = "", const std::string &author = "",
                      const std::string &created_at = "",
                      const std::string &updated_at = "",
                      const Strings &notes = Strings());
  virtual ~Collection();

  const std::string &title() const;
  std::string &title();
  const std::string &author() const;
  std::string &author();
  const std::string &created_at() const;
  std::string &created_at();
  const std::string &updated_at() const;
  std::string &updated_at();
  const Strings &notes() const;
  Strings &notes();
  const Puzzles &puzzles() const;
  Puzzles &puzzles();

  bool load(const std::filesystem::path &path);
  bool load(const std::filesystem::path &path, const std::string &puzzle_type_hint);
  bool load(const std::string &path);
  bool load(const std::string &path, const std::string &puzzle_type_hint);

  bool save(const std::filesystem::path &path) const;
  bool save(const std::string &path) const;

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
