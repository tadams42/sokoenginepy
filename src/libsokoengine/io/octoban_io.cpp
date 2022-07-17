/// @file
#include "octoban_io.hpp"

#include "puzzle_parsing.hpp"

namespace sokoengine {
namespace implementation {

static constexpr PuzzleResizer OCT_RESIZER;
static constexpr PuzzleParser  OCT_PARSER;
static constexpr PuzzlePrinter OCT_PRINTER;

const PuzzleResizer &OctobanIo::resizer() { return OCT_RESIZER; }

const PuzzleParser &OctobanIo::parser() { return OCT_PARSER; }

const PuzzlePrinter &OctobanIo::printer() { return OCT_PRINTER; }

} // namespace implementation
} // namespace sokoengine
