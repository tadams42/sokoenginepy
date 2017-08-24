#ifndef DIRECTION_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define DIRECTION_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

#include <string>

namespace sokoengine {

enum class LIBSOKOENGINE_API EDirection : int {
  E_UP         = 0,
  E_NORTH_EAST = 1,
  E_RIGHT      = 2,
  E_SOUTH_EAST = 3,
  E_DOWN       = 4,
  E_SOUTH_WEST = 5,
  E_LEFT       = 6,
  E_NORTH_WEST = 7
};

///
/// Movement direction for Mover, AtomicMove, etc...
///
class LIBSOKOENGINE_API Direction {
  EDirection m_value;
public:
  static const Direction UP;
  static const Direction DOWN;
  static const Direction LEFT;
  static const Direction RIGHT;
  static const Direction NORTH_WEST;
  static const Direction NORTH_EAST;
  static const Direction SOUTH_WEST;
  static const Direction SOUTH_EAST;

  explicit Direction(EDirection value = EDirection::E_UP) : m_value(value) {};

  bool operator== (const Direction& rv) const { return m_value == rv.m_value; }
  bool operator!= (const Direction& rv) const { return !(*this == rv); }
  bool operator< (const Direction& rv) const { return m_value < rv.m_value; }

  EDirection get_value() const { return m_value; }

  static constexpr int len() { return 8; }

  const Direction& opposite() const {
    if (m_value == UP.m_value) return DOWN;
    else if (m_value == DOWN.m_value) return UP;
    else if (m_value == LEFT.m_value) return RIGHT;
    else if (m_value == RIGHT.m_value) return LEFT;
    else if (m_value == NORTH_EAST.m_value) return SOUTH_WEST;
    else if (m_value == SOUTH_EAST.m_value) return NORTH_WEST;
    else if (m_value == NORTH_WEST.m_value) return SOUTH_EAST;
    else
      // if (m_value == SOUTH_WEST.m_value)
      return NORTH_EAST;
  }

  std::string repr() const {
    if (m_value == UP.m_value) return "Direction.UP";
    else if (m_value == DOWN.m_value) return "Direction.DOWN";
    else if (m_value == LEFT.m_value) return "Direction.LEFT";
    else if (m_value == RIGHT.m_value) return "Direction.RIGHT";
    else if (m_value == NORTH_EAST.m_value) return "Direction.NORTH_EAST";
    else if (m_value == SOUTH_EAST.m_value) return "Direction.SOUTH_EAST";
    else if (m_value == NORTH_WEST.m_value) return "Direction.NORTH_WEST";
    else
      // if (m_value == SOUTH_WEST.m_value)
      return "Direction.SOUTH_WEST";
  }

  std::string str() const { return repr(); }
};

} // namespace sokoengine

#endif // HEADER_GUARD
