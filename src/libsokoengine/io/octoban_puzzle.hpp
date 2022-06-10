#ifndef OCTOBAN_PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define OCTOBAN_PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "puzzle.hpp"

namespace sokoengine {
namespace io {

///
/// Board implementation for Octoban.
///
class LIBSOKOENGINE_API OctobanPuzzle : public Puzzle {
public:
  OctobanPuzzle();
  OctobanPuzzle(board_size_t width, board_size_t height);
  explicit OctobanPuzzle(const std::string &src);
  OctobanPuzzle(const OctobanPuzzle &rv);
  OctobanPuzzle &operator=(const OctobanPuzzle &rv);
  OctobanPuzzle(OctobanPuzzle &&rv);
  OctobanPuzzle &operator=(OctobanPuzzle &&rv);
  virtual ~OctobanPuzzle();
  virtual unique_ptr_t create_clone() const override;
};

} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
