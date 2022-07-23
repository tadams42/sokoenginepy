#ifndef TESSELLATION_IMPL_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define TESSELLATION_IMPL_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "cell_orientation.hpp"
#include "direction.hpp"
#include "tessellation.hpp"

namespace sokoengine {

namespace game {
class PusherStep;
} // namespace game

namespace implementation {

///
/// Types of BoardGraph.
///
enum class LIBSOKOENGINE_LOCAL GraphType : int {
  ///
  /// Directed graphs
  ///
  DIRECTED,

  ///
  /// Directed graphs with self loops and parallel edges
  ///
  DIRECTED_MULTI
};

LIBSOKOENGINE_LOCAL std::string to_str(Tessellation tessellation);

///
/// Base class for all tessellation implementations.
///
class LIBSOKOENGINE_LOCAL TessellationImpl {
public:
  constexpr inline TessellationImpl() {}

  static const TessellationImpl &instance(const Tessellation &tessellation);

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
  virtual game::PusherStep char_to_pusher_step(char input_chr) const = 0;

  ///
  /// Converts PusherStep into movement character.
  ///
  /// @throws std::invalid_argument conversion is not possible in context of this
  /// tessellation
  ///
  virtual char pusher_step_to_char(const game::PusherStep &pusher_step) const = 0;

  ///
  /// Type of board graph used in context of this tessellation.
  ///
  virtual GraphType graph_type() const;

  ///
  /// Calculates board cell orientation for given coordinate.
  ///
  virtual CellOrientation
  cell_orientation(position_t position, board_size_t width, board_size_t height) const;

  ///
  /// All CellOrientation that this tessellation uses.
  ///
  virtual CellOrientations cell_orientations() const;
};

} // namespace implementation
} // namespace sokoengine

#endif // HEADER_GUARD
