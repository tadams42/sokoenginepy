#include "sokoban.hpp"

#include "puzzle_parsing.hpp"

namespace sokoengine {
namespace io {
namespace implementation {

const PuzzleResizer &Sokoban::resizer() {
  static const PuzzleResizer the_one;
  return the_one;
}

const PuzzleParser &Sokoban::parser() {
  static const PuzzleParser the_one;
  return the_one;
}

const PuzzlePrinter &Sokoban::printer() {
  static const PuzzlePrinter the_one;
  return the_one;
}

} // namespace implementation
} // namespace io
} // namespace sokoengine
