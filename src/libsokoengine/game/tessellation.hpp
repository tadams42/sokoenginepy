#ifndef TESSELLATION_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define TESSELLATION_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

namespace sokoengine {
namespace game {

class PusherStep;

///
/// Base class for all tessellation implementations.
///
class LIBSOKOENGINE_API BaseTessellation {
public:
  virtual ~BaseTessellation() = default;

  static const BaseTessellation &instance(const Tessellation &tessellation);

  ///
  /// Directions that are valid in context of this tessellation.
  ///
  virtual const Directions &legal_directions() const = 0;

  ///
  /// Calculates neighbor position in given direction.
  ///
  /// Position is always expressed as 1D index of board graph vertex.
  ///
  /// To convert 2D coordinates into vertex index, use index_1d() method.
  ///
  /// To convert 1D vertex index into 2D coordinates, use combinations of
  /// index_row() and index_column() functions.
  ///
  /// @returns
  /// New position or `.Config.NO_POS` when new position would be off-board.
  ///
  /// @throws std::invalid_argument direction is not one of legal_directions()
  ///
  virtual position_t neighbor_position(
    position_t       position,
    const Direction &direction,
    board_size_t     width,
    board_size_t     height
  ) const = 0;

  ///
  /// Converts movement character to PusherStep
  ///
  /// @throws std::invalid_argument conversion is not possible in context of this
  /// tessellation
  ///
  virtual PusherStep char_to_pusher_step(char input_chr) const = 0;

  ///
  /// Converts PusherStep into movement character.
  ///
  /// @throws std::invalid_argument conversion is not possible in context of this
  /// tessellation
  ///
  virtual char pusher_step_to_char(const PusherStep &pusher_step) const = 0;

  ///
  /// Type of board graph used in context of this tessellation.
  ///
  virtual GraphType graph_type() const;

  ///
  /// Calculates board cell orientation for given coordinate.
  ///
  virtual io::CellOrientation
  cell_orientation(position_t position, board_size_t width, board_size_t height) const;
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
