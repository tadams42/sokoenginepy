#include "direction.hpp"

using namespace std;

namespace sokoengine {

const Direction& Direction::UP = Direction(EDirection::UP);
const Direction& Direction::DOWN = Direction(EDirection::DOWN);
const Direction& Direction::LEFT = Direction(EDirection::LEFT);
const Direction& Direction::RIGHT = Direction(EDirection::RIGHT);
const Direction& Direction::NORTH_EAST = Direction(EDirection::NORTH_EAST);
const Direction& Direction::NORTH_WEST = Direction(EDirection::NORTH_WEST);
const Direction& Direction::SOUTH_EAST = Direction(EDirection::SOUTH_EAST);
const Direction& Direction::SOUTH_WEST = Direction(EDirection::SOUTH_WEST);

string Direction::repr() const {
  switch (m_direction) {
    case EDirection::UP:
      return "Direction.UP";
    case EDirection::DOWN:
      return "Direction.DOWN";
    case EDirection::LEFT:
      return "Direction.LEFT";
    case EDirection::RIGHT:
      return "Direction.RIGHT";
    case EDirection::NORTH_WEST:
      return "Direction.NORTH_WEST";
    case EDirection::NORTH_EAST:
      return "Direction.NORTH_EAST";
    case EDirection::SOUTH_WEST:
      return "Direction.SOUTH_EAST";
    case EDirection::SOUTH_EAST:
    default:
      return "Direction.SOUTH_WEST";
  };
}

string Direction::str() const { return repr(); }

} // namespace sokoengine
