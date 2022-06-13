#ifndef TESSELLATION_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define TESSELLATION_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "direction.hpp"

namespace sokoengine {
namespace game {

class PusherStep;

///
/// Ordered collection of Directions usually describing continuous board path.
///
typedef std::vector<Direction> Directions;

///
/// Type of graph
///
enum class LIBSOKOENGINE_API GraphType : int {
  ///
  /// Directed graphs
  ///
  DIRECTED,

  ///
  /// Directed graphs with self loops and parallel edges
  ///
  DIRECTED_MULTI
};


///
/// Special property of board position that is needed in some tessellations and that
/// depends on cell position.
///
enum class LIBSOKOENGINE_API CellOrientation : int {
  DEFAULT,
  TRIANGLE_DOWN,
  OCTAGON,
};

class SokobanTessellation;
class HexobanTessellation;
class TriobanTessellation;
class OctobanTessellation;

///
/// Base class for tessellations.
///
class LIBSOKOENGINE_API Tessellation {
public:
  static const SokobanTessellation &SOKOBAN;
  static const HexobanTessellation &HEXOBAN;
  static const OctobanTessellation &OCTOBAN;
  static const TriobanTessellation &TRIOBAN;

  virtual ~Tessellation() = 0;

  static const Tessellation &instance_from(const std::string &name);

  bool operator==(const Tessellation &rv) const;
  bool operator!=(const Tessellation &rv) const;

  ///
  /// All Direction supported by this Tesselation
  ///
  virtual const Directions &legal_directions() const = 0;
  ///
  /// Calculate new position in given direction.
  ///
  /// Returns either new position or invalid number (> MAX_POS) if movement in given
  /// direction would've resulted with off-board position.
  ///
  virtual position_t neighbor_position(position_t position, const Direction &direction,
                                       board_size_t width,
                                       board_size_t height) const = 0;
  ///
  /// Converts charater into instance of PusherStep in context of Tessellation.
  ///
  virtual PusherStep char_to_pusher_step(char input_chr) const = 0;
  ///
  /// Converts PusherStep into character representation in context of Tessellation.
  ///
  virtual char pusher_step_to_char(const PusherStep &pusher_step) const = 0;
  virtual GraphType graph_type() const;

  virtual CellOrientation cell_orientation(position_t position,
                                           board_size_t width,
                                           board_size_t height) const;

  virtual std::string str() const = 0;
  virtual std::string repr() const = 0;

protected:
  Tessellation() = default;
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
constexpr position_t X(position_t index, board_size_t width) {
  return width == 0 ? 0 : index % width;
}

///
/// Calculates y-axis position from 1D board position
///
constexpr position_t Y(position_t index, board_size_t width) {
  return width == 0 ? 0 : index / width;
}

///
/// Alias for Y()
///
constexpr position_t ROW(position_t index, board_size_t width) {
  return Y(index, width);
}

///
/// Alias for X()
///
constexpr position_t COLUMN(position_t index, board_size_t width) {
  return X(index, width);
}

///
/// Is position on given board?
///
constexpr bool ON_BOARD(position_t x, position_t y, board_size_t width,
                        board_size_t height) {
  return x < width && y < height;
}

///
/// Is position on given board?
///
constexpr bool ON_BOARD(position_t pos, board_size_t width,
                        board_size_t height) {
  return ON_BOARD(X(pos, width), Y(pos, width), width, height);
}

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
