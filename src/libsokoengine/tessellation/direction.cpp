#include "direction.hpp"

using namespace std;

namespace sokoengine {

static const string strs[DIRECTIONS_COUNT] = {
  string("Direction.UP"),
  string("Direction.DOWN"),
  string("Direction.LEFT"),
  string("Direction.RIGHT"),
  string("Direction.NORTH_WEST"),
  string("Direction.NORTH_EAST"),
  string("Direction.SOUTH_EAST"),
  string("Direction.SOUTH_WEST")
};

LIBSOKOENGINE_API const std::string& direction_repr(Direction d) {
  return strs[direction_pack(d)];
}

LIBSOKOENGINE_API const std::string& direction_str(Direction d) {
  return direction_repr(d);
}

} // namespace sokoengine
