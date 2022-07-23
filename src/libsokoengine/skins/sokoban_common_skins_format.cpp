#include "sokoban_common_skins_format.hpp"

namespace sokoengine {
namespace implementation {

SokobanCommonSkinsFormat::SokobanCommonSkinsFormat(
  uint8_t rows_count_hint, uint8_t columns_count_hint
)
  : CommonSkinsFormat(rows_count_hint, columns_count_hint) {}

SokobanCommonSkinsFormat::~SokobanCommonSkinsFormat() = default;

std::unique_ptr<CommonSkinsFormat> SokobanCommonSkinsFormat::clone() const {
  auto retv =
    std::make_unique<SokobanCommonSkinsFormat>(m_rows_count_hint, m_cols_count_hint);

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

tile_maps_t SokobanCommonSkinsFormat::categorize_tiles(const ImageImpl::tiles_t &src
) const {
  size_t rows_count    = src.size();
  size_t columns_count = rows_count > 0 ? src.back().size() : 0;

  if (rows_count < 3 || columns_count < 3) {
    throw std::invalid_argument(
      "Image doesn't appear to be a Sokoban skin! (detected "
      + std::to_string(rows_count) + " tile rows and " + std::to_string(columns_count)
      + " tile columns)"
    );
  }

  tile_maps_t retv;
  retv.try_emplace(CellOrientation::DEFAULT);
  tile_map_t &image_map = retv.at(CellOrientation::DEFAULT);

  image_map.floor          = point_t(0, 0);
  image_map.goal           = point_t(0, 1);
  image_map.pusher         = point_t(1, 0);
  image_map.pusher_on_goal = point_t(1, 1);
  image_map.box            = point_t(2, 0);
  image_map.box_on_goal    = point_t(2, 1);

  if (rows_count >= 4) {
    image_map.wall     = point_t(1, 3);
    image_map.wall_cap = point_t(2, 2);

    const ImageImpl &lurd_wall     = src[2][0];
    const ImageImpl &lr_wall       = src[2][1];
    const ImageImpl &ud_wall       = src[3][0];
    const ImageImpl &isolated_wall = src[3][1];
    generate_directional_walls(image_map, isolated_wall, lr_wall, ud_wall, lurd_wall);
  }

  if (
    columns_count >= 4
    // Don't try to parse directed pusher on images that have only animations
    && (
      // Has directed pusher, no animations
      rows_count == 6
      // Has directed pusher and animations
      || rows_count == 10
    )
  ) {
    image_map.directional_pushers[Direction::UP]            = point_t(0, 4);
    image_map.directional_pushers[Direction::LEFT]          = point_t(1, 4);
    image_map.directional_pushers[Direction::DOWN]          = point_t(2, 4);
    image_map.directional_pushers[Direction::RIGHT]         = point_t(3, 4);
    image_map.directional_pushers_on_goal[Direction::UP]    = point_t(0, 5);
    image_map.directional_pushers_on_goal[Direction::LEFT]  = point_t(1, 5);
    image_map.directional_pushers_on_goal[Direction::DOWN]  = point_t(2, 5);
    image_map.directional_pushers_on_goal[Direction::RIGHT] = point_t(3, 5);
  }

  if (rows_count == 8) {
    image_map.animated_pusher_row         = 4;
    image_map.animated_pusher_on_goal_row = 5;
    image_map.animated_box_row            = 6;
    image_map.animated_box_on_goal_row    = 7;
  }

  if (rows_count == 10) {
    image_map.animated_pusher_row         = 6;
    image_map.animated_pusher_on_goal_row = 7;
    image_map.animated_box_row            = 8;
    image_map.animated_box_on_goal_row    = 9;
  }

  return retv;
}

polygon_t SokobanCommonSkinsFormat::tile_polygon(CellOrientation orientation) const {
  double w = m_columns_width;
  double h = m_rows_height;
  return polygon_t{
    {
     {0, 0},
     {0, h},
     {w, h},
     {w, 0},
     {0, 0},
     }
  };
}

pointf_t SokobanCommonSkinsFormat::tile_position(
  position_t board_position, board_size_t width, board_size_t height
) const {
  return pointf_t(
    index_x(board_position, width) * m_columns_width,
    index_y(board_position, width) * m_rows_height
  );
}

void SokobanCommonSkinsFormat::generate_directional_walls(
  tile_map_t      &tile_map,
  const ImageImpl &isolated_wall,
  const ImageImpl &lr_wall,
  const ImageImpl &ud_wall,
  const ImageImpl &lurd_wall
) {
  ImageImpl tmp;

  auto push_back = [&](const Directions &dirs) {
    tile_map.directional_walls.emplace_back();
    tile_map.directional_walls.back().first = dirs;
    tmp.swap(tile_map.directional_walls.back().second);
  };

  tmp = isolated_wall;
  push_back(Directions());

  tmp = lr_wall;
  push_back(Directions({Direction::LEFT, Direction::RIGHT}));

  tmp = ud_wall;
  push_back(Directions({Direction::UP, Direction::DOWN}));

  tmp = lurd_wall;
  push_back(
    Directions({Direction::LEFT, Direction::RIGHT, Direction::UP, Direction::DOWN})
  );

  tmp = isolated_wall;
  tmp.replace(ud_wall, down_half(tmp));
  push_back(Directions{Direction::DOWN});

  tmp = isolated_wall;
  tmp.replace(ud_wall, up_half(tmp));
  push_back(Directions{Direction::UP});

  tmp = isolated_wall;
  tmp.replace(lr_wall, right_half(tmp));
  push_back(Directions{Direction::RIGHT});

  tmp = isolated_wall;
  tmp.replace(ud_wall, down_half(tmp));
  tmp.replace(lr_wall, right_half(tmp));
  tmp.replace(lurd_wall, right_bottom_quarter(tmp));
  push_back(Directions{Direction::RIGHT, Direction::DOWN});

  tmp = isolated_wall;
  tmp.replace(lr_wall, right_half(tmp));
  tmp.replace(ud_wall, up_half(tmp));
  tmp.replace(lurd_wall, right_top_quarter(tmp));
  push_back(Directions{Direction::RIGHT, Direction::UP});

  tmp = lurd_wall;
  tmp.replace(ud_wall, left_half(tmp));
  push_back(Directions{Direction::RIGHT, Direction::UP, Direction::DOWN});

  tmp = isolated_wall;
  tmp.replace(lr_wall, left_half(tmp));
  push_back(Directions{Direction::LEFT});

  tmp = isolated_wall;
  tmp.replace(lr_wall, left_half(tmp));
  tmp.replace(ud_wall, down_half(tmp));
  tmp.replace(lurd_wall, left_bottom_quarter(tmp));
  push_back(Directions{Direction::LEFT, Direction::DOWN});

  tmp = isolated_wall;
  tmp.replace(lr_wall, left_half(tmp));
  tmp.replace(ud_wall, up_half(tmp));
  tmp.replace(lurd_wall, left_top_quarter(tmp));
  push_back(Directions{Direction::LEFT, Direction::UP});

  tmp = lurd_wall;
  tmp.replace(ud_wall, right_half(tmp));
  push_back(Directions{Direction::LEFT, Direction::UP, Direction::DOWN});

  tmp = lurd_wall;
  tmp.replace(lr_wall, up_half(tmp));
  push_back(Directions{Direction::LEFT, Direction::RIGHT, Direction::DOWN});

  tmp = lurd_wall;
  tmp.replace(lr_wall, down_half(tmp));
  push_back(Directions{Direction::LEFT, Direction::RIGHT, Direction::UP});
}

rect_t SokobanCommonSkinsFormat::left_half(const ImageImpl &src) {
  return rect_t(0, 0, src.width() / 2, src.height());
}

rect_t SokobanCommonSkinsFormat::right_half(const ImageImpl &src) {
  return rect_t(src.width() / 2, 0, src.width() / 2, src.height());
}

rect_t SokobanCommonSkinsFormat::up_half(const ImageImpl &src) {
  return rect_t(0, 0, src.width(), src.height() / 2);
}

rect_t SokobanCommonSkinsFormat::down_half(const ImageImpl &src) {
  return rect_t(0, src.height() / 2, src.width(), src.height() / 2);
}

rect_t SokobanCommonSkinsFormat::left_top_quarter(const ImageImpl &src) {
  return rect_t(0, 0, src.width() / 2, src.height() / 2);
}

rect_t SokobanCommonSkinsFormat::right_top_quarter(const ImageImpl &src) {
  return rect_t(src.width() / 2, 0, src.width() / 2, src.height() / 2);
}

rect_t SokobanCommonSkinsFormat::left_bottom_quarter(const ImageImpl &src) {
  return rect_t(0, src.height() / 2, src.width() / 2, src.height() / 2);
}

rect_t SokobanCommonSkinsFormat::right_bottom_quarter(const ImageImpl &src) {
  return rect_t(src.width() / 2, src.height() / 2, src.width() / 2, src.height() / 2);
}

} // namespace implementation
} // namespace sokoengine
