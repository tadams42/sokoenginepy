#include "sokoban_puzzle.hpp"
#include "sokoban_tessellation.hpp"

using namespace std;

namespace sokoengine {
namespace io {
using implementation::PuzzleParser;
using implementation::PuzzlePrinter;
using implementation::PuzzleResizer;

LIBSOKOENGINE_LOCAL const PuzzleResizer &sb_static_resizer() {
  static const PuzzleResizer the_one;
  return the_one;
}

LIBSOKOENGINE_LOCAL const PuzzleParser &sb_static_parser() {
  static const PuzzleParser the_one;
  return the_one;
}

LIBSOKOENGINE_LOCAL const PuzzlePrinter &sb_static_printer() {
  static const PuzzlePrinter the_one;
  return the_one;
}

SokobanPuzzle::SokobanPuzzle() : SokobanPuzzle(0, 0) {}

SokobanPuzzle::SokobanPuzzle(board_size_t width, board_size_t height)
  : Puzzle(game::Tessellation::SOKOBAN, sb_static_resizer(), sb_static_parser(),
           sb_static_printer(), width, height) {}

SokobanPuzzle::SokobanPuzzle(const string &src)
  : Puzzle(game::Tessellation::SOKOBAN, sb_static_resizer(), sb_static_parser(),
           sb_static_printer(), src) {}

SokobanPuzzle::SokobanPuzzle(const SokobanPuzzle &rv) : Puzzle(rv) {}

SokobanPuzzle &SokobanPuzzle::operator=(const SokobanPuzzle &rv) {
  if (this != &rv) { Puzzle::operator=(rv); }
  return *this;
}

SokobanPuzzle::SokobanPuzzle(SokobanPuzzle &&) = default;

SokobanPuzzle &SokobanPuzzle::operator=(SokobanPuzzle &&) = default;

SokobanPuzzle::~SokobanPuzzle() = default;

SokobanPuzzle::unique_ptr_t SokobanPuzzle::create_clone() const {
  return make_unique<SokobanPuzzle>(*this);
}

} // namespace io
} // namespace sokoengine
