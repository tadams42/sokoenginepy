#include "trioban_puzzle.hpp"
#include "trioban_tessellation.hpp"

using namespace std;

namespace sokoengine {
namespace io {

using implementation::PuzzleParser;
using implementation::PuzzlePrinter;
using implementation::PuzzleResizer;

LIBSOKOENGINE_LOCAL const PuzzleResizer &tb_static_resizer() {
  static const PuzzleResizer the_one;
  return the_one;
}

LIBSOKOENGINE_LOCAL const PuzzleParser &tb_static_parser() {
  static const PuzzleParser the_one;
  return the_one;
}

LIBSOKOENGINE_LOCAL const PuzzlePrinter &tb_static_printer() {
  static const PuzzlePrinter the_one;
  return the_one;
}

TriobanPuzzle::TriobanPuzzle() : TriobanPuzzle(0, 0) {}

TriobanPuzzle::TriobanPuzzle(board_size_t width, board_size_t height)
  : Puzzle(game::Tessellation::TRIOBAN, tb_static_resizer(), tb_static_parser(),
           tb_static_printer(), width, height) {}

TriobanPuzzle::TriobanPuzzle(const string &src)
  : Puzzle(game::Tessellation::TRIOBAN, tb_static_resizer(), tb_static_parser(),
           tb_static_printer(), src) {}

TriobanPuzzle::TriobanPuzzle(const TriobanPuzzle &rv) : Puzzle(rv) {}

TriobanPuzzle &TriobanPuzzle::operator=(const TriobanPuzzle &rv) {
  if (this != &rv) { Puzzle::operator=(rv); }
  return *this;
}

TriobanPuzzle::TriobanPuzzle(TriobanPuzzle &&) = default;

TriobanPuzzle &TriobanPuzzle::operator=(TriobanPuzzle &&) = default;

TriobanPuzzle::~TriobanPuzzle() = default;

TriobanPuzzle::unique_ptr_t TriobanPuzzle::create_clone() const {
  return make_unique<TriobanPuzzle>(*this);
}

} // namespace io
} // namespace sokoengine
