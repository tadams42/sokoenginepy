#ifndef SOKOBAN_PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define SOKOBAN_PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "puzzle.hpp"

namespace sokoengine {
namespace io {

///
/// Board implementation for Sokoban.
///
class LIBSOKOENGINE_API SokobanPuzzle : public Puzzle {
public:
  SokobanPuzzle();
  SokobanPuzzle(board_size_t width, board_size_t height);
  explicit SokobanPuzzle(const std::string &src);
  SokobanPuzzle(const SokobanPuzzle &rv);
  SokobanPuzzle &operator=(const SokobanPuzzle &rv);
  SokobanPuzzle(SokobanPuzzle &&rv);
  SokobanPuzzle &operator=(SokobanPuzzle &&rv);
  virtual ~SokobanPuzzle();
  virtual unique_ptr_t create_clone() const override;
};

} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
