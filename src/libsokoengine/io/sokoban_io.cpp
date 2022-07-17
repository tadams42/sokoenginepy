/// @file
#include "sokoban_io.hpp"

#include "puzzle_parsing.hpp"

namespace sokoengine {
namespace implementation {

static constexpr PuzzleResizer SOK_RESIZER;
static constexpr PuzzleParser  SOK_PARSER;
static constexpr PuzzlePrinter SOK_PRINTER;

const PuzzleResizer &SokobanIo::resizer() { return SOK_RESIZER; }

const PuzzleParser &SokobanIo::parser() { return SOK_PARSER; }

const PuzzlePrinter &SokobanIo::printer() { return SOK_PRINTER; }

} // namespace implementation
} // namespace sokoengine
