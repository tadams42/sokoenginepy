#include "octoban.hpp"

#include "puzzle_parsing.hpp"

namespace sokoengine {
namespace io {
namespace implementation {

static constexpr PuzzleResizer OCT_RESIZER;
static constexpr PuzzleParser  OCT_PARSER;
static constexpr PuzzlePrinter OCT_PRINTER;

const PuzzleResizer &Octoban::resizer() { return OCT_RESIZER; }

const PuzzleParser &Octoban::parser() { return OCT_PARSER; }

const PuzzlePrinter &Octoban::printer() { return OCT_PRINTER; }

} // namespace implementation
} // namespace io
} // namespace sokoengine
