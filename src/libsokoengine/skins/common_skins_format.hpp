#ifndef COMMON_SKINS_FORMAT_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define COMMON_SKINS_FORMAT_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "cell_orientation.hpp"
#include "direction.hpp"
#include "geometry.hpp"
#include "numeric_types.hpp"

namespace sokoengine {
namespace implementation {

class ImageImpl;

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

  typedef std::pair<Directions, ImageImpl> directional_wall_t;
  typedef std::vector<directional_wall_t>  directional_walls_t;
  directional_walls_t                      directional_walls;

  int animated_pusher_row         = -1;
  int animated_pusher_on_goal_row = -1;
  int animated_box_row            = -1;
  int animated_box_on_goal_row    = -1;
};

struct LIBSOKOENGINE_LOCAL tile_sizes_t {
  // Sizes of each original, unprocessed tile image.
  uint16_t original_tile_height;
  uint16_t original_tile_width;

  // Sizes of processed and cropped tile image.
  uint16_t tile_width;
  uint16_t tile_height;

  // Number of tile rows and columns in source image.
  uint16_t rows_count;
  uint16_t columns_count;
};

typedef std::vector<std::vector<ImageImpl>>   raw_tiles_t;
typedef std::map<CellOrientation, tile_map_t> tile_maps_t;

class LIBSOKOENGINE_LOCAL CommonSkinsFormat {
public:
  virtual ~CommonSkinsFormat() = 0;

  virtual tile_sizes_t guess_tile_sizes(
    uint16_t img_width,
    uint16_t img_height,
    uint8_t  rows_count_hint,
    uint8_t  columns_count_hint
  ) const;
  virtual tile_maps_t categorize_tiles(const raw_tiles_t &src) const = 0;
  virtual polygon_t   tile_polygon(
      uint16_t        original_tile_width,
      uint16_t        original_tile_height,
      CellOrientation orientation
    ) const = 0;
  virtual pointf_t tile_position(
    uint16_t     original_tile_width,
    uint16_t     original_tile_height,
    position_t   board_position,
    board_size_t width,
    board_size_t height
  ) const = 0;
};

class LIBSOKOENGINE_LOCAL SokobanCommonSkinsFormat : public CommonSkinsFormat {
public:
  virtual ~SokobanCommonSkinsFormat();

  virtual tile_maps_t categorize_tiles(const raw_tiles_t &src) const override;

  virtual polygon_t tile_polygon(
    uint16_t        original_tile_width,
    uint16_t        original_tile_height,
    CellOrientation orientation
  ) const override;
  virtual pointf_t tile_position(
    uint16_t     original_tile_width,
    uint16_t     original_tile_height,
    position_t   board_position,
    board_size_t width,
    board_size_t height
  ) const override;

private:
  static void generate_directional_walls(
    tile_map_t      &tile_map,
    const ImageImpl &isolated_wall,
    const ImageImpl &lr_wall,
    const ImageImpl &ud_wall,
    const ImageImpl &lurd_wall
  );
  static rect_t left_half(const ImageImpl &src);
  static rect_t right_half(const ImageImpl &src);
  static rect_t up_half(const ImageImpl &src);
  static rect_t down_half(const ImageImpl &src);
  static rect_t left_top_quarter(const ImageImpl &src);
  static rect_t right_top_quarter(const ImageImpl &src);
  static rect_t left_bottom_quarter(const ImageImpl &src);
  static rect_t right_bottom_quarter(const ImageImpl &src);
};

class LIBSOKOENGINE_LOCAL HexobanCommonSkinsFormat : public CommonSkinsFormat {
public:
  virtual ~HexobanCommonSkinsFormat();

  virtual tile_maps_t categorize_tiles(const raw_tiles_t &src) const override;
  virtual polygon_t   tile_polygon(
      uint16_t        original_tile_width,
      uint16_t        original_tile_height,
      CellOrientation orientation
    ) const override;
  virtual pointf_t tile_position(
    uint16_t     original_tile_width,
    uint16_t     original_tile_height,
    position_t   board_position,
    board_size_t width,
    board_size_t height
  ) const override;
};

class LIBSOKOENGINE_LOCAL TriobanCommonSkinsFormat : public CommonSkinsFormat {
public:
  virtual ~TriobanCommonSkinsFormat();

  virtual tile_sizes_t guess_tile_sizes(
    uint16_t img_width,
    uint16_t img_height,
    uint8_t  rows_count_hint,
    uint8_t  columns_count_hint
  ) const override;
  virtual tile_maps_t categorize_tiles(const raw_tiles_t &src) const override;
  virtual polygon_t   tile_polygon(
      uint16_t        original_tile_width,
      uint16_t        original_tile_height,
      CellOrientation orientation
    ) const override;
  virtual pointf_t tile_position(
    uint16_t     original_tile_width,
    uint16_t     original_tile_height,
    position_t   board_position,
    board_size_t width,
    board_size_t height
  ) const override;
};

class LIBSOKOENGINE_LOCAL OctobanCommonSkinsFormat : public CommonSkinsFormat {
public:
  virtual ~OctobanCommonSkinsFormat();

  virtual tile_maps_t categorize_tiles(const raw_tiles_t &src) const override;
  virtual polygon_t   tile_polygon(
      uint16_t        original_tile_width,
      uint16_t        original_tile_height,
      CellOrientation orientation
    ) const override;
  virtual pointf_t tile_position(
    uint16_t     original_tile_width,
    uint16_t     original_tile_height,
    position_t   board_position,
    board_size_t width,
    board_size_t height
  ) const override;
};

} // namespace implementation
} // namespace sokoengine

#endif // HEADER_GUARD
