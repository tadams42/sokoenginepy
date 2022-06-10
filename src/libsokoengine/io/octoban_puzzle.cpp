#include "octoban_puzzle.hpp"
#include "octoban_tessellation.hpp"

using namespace std;

namespace sokoengine {
namespace io {
using implementation::PuzzleParser;
using implementation::PuzzlePrinter;
using implementation::PuzzleResizer;

LIBSOKOENGINE_LOCAL const PuzzleResizer &ob_static_resizer() {
  static const PuzzleResizer the_one;
  return the_one;
}

LIBSOKOENGINE_LOCAL const PuzzleParser &ob_static_parser() {
  static const PuzzleParser the_one;
  return the_one;
}

LIBSOKOENGINE_LOCAL const PuzzlePrinter &ob_static_printer() {
  static const PuzzlePrinter the_one;
  return the_one;
}

OctobanPuzzle::OctobanPuzzle() : OctobanPuzzle(0, 0) {}

OctobanPuzzle::OctobanPuzzle(board_size_t width, board_size_t height)
  : Puzzle(game::Tessellation::OCTOBAN, ob_static_resizer(), ob_static_parser(),
           ob_static_printer(), width, height) {}

OctobanPuzzle::OctobanPuzzle(const string &src)
  : Puzzle(game::Tessellation::OCTOBAN, ob_static_resizer(), ob_static_parser(),
           ob_static_printer(), src) {}

OctobanPuzzle::OctobanPuzzle(const OctobanPuzzle &rv) : Puzzle(rv) {}

OctobanPuzzle &OctobanPuzzle::operator=(const OctobanPuzzle &rv) {
  if (this != &rv) { Puzzle::operator=(rv); }
  return *this;
}

OctobanPuzzle::OctobanPuzzle(OctobanPuzzle &&) = default;

OctobanPuzzle &OctobanPuzzle::operator=(OctobanPuzzle &&) = default;

OctobanPuzzle::~OctobanPuzzle() = default;

OctobanPuzzle::unique_ptr_t OctobanPuzzle::create_clone() const {
  return make_unique<OctobanPuzzle>(*this);
}

} // namespace io
} // namespace sokoengine
