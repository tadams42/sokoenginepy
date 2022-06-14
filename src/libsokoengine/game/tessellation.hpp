#ifndef TESSELLATION_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define TESSELLATION_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "config.hpp"

namespace sokoengine {
namespace game {

class PusherStep;

///
/// Base class for concrete implementations of sokoengine::game::Tessellation.
///
class LIBSOKOENGINE_API BaseTessellation {
public:
  virtual ~BaseTessellation() = default;

  static const BaseTessellation &instance(const Tessellation &tessellation);

  ///
  /// All Direction supported by this Tessellation
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

  virtual io::CellOrientation cell_orientation(position_t position, board_size_t width,
                                               board_size_t height) const;

  static const std::string &direction_repr(Direction d);
  static const std::string &direction_str(Direction d);
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
