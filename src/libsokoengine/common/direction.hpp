#ifndef DIRECTION_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define DIRECTION_0FEA723A_C86F_6753_04ABD475F6FCA5FB
/// @file

#include "sokoengine_config.hpp"

namespace sokoengine {

////
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
/// Ordered collection of Directions usually describing continuous board path.
///
typedef std::vector<Direction> Directions;

namespace implementation {

///
/// Packs Direction into 8-bit integer.
///
constexpr uint8_t direction_pack(const Direction &direction) {
  return static_cast<uint8_t>(direction);
}

///
/// Number of available Direction.
///
static constexpr uint8_t DIRECTIONS_COUNT = direction_pack(Direction::NORTH_WEST) + 1;

///
/// Opposite Direction lookup.
///
static constexpr Direction DIRECTIONS[DIRECTIONS_COUNT] = {
  Direction::UP,
  Direction::NORTH_EAST,
  Direction::RIGHT,
  Direction::SOUTH_EAST,
  Direction::DOWN,
  Direction::SOUTH_WEST,
  Direction::LEFT,
  Direction::NORTH_WEST};

///
/// Opposite directions lookup
///
static constexpr Direction OPPOSITE_DIRECTIONS[DIRECTIONS_COUNT] = {
  Direction::DOWN,
  Direction::SOUTH_WEST,
  Direction::LEFT,
  Direction::NORTH_WEST,
  Direction::UP,
  Direction::NORTH_EAST,
  Direction::RIGHT,
  Direction::SOUTH_EAST};

///
/// Reverse operation from direction_pack().
///
constexpr const Direction &direction_unpack(uint8_t val) { return DIRECTIONS[val]; }

LIBSOKOENGINE_LOCAL std::string to_str(Direction d);

} // namespace implementation

///
/// Opposite Direction lookup.
///
LIBSOKOENGINE_API constexpr Direction opposite(const Direction d) {
  return implementation::OPPOSITE_DIRECTIONS[static_cast<uint8_t>(d)];
}

} // namespace sokoengine

#endif // HEADER_GUARD
