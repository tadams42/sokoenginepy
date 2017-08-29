#ifndef DIRECTION_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define DIRECTION_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

#include <string>

namespace sokoengine {

///
/// Direction values.
///
enum class LIBSOKOENGINE_API EDirection : unsigned char {
  UP, NORTH_EAST, RIGHT, SOUTH_EAST, DOWN, SOUTH_WEST, LEFT, NORTH_WEST
};

///
/// Movement directions.
///
class LIBSOKOENGINE_API Direction {
public:
  EDirection m_direction;

  static const Direction& UP;
  static const Direction& DOWN;
  static const Direction& LEFT;
  static const Direction& RIGHT;
  static const Direction& NORTH_WEST;
  static const Direction& NORTH_EAST;
  static const Direction& SOUTH_WEST;
  static const Direction& SOUTH_EAST;

  explicit constexpr Direction(EDirection value = EDirection::UP) :
    m_direction(value)
  {};

  bool operator== (const Direction& rv) const { return m_direction == rv.m_direction; }
  bool operator!= (const Direction& rv) const { return !(*this == rv); }
  bool operator< (const Direction& rv) const { return m_direction < rv.m_direction; }

  static constexpr unsigned char len() { return 8; }

  const Direction& opposite() const {
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

  ///
  /// Type for compact Direction representation
  ///
  typedef unsigned char packed_t;

  static const Direction& unpack(packed_t c) {
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

  packed_t pack() const { return static_cast<packed_t>(m_direction); }

  std::string repr() const;
  std::string str() const;
};

} // namespace sokoengine

#endif // HEADER_GUARD
