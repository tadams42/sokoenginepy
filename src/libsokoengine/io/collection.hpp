#ifndef COLLECTION_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define COLLECTION_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "puzzle_types.hpp"

#include <filesystem>
#include <memory>
#include <vector>

namespace sokoengine {
///
/// Namespace for I/O part of sokoengine
///
namespace io {

class LIBSOKOENGINE_API Puzzle;

///
/// DEfault type for sequence of Puzzle
///
typedef std::vector<Puzzle> Puzzles;

///
/// Collection of one or more game puzzles.
///
class LIBSOKOENGINE_API Collection {
public:
  explicit Collection(const std::string &title = "", const std::string &author = "",
                      const std::string &notes = "", const std::string &created_at = "",
                      const std::string &updated_at = "");
  virtual ~Collection();

  void clear();

  const std::string &title() const;
  std::string &title();
  const std::string &author() const;
  std::string &author();
  const std::string &created_at() const;
  std::string &created_at();
  const std::string &updated_at() const;
  std::string &updated_at();
  const std::string &notes() const;
  std::string &notes();
  const Puzzles &puzzles() const;
  Puzzles &puzzles();

  bool load(const std::filesystem::path &path);
  bool load(const std::filesystem::path &path, const PuzzleTypes &puzzle_type_hint);
  bool load(const std::string &path);
  bool load(const std::string &path, const PuzzleTypes &puzzle_type_hint);
  bool save(const std::filesystem::path &path) const;
  bool save(const std::string &path) const;
  void reformat(bool use_visible_floor = false, uint8_t break_long_lines_at = 80,
                bool rle_encode = false);

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
