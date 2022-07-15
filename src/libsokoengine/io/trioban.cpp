#include "trioban.hpp"

#include "puzzle_parsing.hpp"

namespace sokoengine {
namespace io {
namespace implementation {

const PuzzleResizer &Trioban::resizer() {
  static const PuzzleResizer the_one;
  return the_one;
}

const PuzzleParser &Trioban::parser() {
  static const PuzzleParser the_one;
  return the_one;
}

const PuzzlePrinter &Trioban::printer() {
  static const PuzzlePrinter the_one;
  return the_one;
}

} // namespace implementation
} // namespace io
} // namespace sokoengine
