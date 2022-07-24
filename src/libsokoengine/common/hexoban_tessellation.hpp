#ifndef HEXOBAN_TESSELLATION_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define HEXOBAN_TESSELLATION_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "tessellation_impl.hpp"

namespace sokoengine {
namespace implementation {

class LIBSOKOENGINE_LOCAL HexobanTessellation : public TessellationImpl {
public:
  constexpr inline HexobanTessellation()
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
};

} // namespace implementation
} // namespace sokoengine

#endif // HEADER_GUARD
