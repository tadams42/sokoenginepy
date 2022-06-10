#ifndef HEXOBAN_PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define HEXOBAN_PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "puzzle.hpp"

namespace sokoengine {
namespace io {

///
/// Board implementation for Hexoban.
///
class LIBSOKOENGINE_API HexobanPuzzle : public Puzzle {
public:
  HexobanPuzzle();
  HexobanPuzzle(board_size_t width, board_size_t height);
  explicit HexobanPuzzle(const std::string &src);
  HexobanPuzzle(const HexobanPuzzle &rv);
  HexobanPuzzle &operator=(const HexobanPuzzle &rv);
  HexobanPuzzle(HexobanPuzzle &&rv);
  HexobanPuzzle &operator=(HexobanPuzzle &&rv);
  virtual ~HexobanPuzzle();
  virtual unique_ptr_t create_clone() const override;
};

} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
