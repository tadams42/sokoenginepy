#ifndef TRIOBAN_PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define TRIOBAN_PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "puzzle.hpp"

namespace sokoengine {
namespace io {

///
/// Board implementation for Trioban.
///
class LIBSOKOENGINE_API TriobanPuzzle : public Puzzle {
public:
  TriobanPuzzle();
  TriobanPuzzle(board_size_t width, board_size_t height);
  explicit TriobanPuzzle(const std::string &src);
  TriobanPuzzle(const TriobanPuzzle &rv);
  TriobanPuzzle &operator=(const TriobanPuzzle &rv);
  TriobanPuzzle(TriobanPuzzle &&rv);
  TriobanPuzzle &operator=(TriobanPuzzle &&rv);
  virtual ~TriobanPuzzle();
  virtual unique_ptr_t create_clone() const override;
};

} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
