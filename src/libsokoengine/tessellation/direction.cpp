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

LIBSOKOENGINE_API const std::string& repr_direction(Direction d) {
  return strs[static_cast<uint8_t>(d)];
}

LIBSOKOENGINE_API const std::string& str_direction(Direction d) {
  return repr_direction(d);
}

} // namespace sokoengine
