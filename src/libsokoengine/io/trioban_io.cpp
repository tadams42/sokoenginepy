/// @file
#include "trioban_io.hpp"

#include "puzzle_parsing.hpp"

namespace sokoengine {
namespace implementation {

static constexpr PuzzleResizer TRI_RESIZER;
static constexpr PuzzleParser  TRI_PARSER;
static constexpr PuzzlePrinter TRI_PRINTER;

const PuzzleResizer &TriobanIo::resizer() { return TRI_RESIZER; }

const PuzzleParser &TriobanIo::parser() { return TRI_PARSER; }

const PuzzlePrinter &TriobanIo::printer() { return TRI_PRINTER; }

} // namespace implementation
} // namespace sokoengine
