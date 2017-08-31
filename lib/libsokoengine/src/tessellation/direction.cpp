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

Direction::Direction(const EDirection& value) :
  m_direction(value)
{}

bool Direction::operator== (const Direction& rv) const {
  return m_direction == rv.m_direction;
}

bool Direction::operator!= (const Direction& rv) const {
  return !(*this == rv);
}

bool Direction::operator< (const Direction& rv) const {
  return m_direction < rv.m_direction;
}

const Direction& Direction::opposite() const {
  switch (m_direction) {
    case EDirection::UP:
      return DOWN;
    case EDirection::DOWN:
      return UP;
    case EDirection::LEFT:
      return RIGHT;
    case EDirection::RIGHT:
      return LEFT;
    case EDirection::NORTH_WEST:
      return SOUTH_EAST;
    case EDirection::NORTH_EAST:
      return SOUTH_WEST;
    case EDirection::SOUTH_WEST:
      return NORTH_EAST;
    case EDirection::SOUTH_EAST:
    default:
      return NORTH_WEST;
  };
}

const Direction& Direction::unpack(packed_t c) {
  switch (c) {
    case static_cast<packed_t>(EDirection::LEFT):
      return LEFT;
    case static_cast<packed_t>(EDirection::RIGHT):
      return RIGHT;
    case static_cast<packed_t>(EDirection::UP):
      return UP;
    case static_cast<packed_t>(EDirection::DOWN):
      return DOWN;
    case static_cast<packed_t>(EDirection::NORTH_WEST):
      return NORTH_WEST;
    case static_cast<packed_t>(EDirection::NORTH_EAST):
      return NORTH_EAST;
    case static_cast<packed_t>(EDirection::SOUTH_WEST):
      return SOUTH_WEST;
    case static_cast<packed_t>(EDirection::SOUTH_EAST):
    default:
      return SOUTH_EAST;
  }
}

Direction::packed_t Direction::pack() const {
  return static_cast<packed_t>(m_direction);
}

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
