#ifndef COMMON_SKINS_FORMAT_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define COMMON_SKINS_FORMAT_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "direction.hpp"
#include "image_impl.hpp"
#include "numeric_types.hpp"
#include "tessellation.hpp"
#include "tile_shape.hpp"

namespace sokoengine {
namespace implementation {

struct LIBSOKOENGINE_LOCAL tile_map_t {
  point_t floor;
  point_t non_playable_floor;
  point_t goal;
  point_t pusher;
  point_t pusher_on_goal;
  point_t box;
  point_t box_on_goal;
  point_t wall;
  point_t wall_cap;

  std::map<Direction, point_t> directional_pushers;
  std::map<Direction, point_t> directional_pushers_on_goal;

  typedef std::pair<directions_t, ImageImpl> directional_wall_t;
  typedef std::vector<directional_wall_t>    directional_walls_t;
  directional_walls_t                        directional_walls;

  int animated_pusher_row         = -1;
  int animated_pusher_on_goal_row = -1;
  int animated_box_row            = -1;
  int animated_box_on_goal_row    = -1;
};

typedef std::map<TileShape, tile_map_t> tile_maps_t;

class LIBSOKOENGINE_LOCAL CommonSkinsFormat {
public:
  CommonSkinsFormat(CommonSkinsFormat &)                                    = delete;
  CommonSkinsFormat                         &operator=(CommonSkinsFormat &) = delete;
  virtual std::unique_ptr<CommonSkinsFormat> clone() const                  = 0;
  virtual ~CommonSkinsFormat()                                              = 0;

  static std::unique_ptr<CommonSkinsFormat> instance(
    Tessellation tessellation, uint8_t rows_count_hint, uint8_t columns_count_hint
  );

  void     set_image(uint32_t img_width, uint32_t img_heigh);
  uint32_t img_width() const;
  uint32_t img_height() const;
  uint16_t columns_width() const;
  uint16_t rows_height() const;
  uint16_t tile_width() const;
  uint16_t tile_height() const;
  uint8_t  rows_count() const;
  uint8_t  columns_count() const;

  virtual tile_maps_t categorize_tiles(const ImageImpl::tiles_t &src) const = 0;
  virtual polygon_t   tile_polygon(TileShape shape) const                   = 0;
  virtual pointf_t    tile_position(
       position_t board_position, board_size_t width, board_size_t height
     ) const = 0;
  virtual point_t
  canvas_size(board_size_t board_width, board_size_t board_height) const;

protected:
  CommonSkinsFormat(uint8_t rows_count_hint, uint8_t columns_count_hint);

  uint32_t m_img_width       = 0;
  uint32_t m_img_height      = 0;
  uint8_t  m_rows_count_hint = 0;
  uint8_t  m_cols_count_hint = 0;
  uint16_t m_columns_width   = 0;
  uint16_t m_rows_height     = 0;
  uint16_t m_tile_width      = 0;
  uint16_t m_tile_height     = 0;
  uint8_t  m_rows_count      = 0;
  uint8_t  m_columns_count   = 0;

private:
  void guess_tile_sizes();
};

} // namespace implementation
} // namespace sokoengine

#endif // HEADER_GUARD
