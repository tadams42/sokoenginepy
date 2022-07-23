#include "trioban_common_skins_format.hpp"

namespace sokoengine {
namespace implementation {

TriobanCommonSkinsFormat::TriobanCommonSkinsFormat(
  uint8_t rows_count_hint, uint8_t columns_count_hint
)
  : CommonSkinsFormat(
    rows_count_hint == 0 ? 3 : rows_count_hint,
    columns_count_hint == 0 ? 3 : columns_count_hint
  ) {}

TriobanCommonSkinsFormat::~TriobanCommonSkinsFormat() = default;

std::unique_ptr<CommonSkinsFormat> TriobanCommonSkinsFormat::clone() const {
  auto retv =
    std::make_unique<TriobanCommonSkinsFormat>(m_rows_count_hint, m_cols_count_hint);

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

tile_maps_t TriobanCommonSkinsFormat::categorize_tiles(const ImageImpl::tiles_t &src
) const {
  size_t rows_count    = src.size();
  size_t columns_count = rows_count > 0 ? src.back().size() : 0;

  if (rows_count < 3 || columns_count < 3) {
    throw std::invalid_argument(
      "Image doesn't appear to be a Trioban skin! (detected "
      + std::to_string(rows_count) + " tile rows and " + std::to_string(columns_count)
      + " tile columns)"
    );
  }

  tile_maps_t retv;
  retv.try_emplace(CellOrientation::DEFAULT);
  tile_map_t &map_default = retv.at(CellOrientation::DEFAULT);
  retv.try_emplace(CellOrientation::TRIANGLE_DOWN);
  tile_map_t &map_down = retv.at(CellOrientation::TRIANGLE_DOWN);

  map_default.floor          = point_t(0, 0);
  map_default.pusher         = point_t(1, 0);
  map_default.box            = point_t(2, 0);
  map_default.goal           = point_t(0, 2);
  map_default.pusher_on_goal = point_t(1, 2);
  map_default.box_on_goal    = point_t(2, 2);
  map_default.wall           = point_t(0, 4);

  map_down.floor          = point_t(0, 1);
  map_down.pusher         = point_t(1, 1);
  map_down.box            = point_t(2, 1);
  map_down.goal           = point_t(0, 3);
  map_down.pusher_on_goal = point_t(1, 3);
  map_down.box_on_goal    = point_t(2, 3);
  map_down.wall           = point_t(1, 4);

  if (rows_count >= 9) {
    map_default.directional_pushers[Direction::NORTH_EAST]         = point_t(0, 5);
    map_default.directional_pushers[Direction::SOUTH_WEST]         = point_t(1, 5);
    map_default.directional_pushers[Direction::SOUTH_EAST]         = point_t(1, 5);
    map_default.directional_pushers[Direction::NORTH_WEST]         = point_t(2, 5);
    map_default.directional_pushers_on_goal[Direction::NORTH_EAST] = point_t(0, 7);
    map_default.directional_pushers_on_goal[Direction::SOUTH_WEST] = point_t(1, 7);
    map_default.directional_pushers_on_goal[Direction::SOUTH_EAST] = point_t(1, 7);
    map_default.directional_pushers_on_goal[Direction::NORTH_WEST] = point_t(2, 7);

    map_down.directional_pushers[Direction::SOUTH_EAST]         = point_t(0, 6);
    map_down.directional_pushers[Direction::NORTH_WEST]         = point_t(1, 6);
    map_down.directional_pushers[Direction::NORTH_EAST]         = point_t(1, 6);
    map_down.directional_pushers[Direction::SOUTH_WEST]         = point_t(2, 6);
    map_down.directional_pushers_on_goal[Direction::SOUTH_EAST] = point_t(0, 8);
    map_down.directional_pushers_on_goal[Direction::NORTH_WEST] = point_t(1, 8);
    map_down.directional_pushers_on_goal[Direction::NORTH_EAST] = point_t(1, 8);
    map_down.directional_pushers_on_goal[Direction::SOUTH_WEST] = point_t(2, 8);
  }

  return retv;
}

polygon_t TriobanCommonSkinsFormat::tile_polygon(CellOrientation orientation) const {
  // Trioban tile image in skin image is placed into bounding rectangle such that:
  //
  // - width of bounding rectangle is equal to width of triangle
  // - height of bounding rectangle is < height of triangle
  // - triangle is aligned with bottom of bounding rectangle

  double a = m_columns_width; // Triangle side length
  double h = a * sqrt(3) / 2; // Triangle height

  if (orientation == CellOrientation::DEFAULT) {
    return polygon_t{
      {
       {0, h},
       {a, h},
       {a / 2, 0},
       {0, h},
       }
    };
  } else {
    return polygon_t{
      {
       {0, 0},
       {a / 2, h},
       {a, 0},
       {0, 0},
       }
    };
  }
}

pointf_t TriobanCommonSkinsFormat::tile_position(
  position_t board_position, board_size_t width, board_size_t height
) const {
  position_t x           = index_x(board_position, width);
  position_t y           = index_y(board_position, width);
  double     a           = m_columns_width;
  double     h           = a * sqrt(3) / 2;
  double     shift_right = a / 2;

  return pointf_t(x * shift_right, y * h);
}

point_t TriobanCommonSkinsFormat::canvas_size(
  board_size_t board_width, board_size_t board_height
) const {
  return point_t(
    (board_width / 1.85) * m_columns_width, (board_height * 1.05) * m_rows_height
  );
}

} // namespace implementation
} // namespace sokoengine
