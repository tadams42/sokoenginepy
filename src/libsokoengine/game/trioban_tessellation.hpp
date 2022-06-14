#ifndef TRIOBAN_TESSELLATION_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define TRIOBAN_TESSELLATION_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "tessellation.hpp"

namespace sokoengine {
namespace game {

///
/// Tessellation for Trioban.
///
class LIBSOKOENGINE_API TriobanTessellation : public BaseTessellation {
public:
  virtual const Directions &legal_directions() const override;
  virtual position_t neighbor_position(position_t position, const Direction &direction,
                                       board_size_t width,
                                       board_size_t height) const override;
  virtual PusherStep char_to_pusher_step(char input_chr) const override;
  virtual char pusher_step_to_char(const PusherStep &pusher_step) const override;
  virtual GraphType graph_type() const override;
  virtual io::CellOrientation cell_orientation(position_t position, board_size_t width,
                                               board_size_t height) const override;
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
