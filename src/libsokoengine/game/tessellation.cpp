#include "tessellation.hpp"

#include "hexoban_tessellation.hpp"
#include "octoban_tessellation.hpp"
#include "sokoban_tessellation.hpp"
#include "trioban_tessellation.hpp"

#include <boost/algorithm/string.hpp>

using std::invalid_argument;

namespace sokoengine {
namespace game {
namespace implementation {

using io::CellOrientation;

static constexpr SokobanTessellation SOKOBAN;
static constexpr HexobanTessellation HEXOBAN;
static constexpr TriobanTessellation TRIOBAN;
static constexpr OctobanTessellation OCTOBAN;

const BaseTessellation &BaseTessellation::instance(const Tessellation &tessellation) {
  switch (tessellation) {
    case Tessellation::SOKOBAN:
      return SOKOBAN;
      break;
    case Tessellation::HEXOBAN:
      return HEXOBAN;
      break;
    case Tessellation::TRIOBAN:
      return TRIOBAN;
      break;
    case Tessellation::OCTOBAN:
      return OCTOBAN;
      break;
      // Do not handle default, let compiler generate warning when another
      // tessellation is added...
  }
  throw invalid_argument("Unknown tessellation!");
}

GraphType BaseTessellation::graph_type() const { return GraphType::DIRECTED; }

CellOrientation BaseTessellation::cell_orientation(
  position_t position, board_size_t width, board_size_t height
) const {
  return CellOrientation::DEFAULT;
}

} // namespace implementation
} // namespace game
} // namespace sokoengine
