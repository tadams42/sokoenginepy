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

  explicit Direction(const EDirection& value = EDirection::UP);

  bool operator== (const Direction& rv) const;
  bool operator!= (const Direction& rv) const;
  bool operator< (const Direction& rv) const;

  static constexpr unsigned char len() { return 8; }

  const Direction& opposite() const;

  ///
  /// Type for compact Direction representation
  ///
  typedef unsigned char packed_t;

  static const Direction& unpack(packed_t c);
  packed_t pack() const;
  std::string repr() const;
  std::string str() const;
};

} // namespace sokoengine

#endif // HEADER_GUARD
