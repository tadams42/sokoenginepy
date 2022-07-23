/// @file
#include "tessellation_impl.hpp"

#include "hexoban_tessellation.hpp"
#include "octoban_tessellation.hpp"
#include "sokoban_tessellation.hpp"
#include "trioban_tessellation.hpp"

#include <boost/algorithm/string.hpp>

using std::invalid_argument;
using std::string;

namespace sokoengine {
namespace implementation {

string to_str(Tessellation tessellation) {
  switch (tessellation) {
    case Tessellation::SOKOBAN:
      return "Tessellation.SOKOBAN";
      break;
    case Tessellation::HEXOBAN:
      return "Tessellation.HEXOBAN";
      break;
    case Tessellation::TRIOBAN:
      return "Tessellation.TRIOBAN";
      break;
    case Tessellation::OCTOBAN:
      return "Tessellation.OCTOBAN";
      break;
      // Do not handle default, let compiler generate warning when another
      // tessellation is added...
  }
  throw std::invalid_argument("Unknown tessellation!");
}

static constexpr SokobanTessellation SOKOBAN;
static constexpr HexobanTessellation HEXOBAN;
static constexpr TriobanTessellation TRIOBAN;
static constexpr OctobanTessellation OCTOBAN;

const TessellationImpl &TessellationImpl::instance(const Tessellation &tessellation) {
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

GraphType TessellationImpl::graph_type() const { return GraphType::DIRECTED; }

CellOrientation TessellationImpl::cell_orientation(
  position_t position, board_size_t width, board_size_t height
) const {
  return CellOrientation::DEFAULT;
}

CellOrientations TessellationImpl::cell_orientations() const {
  return CellOrientations{CellOrientation::DEFAULT};
}

} // namespace implementation
} // namespace sokoengine
