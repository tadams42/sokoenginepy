#include "trioban.hpp"

#include "puzzle_parsing.hpp"

namespace sokoengine {
namespace io {
namespace implementation {

static constexpr PuzzleResizer TRI_RESIZER;
static constexpr PuzzleParser  TRI_PARSER;
static constexpr PuzzlePrinter TRI_PRINTER;

const PuzzleResizer &Trioban::resizer() { return TRI_RESIZER; }

const PuzzleParser &Trioban::parser() { return TRI_PARSER; }

const PuzzlePrinter &Trioban::printer() { return TRI_PRINTER; }

} // namespace implementation
} // namespace io
} // namespace sokoengine
