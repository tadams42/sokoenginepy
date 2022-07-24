#ifndef OCTOBAN_TESSELLATION_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define OCTOBAN_TESSELLATION_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "tessellation_impl.hpp"

namespace sokoengine {
namespace implementation {

class LIBSOKOENGINE_LOCAL OctobanTessellation : public TessellationImpl {
public:
  constexpr inline OctobanTessellation()
    : TessellationImpl() {}

  virtual const directions_t &legal_directions() const override;
  virtual position_t          neighbor_position(
             position_t       position,
             const Direction &direction,
             board_size_t     width,
             board_size_t     height
           ) const override;
  virtual game::PusherStep char_to_pusher_step(char input_chr) const override;
  virtual char pusher_step_to_char(const game::PusherStep &pusher_step) const override;
  virtual TileShape tile_shape(
    position_t position, board_size_t width, board_size_t height
  ) const override;
  virtual tile_shapes_t tile_shapes() const override;
};

} // namespace implementation
} // namespace sokoengine

#endif // HEADER_GUARD
