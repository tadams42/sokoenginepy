/// @file
#include "direction.hpp"

#include <boost/algorithm/string.hpp>

using std::runtime_error;
using std::string;

namespace sokoengine {
namespace implementation {

string to_str(Direction d) {
  switch (d) {
    case Direction::UP:
      return "Direction.UP";
      break;
    case Direction::DOWN:
      return "Direction.DOWN";
      break;
    case Direction::LEFT:
      return "Direction.LEFT";
      break;
    case Direction::RIGHT:
      return "Direction.RIGHT";
      break;
    case Direction::NORTH_EAST:
      return "Direction.NORTH_EAST";
      break;
    case Direction::NORTH_WEST:
      return "Direction.NORTH_WEST";
      break;
    case Direction::SOUTH_EAST:
      return "Direction.SOUTH_EAST";
      break;
    case Direction::SOUTH_WEST:
      return "Direction.SOUTH_WEST";
      break;
  }
  throw runtime_error("Unhandled direction!");
}

} // namespace implementation
} // namespace sokoengine
