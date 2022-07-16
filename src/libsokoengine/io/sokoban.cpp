#include "sokoban.hpp"

#include "puzzle_parsing.hpp"

namespace sokoengine {
namespace io {
namespace implementation {

static constexpr PuzzleResizer SOK_RESIZER;
static constexpr PuzzleParser  SOK_PARSER;
static constexpr PuzzlePrinter SOK_PRINTER;

const PuzzleResizer &Sokoban::resizer() { return SOK_RESIZER; }

const PuzzleParser &Sokoban::parser() { return SOK_PARSER; }

const PuzzlePrinter &Sokoban::printer() { return SOK_PRINTER; }

} // namespace implementation
} // namespace io
} // namespace sokoengine
