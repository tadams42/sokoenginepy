#include "common_skins_format.hpp"

#include "image.hpp"
#include "image_impl.hpp"
#include "tessellation.hpp"

using std::map;

namespace sokoengine {
namespace implementation {

CommonSkinsFormat::~CommonSkinsFormat()               = default;
SokobanCommonSkinsFormat::~SokobanCommonSkinsFormat() = default;
HexobanCommonSkinsFormat::~HexobanCommonSkinsFormat() = default;
OctobanCommonSkinsFormat::~OctobanCommonSkinsFormat() = default;
TriobanCommonSkinsFormat::~TriobanCommonSkinsFormat() = default;

tile_sizes_t CommonSkinsFormat::guess_tile_sizes(
  uint16_t img_width,
  uint16_t img_height,
  uint8_t  rows_count_hint,
  uint8_t  columns_count_hint
) const {
  // The following code is a derivative work of the code from the SokobanYASC project,
  // which is licensed GPLv2. This code therefore is also licensed under the terms of
  // the GNU Public License, version 2.
  //
  // SokobanYASC Copyright by briandamgaard and SokobanYASC contributors under GPLv2.
  // https://sourceforge.net/projects/sokobanyasc/
  // https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html

  // Algorithm implemented here was translated to C++ using implementation from
  // SokobanYASC TSkins.GuessColumnsAndRows

  uint16_t col_width = 0, col_height = 0;

  bool success = false;

  uint16_t cols_count = columns_count_hint == 0 ? 4 : columns_count_hint;
  uint16_t rows_count = rows_count_hint == 0 ? 1 : rows_count_hint;

  uint16_t start_col_count         = cols_count;
  uint16_t oblonged_tile_col_count = 0;

  while (!success && rows_count <= img_height) {
    while (rows_count <= img_height && img_height % rows_count != 0)
      rows_count += 1;

    col_height = std::div(img_height, rows_count).quot;
    cols_count = start_col_count;

    while (!success && cols_count < img_width) {
      if (img_width % cols_count == 0) {
        if (
          // 'True': a square tile
          std::div(img_width, cols_count).quot == col_height
          && (
            // '<=256': tiles are probably not bigger than 256x256 pixels
            col_height <= 256
            || (
              // check if it looks like a 1-row skin with very large tiles up to 512x512
              rows_count == 1 && cols_count >= 7 && col_height <= 512
            )
          )
        ) {
          success = true;
        } else {
          if (
            // clang-format off
            rows_count == 1
            && cols_count >= 4
            && cols_count < img_width
            && img_height <= 32
            && oblonged_tile_col_count == 0
            // clang-format on
          ) {
            // remember this column count and use it unless there is a square tile
            oblonged_tile_col_count = cols_count;
          }
          cols_count += 1;
        }
      } else {
        cols_count += 1;
      }
    }

    if (!success) {
      if (rows_count > 1 || oblonged_tile_col_count == 0) {
        rows_count += 1;
      } else {
        success    = true;
        cols_count = oblonged_tile_col_count;
      }
    }
  }

  if (
    (!success
    || (
      // 'True': a heuristic: the number of tiles seems unreasonably high
      cols_count >= 12 && rows_count >= 12
    ))
    && img_width >= 64
    && img_height >= 64
    && (
      img_width % std::div(img_width, 4).quot == 0
    )
    && (
      (  img_height % std::div(img_height,  4).quot == 0 )
      || (  img_height % std::div(img_height, 6).quot == 0 )
    )
  ) {
    // 'True' : assume the skin has 4 x 4 or 4 x 6 non-square tiles
    cols_count = 4;
    if (img_height % std::div(img_height, 4).quot == 0) {
      rows_count = 4;
    } else {
      rows_count = 6;
    }
    success = true;
  }

  if (!success) {
    throw std::invalid_argument(
      "Failed to calculate tile columns and rows counts from image "
    );
  }

  col_width  = std::div(img_width, cols_count).quot;
  col_height = std::div(img_height, rows_count).quot;

  if (rows_count * col_height != img_height || cols_count * col_width != img_width)
    throw std::invalid_argument(
      "Skin image width and height not divisible by tile width and height!"
    );

  tile_sizes_t retv;
  retv.original_tile_height = col_height;
  retv.original_tile_width  = col_width;
  retv.columns_count        = cols_count;
  retv.rows_count           = rows_count;

  auto box =
    bounding_rect(tile_polygon(col_width, col_height, CellOrientation::DEFAULT))
      .to_aligned_rect();
  retv.tile_height = box.height();
  retv.tile_width  = box.width();

  return retv;
}

map<CellOrientation, tile_map_t>
SokobanCommonSkinsFormat::categorize_tiles(const raw_tiles_t &src) const {
  size_t rows_count    = src.size();
  size_t columns_count = rows_count > 0 ? src.back().size() : 0;

  if (rows_count < 3 || columns_count < 3) {
    throw std::invalid_argument(
      "Image doesn't appear to be a Sokoban skin! (detected "
      + std::to_string(rows_count) + " tile rows and " + std::to_string(columns_count)
      + " tile columns)"
    );
  }

  map<CellOrientation, tile_map_t> retv;
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

polygon_t SokobanCommonSkinsFormat::tile_polygon(
  uint16_t        original_tile_width,
  uint16_t        original_tile_height,
  CellOrientation orientation
) const {
  double w = original_tile_width;
  double h = original_tile_height;
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
  uint16_t     original_tile_width,
  uint16_t     original_tile_height,
  position_t   board_position,
  board_size_t width,
  board_size_t height
) const {
  return pointf_t(
    index_x(board_position, width) * original_tile_width,
    index_y(board_position, width) * original_tile_height
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

map<CellOrientation, tile_map_t>
HexobanCommonSkinsFormat::categorize_tiles(const raw_tiles_t &src) const {
  size_t rows_count    = src.size();
  size_t columns_count = rows_count > 0 ? src.back().size() : 0;

  if (rows_count < 3 || columns_count < 3) {
    throw std::invalid_argument(
      "Image doesn't appear to be a Hexoban skin! (detected "
      + std::to_string(rows_count) + " tile rows and " + std::to_string(columns_count)
      + " tile columns)"
    );
  }

  map<CellOrientation, tile_map_t> retv;
  retv.try_emplace(CellOrientation::DEFAULT);
  tile_map_t &image_map = retv.at(CellOrientation::DEFAULT);

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

polygon_t HexobanCommonSkinsFormat::tile_polygon(
  uint16_t        original_tile_width,
  uint16_t        original_tile_height,
  CellOrientation orientation
) const {
  // double w = original_tile_width;
  double h = original_tile_height;

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
  uint16_t     original_tile_width,
  uint16_t     original_tile_height,
  position_t   board_position,
  board_size_t width,
  board_size_t height
) const {
  position_t x = index_x(board_position, width);
  position_t y = index_y(board_position, width);

  polygon_t polygon =
    tile_polygon(original_tile_width, original_tile_height, CellOrientation::DEFAULT);
  rectf_t rect = bounding_rect(polygon);

  double w = rect.width();
  double h = rect.height();

  double shift_right = w / 2;
  double shift_up    = h / 4;

  pointf_t pos;
  pos.x(y % 2 == 0 ? x * w : x * w + shift_right);
  pos.y(y * (h - shift_up));

  return pos;
}

map<CellOrientation, tile_map_t>
TriobanCommonSkinsFormat::categorize_tiles(const raw_tiles_t &src) const {
  size_t rows_count    = src.size();
  size_t columns_count = rows_count > 0 ? src.back().size() : 0;

  if (rows_count < 3 || columns_count < 3) {
    throw std::invalid_argument(
      "Image doesn't appear to be a Trioban skin! (detected "
      + std::to_string(rows_count) + " tile rows and " + std::to_string(columns_count)
      + " tile columns)"
    );
  }

  map<CellOrientation, tile_map_t> retv;
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

tile_sizes_t TriobanCommonSkinsFormat::guess_tile_sizes(
  uint16_t img_width,
  uint16_t img_height,
  uint8_t  rows_count_hint,
  uint8_t  columns_count_hint
) const {
  return CommonSkinsFormat::guess_tile_sizes(
    img_width,
    img_height,
    rows_count_hint == 0 ? 3 : rows_count_hint,
    columns_count_hint == 0 ? 3 : columns_count_hint
  );
}

polygon_t TriobanCommonSkinsFormat::tile_polygon(
  uint16_t        original_tile_width,
  uint16_t        original_tile_height,
  CellOrientation orientation
) const {
  // Trioban tile image in skin image is placed into bounding rectangle such that:
  //
  // - width of bounding rectangle is equal to width of triangle
  // - height of bounding rectangle is < height of triangle
  // - triangle is aligned with bottom of bounding rectangle

  // QPolygonF triangle(4);

  double a = original_tile_width; // Triangle side length
  double h = a * sqrt(3) / 2;     // Triangle height

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
  uint16_t     original_tile_width,
  uint16_t     original_tile_height,
  position_t   board_position,
  board_size_t width,
  board_size_t height
) const {
  position_t x           = index_x(board_position, width);
  position_t y           = index_y(board_position, width);
  double     a           = original_tile_width;
  double     h           = a * sqrt(3) / 2;
  double     shift_right = a / 2;

  return pointf_t(x * shift_right, y * h);
}

map<CellOrientation, tile_map_t>
OctobanCommonSkinsFormat::categorize_tiles(const raw_tiles_t &src) const {
  // TODO
  return SokobanCommonSkinsFormat().categorize_tiles(src);
}

polygon_t OctobanCommonSkinsFormat::tile_polygon(
  uint16_t        original_tile_width,
  uint16_t        original_tile_height,
  CellOrientation orientation
) const {
  // TODO
  return SokobanCommonSkinsFormat().tile_polygon(
    original_tile_width, original_tile_height, orientation
  );
}

pointf_t OctobanCommonSkinsFormat::tile_position(
  uint16_t     original_tile_width,
  uint16_t     original_tile_height,
  position_t   board_position,
  board_size_t width,
  board_size_t height
) const {
  // TODO
  return SokobanCommonSkinsFormat().tile_position(
    original_tile_width, original_tile_height, board_position, width, height
  );
}

} // namespace implementation
} // namespace sokoengine
