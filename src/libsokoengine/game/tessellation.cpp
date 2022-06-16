#include "tessellation.hpp"

#include "hexoban_tessellation.hpp"
#include "octoban_tessellation.hpp"
#include "sokoban_tessellation.hpp"
#include "trioban_tessellation.hpp"

#include <boost/algorithm/string.hpp>

using namespace std;

namespace sokoengine {
namespace game {

using io::CellOrientation;

namespace implementation {

static const string strs[DIRECTIONS_COUNT] = {
  string("Direction.UP"),         string("Direction.DOWN"),
  string("Direction.LEFT"),       string("Direction.RIGHT"),
  string("Direction.NORTH_WEST"), string("Direction.NORTH_EAST"),
  string("Direction.SOUTH_EAST"), string("Direction.SOUTH_WEST")};

} // namespace implementation

const std::string &BaseTessellation::direction_repr(Direction d) {
  return implementation::strs[direction_pack(d)];
}

const std::string &BaseTessellation::direction_str(Direction d) {
  return direction_repr(d);
}

const BaseTessellation &BaseTessellation::instance(const Tessellation &tessellation) {
  static const SokobanTessellation SOKOBAN;
  static const HexobanTessellation HEXOBAN;
  static const TriobanTessellation TRIOBAN;
  static const OctobanTessellation OCTOBAN;

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
    // Do not handle default, let compiler generate warning when another tessellation
    // is added...
  }
  throw invalid_argument("Unknown tessellation!");
}

GraphType BaseTessellation::graph_type() const { return GraphType::DIRECTED; }

CellOrientation BaseTessellation::cell_orientation(position_t position,
                                                   board_size_t width,
                                                   board_size_t height) const {
  return CellOrientation::DEFAULT;
}

} // namespace game
} // namespace sokoengine
