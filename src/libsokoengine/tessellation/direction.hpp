#ifndef DIRECTION_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define DIRECTION_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

#include <string>

namespace sokoengine {

///
/// Enumeration of possible movement directions.
///
enum class LIBSOKOENGINE_API Direction : uint8_t {
  UP = 0,
  NORTH_EAST,
  RIGHT,
  SOUTH_EAST,
  DOWN,
  SOUTH_WEST,
  LEFT,
  NORTH_WEST
};

///
/// Count of existing movement directions.
///
constexpr uint8_t DIRECTIONS_COUNT = 8;

///
/// Mapping of opposite movement directions.
///
constexpr Direction OPPOSITE_DIRECTIONS[DIRECTIONS_COUNT] = {
  Direction::DOWN,
  Direction::SOUTH_WEST,
  Direction::LEFT,
  Direction::NORTH_WEST,
  Direction::UP,
  Direction::NORTH_EAST,
  Direction::RIGHT,
  Direction::SOUTH_EAST
};

///
/// Opposite movement direction lookup.
///
LIBSOKOENGINE_API constexpr Direction opposite(const Direction d) {
  return OPPOSITE_DIRECTIONS[static_cast<uint8_t>(d)];
}

LIBSOKOENGINE_API const std::string& repr_direction(Direction d);
LIBSOKOENGINE_API const std::string& str_direction(Direction d);

} // namespace sokoengine

#endif // HEADER_GUARD
