#include "hexoban_common_skins_format.hpp"

#include <cmath>

namespace sokoengine {
namespace implementation {

HexobanCommonSkinsFormat::HexobanCommonSkinsFormat(
  uint8_t rows_count_hint, uint8_t columns_count_hint
)
  : CommonSkinsFormat(rows_count_hint, columns_count_hint) {}

HexobanCommonSkinsFormat::~HexobanCommonSkinsFormat() = default;

std::unique_ptr<CommonSkinsFormat> HexobanCommonSkinsFormat::clone() const {
  auto retv =
    std::make_unique<HexobanCommonSkinsFormat>(m_rows_count_hint, m_cols_count_hint);

  retv->m_img_width     = m_img_width;
  retv->m_img_height    = m_img_height;
  retv->m_columns_width = m_columns_width;
  retv->m_rows_height   = m_rows_height;
  retv->m_tile_width    = m_tile_width;
  retv->m_tile_height   = m_tile_height;
  retv->m_rows_count    = m_rows_count;
  retv->m_columns_count = m_columns_count;

  return retv;
}

tile_maps_t HexobanCommonSkinsFormat::categorize_tiles(const ImageImpl::tiles_t &src
) const {
  size_t rows_count    = src.size();
  size_t columns_count = rows_count > 0 ? src.back().size() : 0;

  if (rows_count < 3 || columns_count < 3) {
    throw std::invalid_argument(
      "Image doesn't appear to be a Hexoban skin! (detected "
      + std::to_string(rows_count) + " tile rows and " + std::to_string(columns_count)
      + " tile columns)"
    );
  }

  tile_maps_t retv;
  retv.try_emplace(TileShape::DEFAULT);
  tile_map_t &image_map = retv.at(TileShape::DEFAULT);

  image_map.floor          = point_t(0, 0);
  image_map.goal           = point_t(0, 1);
  image_map.pusher         = point_t(1, 0);
  image_map.pusher_on_goal = point_t(1, 1);
  image_map.box            = point_t(2, 0);
  image_map.box_on_goal    = point_t(2, 1);
  image_map.wall           = point_t(0, 2);

  if (rows_count >= 5 && columns_count >= 6) {
    image_map.directional_pushers[Direction::LEFT]               = point_t(0, 3);
    image_map.directional_pushers[Direction::NORTH_WEST]         = point_t(1, 3);
    image_map.directional_pushers[Direction::NORTH_EAST]         = point_t(2, 3);
    image_map.directional_pushers[Direction::RIGHT]              = point_t(3, 3);
    image_map.directional_pushers[Direction::SOUTH_EAST]         = point_t(4, 3);
    image_map.directional_pushers[Direction::SOUTH_WEST]         = point_t(5, 3);
    image_map.directional_pushers_on_goal[Direction::LEFT]       = point_t(0, 4);
    image_map.directional_pushers_on_goal[Direction::NORTH_WEST] = point_t(1, 4);
    image_map.directional_pushers_on_goal[Direction::NORTH_EAST] = point_t(2, 4);
    image_map.directional_pushers_on_goal[Direction::RIGHT]      = point_t(3, 4);
    image_map.directional_pushers_on_goal[Direction::SOUTH_EAST] = point_t(4, 4);
    image_map.directional_pushers_on_goal[Direction::SOUTH_WEST] = point_t(5, 4);
  }

  return retv;
}

polygon_t HexobanCommonSkinsFormat::tile_polygon(TileShape shape) const {
  // double w = original_tile_width;
  double h = m_rows_height;

  // Regular hexagons in skins are placed in bounding rectangle with:
  //
  // - bounding rectangle height == hexagon height
  // - bounding rect width > hexagon width
  // - left side of hexagon is aligned with left side of bounding rect

  double s = h / 2.0;     // hexagon side length
  double a = sqrt(3) * s; // width of bounding rect
  double b = h;           // height of bounding rect

  return polygon_t{
    {
     {a / 2, 0},
     {a, b / 4},
     {a, b * 3 / 4.0},
     {a / 2, b},
     {0, b * 3 / 4.0},
     {0, b / 4.0},
     {a / 2, 0},
     }
  };
}

pointf_t HexobanCommonSkinsFormat::tile_position(
  position_t board_position, board_size_t width, board_size_t height
) const {
  position_t x = index_x(board_position, width);
  position_t y = index_y(board_position, width);

  polygon_t polygon = tile_polygon(TileShape::DEFAULT);
  rectf_t   rect    = bounding_rect(polygon);

  double w = rect.width();
  double h = rect.height();

  double shift_right = w / 2;
  double shift_up    = h / 4;

  pointf_t pos;
  pos.x(y % 2 == 0 ? x * w : x * w + shift_right);
  pos.y(y * (h - shift_up));

  return pos;
}

point_t HexobanCommonSkinsFormat::canvas_size(
  board_size_t board_width, board_size_t board_height
) const {
  return point_t(
    (board_width + 0.6) * m_columns_width, (board_height * 0.8) * m_rows_height
  );
}

} // namespace implementation
} // namespace sokoengine
