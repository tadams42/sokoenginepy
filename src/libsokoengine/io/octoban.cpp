#include "octoban.hpp"

#include "puzzle_parsing.hpp"

namespace sokoengine {
namespace io {
namespace implementation {

const PuzzleResizer &Octoban::resizer() {
  static const PuzzleResizer the_one;
  return the_one;
}

const PuzzleParser &Octoban::parser() {
  static const PuzzleParser the_one;
  return the_one;
}

const PuzzlePrinter &Octoban::printer() {
  static const PuzzlePrinter the_one;
  return the_one;
}

} // namespace implementation
} // namespace io
} // namespace sokoengine
