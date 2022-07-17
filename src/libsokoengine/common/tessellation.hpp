#ifndef TESSELLATION_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define TESSELLATION_0FEA723A_C86F_6753_04ABD475F6FCA5FB
/// @file

#include "numeric_types.hpp"

namespace sokoengine {

///
/// Supported game tessellations.
///
enum class LIBSOKOENGINE_API Tessellation : uint8_t {
  ///
  /// Tessellation for Sokoban game variant.
  ///
  /// Board is laid out on squares.
  ///
  /// Direction <-> character mapping:
  ///
  /// | LEFT | RIGHT | UP   | DOWN |
  /// | ---- | ----- | ---- | ---- |
  /// | l, L | r, R  | u, U | d, D |
  ///
  SOKOBAN = 0,
  ///
  /// Tessellation for Hexoban game variant.
  ///
  /// Board space is laid out on vertical hexagons with following coordinate system:
  ///
  /// @image html hexoban_coordinates.png
  ///
  /// Textual representation uses two characters for each hexagon. This allows different
  /// encoding schemes.
  ///
  /// | Scheme 1                 | Scheme 2                 |
  /// | ------------------------ | ------------------------ |
  /// | ![](hexoban_scheme1.png) | ![](hexoban_scheme2.png) |
  ///
  /// As long as encoding of single board is consistent, all methods handle any scheme
  /// transparently - parsing of board strings 'Just Works (TM)'
  ///
  /// Direction <-> character mapping:
  ///
  /// | LEFT | RIGHT | NORTH_WEST | SOUTH_WEST | NORTH_EAST | SOUTH_EAST |
  /// | ---- | ----- | ---------- | ---------- | ---------- | ---------- |
  /// | l, L | r, R  | u, U       | d, D       | n, N       | s, S       |
  ///
  HEXOBAN,
  ///
  /// Tessellation for Trioban game variant.
  ///
  /// Board is laid out on alternating triangles with origin triangle pointing down.
  ///
  /// Direction <-> character mapping:
  ///
  /// | LEFT | RIGHT | NORTH_EAST | NORTH_WEST | SOUTH_EAST | SOUTH_WEST |
  /// | ---- | ----- | ---------- | ---------- | ---------- | ---------- |
  /// | l, L | r, R  | n, N       | u, U       | d, D       | s, S       |
  ///
  /// Depending on pusher position, not all move directions are allowed on all board
  /// positions:
  ///
  /// @image html trioban_am.png
  ///
  TRIOBAN,
  ///
  /// Tessellation for Octoban game variant.
  ///
  /// Board space is laid out on alternating squares and octagons with origin of
  /// coordinate system being octagon. Tessellation allows all 8 directions of movement
  /// from Direction and depending on current pusher position some of these directions
  /// do not result in successful move.
  ///
  /// Direction <-> character mapping:
  ///
  /// | UP   | NORTH_EAST | RIGHT | SOUTH_EAST | DOWN | SOUTH_WEST | LEFT | NORTH_WEST |
  /// | ---- | ---------- | ----- | ---------- | ---- | ---------- | ---- | ---------- |
  /// | u, U | n, N       | r, R  | e, E       | d, D | s, S       | l, L | w, W       |
  ///
  OCTOBAN
};

///
/// Converts 2D board position to 1D board position
///
constexpr position_t index_1d(position_t x, position_t y, board_size_t width) {
  return y * width + x;
}

///
/// Calculates x-axis position from 1D board position
///
constexpr position_t index_x(position_t index, board_size_t width) {
  return width == 0 ? 0 : index % width;
}

///
/// Calculates y-axis position from 1D board position
///
constexpr position_t index_y(position_t index, board_size_t width) {
  return width == 0 ? 0 : index / width;
}

///
/// Alias for index_y()
///
constexpr position_t index_row(position_t index, board_size_t width) {
  return index_y(index, width);
}

///
/// Alias for index_x()
///
constexpr position_t index_column(position_t index, board_size_t width) {
  return index_x(index, width);
}

///
/// Is position on given board?
///
constexpr bool
is_on_board_2d(position_t x, position_t y, board_size_t width, board_size_t height) {
  return x < width && y < height;
}

///
/// Is position on given board?
///
constexpr bool is_on_board_1d(position_t pos, board_size_t width, board_size_t height) {
  return is_on_board_2d(index_x(pos, width), index_y(pos, width), width, height);
}

} // namespace sokoengine

#endif // HEADER_GUARD
