#ifndef HEXOBAN_TESSELLATION_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define HEXOBAN_TESSELLATION_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "tessellation.hpp"

namespace sokoengine {
namespace game {

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
class LIBSOKOENGINE_API HexobanTessellation : public BaseTessellation {
public:
  virtual const Directions &legal_directions() const override;
  virtual position_t        neighbor_position(
           position_t       position,
           const Direction &direction,
           board_size_t     width,
           board_size_t     height
         ) const override;
  virtual PusherStep char_to_pusher_step(char input_chr) const override;
  virtual char       pusher_step_to_char(const PusherStep &pusher_step) const override;
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
