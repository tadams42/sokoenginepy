#ifndef DIRECTION_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define DIRECTION_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

#include <string>

namespace sokoengine {
namespace game {

///
/// Movement directions.
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
/// Movement directions count.
///
constexpr uint8_t DIRECTIONS_COUNT =
  static_cast<uint8_t>(Direction::NORTH_WEST) + 1;

///
/// Directions lookup.
///
constexpr Direction DIRECTIONS[DIRECTIONS_COUNT] = {
  Direction::UP,   Direction::NORTH_EAST, Direction::RIGHT, Direction::SOUTH_EAST,
  Direction::DOWN, Direction::SOUTH_WEST, Direction::LEFT,  Direction::NORTH_WEST};

///
/// Opposite directions lookup
///
constexpr Direction OPPOSITE_DIRECTIONS[DIRECTIONS_COUNT] = {
  Direction::DOWN, Direction::SOUTH_WEST, Direction::LEFT,  Direction::NORTH_WEST,
  Direction::UP,   Direction::NORTH_EAST, Direction::RIGHT, Direction::SOUTH_EAST};

constexpr uint8_t direction_pack(const Direction &direction) {
  return static_cast<uint8_t>(direction);
}

constexpr const Direction &direction_unpack(uint8_t val) {
  return DIRECTIONS[val];
}

///
/// Opposite direction lookup.
///
LIBSOKOENGINE_API constexpr Direction opposite(const Direction d) {
  return OPPOSITE_DIRECTIONS[static_cast<uint8_t>(d)];
}

LIBSOKOENGINE_API const std::string &direction_repr(Direction d);
LIBSOKOENGINE_API const std::string &direction_str(Direction d);

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
