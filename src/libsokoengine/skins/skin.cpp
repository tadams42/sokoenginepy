#include "skin.hpp"

#include "common_skins_format.hpp"
#include "geometry.hpp"
#include "image.hpp"
#include "image_impl.hpp"

#include <boost/algorithm/string.hpp>

using sokoengine::implementation::bounding_rect;
using sokoengine::implementation::CommonSkinsFormat;
using sokoengine::implementation::HexobanCommonSkinsFormat;
using sokoengine::implementation::ImageImpl;
using sokoengine::implementation::OctobanCommonSkinsFormat;
using sokoengine::implementation::raw_tiles_t;
using sokoengine::implementation::SokobanCommonSkinsFormat;
using sokoengine::implementation::tile_map_t;
using sokoengine::implementation::tile_sizes_t;
using sokoengine::implementation::TriobanCommonSkinsFormat;
using std::istream;
using std::map;
using std::string;
using std::unique_ptr;
using std::vector;

namespace fs = std::filesystem;

namespace sokoengine {
namespace skins {

//
// All tile images for single cell orientation.
//
// In Trioban, we need two pusher on goal images: one for situation when pusher is on
// triangle pointing up, and another for triangle pointing down. Similarly for other
// tile types. This means that Trioban will have two sets of tiles: one for "triangle
// pointing up" and other for "triangle pointing down". Octoban would have one set for
// "square" tiles and other for "octagon" tiles.
//
// In Sokoban and Hexoban tessellations, we only have one possible cell orientation and
// thus need single set of tile images.
//
// tileset_t represents set of board tiles for one CellOrientation.
//
struct LIBSOKOENGINE_LOCAL tileset_t {
  Image floor;
  Image non_playable_floor;
  Image goal;
  Image pusher;
  Image pusher_on_goal;
  Image box;
  Image box_on_goal;
  Image wall;
  Image wall_cap;

  Skin::directional_pushers_t directional_pushers;
  Skin::directional_pushers_t directional_pushers_on_goal;
  Skin::directional_walls_t   directional_walls;

  Skin::animation_frames_t animated_pusher;
  Skin::animation_frames_t animated_pusher_on_goal;
  Skin::animation_frames_t animated_box;
  Skin::animation_frames_t animated_box_on_goal;
};

class LIBSOKOENGINE_LOCAL Skin::PIMPL {
public:
  Tessellation                  m_tessellation;
  unique_ptr<CommonSkinsFormat> m_format;

  string m_path;

  uint8_t  m_rows_count_hint      = 0;
  uint8_t  m_cols_count_hint      = 0;
  uint16_t m_original_tile_width  = 0;
  uint16_t m_original_tile_height = 0;
  uint16_t m_tile_width           = 0;
  uint16_t m_tile_height          = 0;
  uint16_t m_rows_count           = 0;
  uint16_t m_columns_count        = 0;

  tiles_matrix_t                                  m_original_tiles;
  map<CellOrientation, implementation::polygon_t> m_polygons;
  map<CellOrientation, tileset_t>                 m_tilesets;

  Image m_empty_image;

  PIMPL(
    Tessellation  tessellation,
    const string &path,
    uint16_t      rows_count_hint,
    uint16_t      columns_count_hint
  )
    : m_tessellation(tessellation)
    , m_path(path)
    , m_rows_count_hint(rows_count_hint)
    , m_cols_count_hint(columns_count_hint) {
    init_format();

    raw_tiles_t raw_tiles;

    {
      ImageImpl img;
      img.load(m_path);
      slice_tiles(img, raw_tiles);
    }

    apply_tiles(raw_tiles);
  }

  PIMPL(
    Tessellation tessellation,
    istream     &src,
    ImageFormats format,
    uint8_t      rows_count_hint,
    uint8_t      columns_count_hint
  )
    : m_tessellation(tessellation)
    , m_rows_count_hint(rows_count_hint)
    , m_cols_count_hint(columns_count_hint) {
    init_format();

    raw_tiles_t raw_tiles;

    {
      ImageImpl img;
      img.load(src, format);
      slice_tiles(img, raw_tiles);
    }

    apply_tiles(raw_tiles);
  }

  PIMPL(
    Tessellation tessellation,
    uint16_t     original_tile_width,
    uint16_t     original_tile_height
  )
    : m_tessellation(tessellation)
    , m_original_tile_width(original_tile_width)
    , m_original_tile_height(original_tile_height) {
    init_format();
    init_tile_sizes();

    for (auto orientation : m_format->cell_orientations()) {
      m_polygons.try_emplace(
        orientation,
        m_format->tile_polygon(
          m_original_tile_width, m_original_tile_height, orientation
        )
      );
    }
  }

  PIMPL(const PIMPL &rv)
    : m_tessellation(rv.m_tessellation)
    , m_format(rv.m_format->clone())
    , m_path(rv.m_path)
    , m_rows_count_hint(rv.m_rows_count_hint)
    , m_cols_count_hint(rv.m_cols_count_hint)
    , m_original_tile_width(rv.m_original_tile_width)
    , m_original_tile_height(rv.m_original_tile_height)
    , m_tile_width(rv.m_tile_width)
    , m_tile_height(rv.m_tile_height)
    , m_rows_count(rv.m_rows_count)
    , m_columns_count(rv.m_columns_count)
    , m_original_tiles(rv.m_original_tiles)
    , m_polygons(rv.m_polygons)
    , m_tilesets(rv.m_tilesets) {}

  PIMPL &operator=(const PIMPL &rv) {
    if (this != &rv) {
      m_tessellation         = rv.m_tessellation;
      m_format               = rv.m_format->clone();
      m_path                 = rv.m_path;
      m_rows_count_hint      = rv.m_rows_count_hint;
      m_cols_count_hint      = rv.m_cols_count_hint;
      m_original_tile_width  = rv.m_original_tile_width;
      m_original_tile_height = rv.m_original_tile_height;
      m_tile_width           = rv.m_tile_width;
      m_tile_height          = rv.m_tile_height;
      m_rows_count           = rv.m_rows_count;
      m_columns_count        = rv.m_columns_count;
      m_original_tiles       = rv.m_original_tiles;
      m_polygons             = rv.m_polygons;
      m_tilesets             = rv.m_tilesets;
    }
    return *this;
  }

  PIMPL(PIMPL &&)            = default;
  PIMPL &operator=(PIMPL &&) = default;
  ~PIMPL()                   = default;

  bool is_empty() const {
    return m_original_tiles.size() == 0 || m_tilesets.size() == 0;
  }

private:
  void apply_tiles(raw_tiles_t &from) {
    auto raw_tiles = m_format->categorize_tiles(from);

    for (const auto &[orientation, tile_map] : raw_tiles) {
      m_polygons.try_emplace(
        orientation,
        m_format->tile_polygon(
          m_original_tile_width, m_original_tile_height, orientation
        )
      );
      m_tilesets.try_emplace(orientation);

      const implementation::polygon_t &polygon      = m_polygons.at(orientation);
      tileset_t                       &dest_tileset = m_tilesets.at(orientation);

      apply_tileset(from, raw_tiles.at(orientation), dest_tileset, polygon);
    }

    m_original_tiles = tiles_matrix_t(m_rows_count, vector<Image>(m_columns_count));
    for (size_t row = 0; row < m_rows_count; ++row) {
      for (size_t column = 0; column < m_columns_count; ++column) {
        from[row][column].swap(m_original_tiles[row][column]);
      }
    }
  }

  void apply_tileset(
    const raw_tiles_t              &from,
    const tile_map_t               &tile_map,
    tileset_t                      &into,
    const implementation::polygon_t polygon
  ) {
    ImageImpl img;

    auto crop = [&](const ImageImpl &src, Image &dest) {
      ImageImpl i = src;
      i.crop_to_bounding_box(polygon);
      i.swap(dest);
    };

    auto crop_transparent = [&](const ImageImpl &src, Image &dest) {
      ImageImpl i = src;
      i.crop_to_bounding_box(polygon);
      i.set_outer_pixels_transparent(polygon);
      i.swap(dest);
    };

    auto crop_transparent_grey = [&](const ImageImpl &src, Image &dest) {
      ImageImpl i = src;
      i.crop_to_bounding_box(polygon);
      i.set_outer_pixels_transparent(polygon);
      i.grayscale();
      i.swap(dest);
    };

    auto crop_transparent_mask = [&](const ImageImpl &src, Image &dest) {
      const ImageImpl &floor = from[tile_map.floor.y()][tile_map.floor.x()];
      ImageImpl        i     = src;
      i.subtract(floor);
      i.crop_to_bounding_box(polygon);
      i.set_outer_pixels_transparent(polygon);
      i.swap(dest);
    };

    crop_transparent(from[tile_map.floor.y()][tile_map.floor.x()], into.floor);
    crop_transparent_grey(
      from[tile_map.floor.y()][tile_map.floor.x()], into.non_playable_floor
    );

    crop_transparent(from[tile_map.goal.y()][tile_map.goal.x()], into.goal);

    crop_transparent_mask(from[tile_map.pusher.y()][tile_map.pusher.x()], into.pusher);
    crop_transparent_mask(
      from[tile_map.pusher_on_goal.y()][tile_map.pusher_on_goal.x()],
      into.pusher_on_goal
    );
    crop_transparent_mask(from[tile_map.box.y()][tile_map.box.x()], into.box);
    crop_transparent_mask(
      from[tile_map.box_on_goal.y()][tile_map.box_on_goal.x()], into.box_on_goal
    );

    crop(from[tile_map.wall.y()][tile_map.wall.x()], into.wall);
    crop(from[tile_map.wall_cap.y()][tile_map.wall_cap.x()], into.wall_cap);

    for (const auto &[direction, position] : tile_map.directional_pushers) {
      into.directional_pushers.try_emplace(direction);
      crop_transparent_mask(
        from[position.y()][position.x()], into.directional_pushers.at(direction)
      );
    }
    for (const auto &[direction, position] : tile_map.directional_pushers_on_goal) {
      into.directional_pushers_on_goal.try_emplace(direction);
      crop_transparent_mask(
        from[position.y()][position.x()], into.directional_pushers_on_goal.at(direction)
      );
    }

    for (const auto &dir_wall : tile_map.directional_walls) {
      into.directional_walls.emplace_back(dir_wall.first, Image());
      crop(dir_wall.second, into.directional_walls.back().second);
    }

    if (tile_map.animated_pusher_row > 0) {
      for (const ImageImpl &tile : from[tile_map.animated_pusher_row]) {
        into.animated_pusher.emplace_back();
        crop_transparent_mask(tile, into.animated_pusher.back());
      }
    }

    if (tile_map.animated_pusher_on_goal_row > 0) {
      for (const ImageImpl &tile : from[tile_map.animated_pusher_on_goal_row]) {
        into.animated_pusher_on_goal.emplace_back();
        crop_transparent_mask(tile, into.animated_pusher_on_goal.back());
      }
    }

    if (tile_map.animated_box_row > 0) {
      for (const ImageImpl &tile : from[tile_map.animated_box_row]) {
        into.animated_box.emplace_back();
        crop_transparent_mask(tile, into.animated_box.back());
      }
    }

    if (tile_map.animated_box_on_goal_row > 0) {
      for (const ImageImpl &tile : from[tile_map.animated_box_on_goal_row]) {
        into.animated_box_on_goal.emplace_back();
        crop_transparent_mask(tile, into.animated_box_on_goal.back());
      }
    }
  }

  void slice_tiles(ImageImpl &from, raw_tiles_t &into) {
    tile_sizes_t sizes = m_format->guess_tile_sizes(
      from.width(), from.height(), m_rows_count_hint, m_cols_count_hint
    );
    m_original_tile_width  = sizes.original_tile_width;
    m_original_tile_height = sizes.original_tile_height;
    m_rows_count           = sizes.rows_count;
    m_columns_count        = sizes.columns_count;
    init_tile_sizes();

    for (size_t row = 0; row < m_rows_count; ++row) {
      into.emplace_back(m_columns_count);
      vector<ImageImpl> &row_data = into.back();

      for (size_t column = 0; column < m_columns_count; ++column) {
        implementation::rect_t tile_rect(
          column * m_original_tile_width,
          row * m_original_tile_height,
          m_original_tile_width,
          m_original_tile_height
        );
        row_data[column] = from.subimage(tile_rect);
      }
    }
  }

  void init_tile_sizes() {
    auto box = bounding_rect(m_format->tile_polygon(
                               m_original_tile_width,
                               m_original_tile_height,
                               CellOrientation::DEFAULT
                             ))
                 .to_aligned_rect();
    m_tile_height = box.height();
    m_tile_width  = box.width();
  }

  void init_format() {
    bool found = false;
    switch (m_tessellation) {
      case Tessellation::SOKOBAN:
        m_format = std::make_unique<SokobanCommonSkinsFormat>();
        found    = true;
        break;
      case Tessellation::HEXOBAN:
        m_format = std::make_unique<HexobanCommonSkinsFormat>();
        found    = true;
        break;
      case Tessellation::TRIOBAN:
        m_format = std::make_unique<TriobanCommonSkinsFormat>();
        found    = true;
        break;
      case Tessellation::OCTOBAN:
        m_format = std::make_unique<OctobanCommonSkinsFormat>();
        found    = true;
        break;
        // Don't use default so we get compiler warning
    };
    if (!found) {
      throw std::invalid_argument("Unknown tessellation!");
    }
  }
};

Skin::Skin(
  Tessellation  tessellation,
  const string &path,
  uint8_t       rows_count_hint,
  uint8_t       columns_count_hint
)
  : m_impl(
    std::make_unique<PIMPL>(tessellation, path, rows_count_hint, columns_count_hint)
  ) {}

Skin::Skin(
  Tessellation tessellation,
  istream     &src,
  ImageFormats format,
  uint8_t      rows_count_hint,
  uint8_t      columns_count_hint
)
  : m_impl(std::make_unique<PIMPL>(
    tessellation, src, format, rows_count_hint, columns_count_hint
  )) {}

Skin::Skin(
  Tessellation tessellation, uint16_t original_tile_width, uint16_t original_tile_height
)
  : m_impl(
    std::make_unique<PIMPL>(tessellation, original_tile_width, original_tile_height)
  ) {}

Skin::Skin(const Skin &rv)
  : m_impl(std::make_unique<PIMPL>(*rv.m_impl)) {}

Skin &Skin::operator=(const Skin &rv) {
  if (this != &rv) {
    m_impl = std::make_unique<PIMPL>(*rv.m_impl);
  };
  return *this;
}

Skin::Skin(Skin &&)            = default;
Skin &Skin::operator=(Skin &&) = default;
Skin::~Skin()                  = default;

const string &Skin::path() const { return m_impl->m_path; }

uint16_t Skin::rows_count() const { return m_impl->m_rows_count; }

uint16_t Skin::columns_count() const { return m_impl->m_columns_count; }

uint16_t Skin::original_tile_width() const { return m_impl->m_original_tile_width; }

uint16_t Skin::original_tile_height() const { return m_impl->m_original_tile_height; }

const Skin::tiles_matrix_t &Skin::tiles() const { return m_impl->m_original_tiles; }

uint16_t Skin::tile_width() const { return m_impl->m_tile_width; }

uint16_t Skin::tile_height() const { return m_impl->m_tile_width; }

Skin::polygon_t Skin::tile_polygon(CellOrientation orientation) const {
  const implementation::polygon_t &p = m_impl->m_polygons.at(orientation);

  Skin::polygon_t retv;
  for (const auto &pnt : p.outer()) {
    retv.push_back(std::make_pair(pnt.x(), pnt.y()));
  }

  return retv;
}

Skin::point_t Skin::tile_position(
  position_t board_position, board_size_t width, board_size_t height
) const {
  auto p = m_impl->m_format->tile_position(
    m_impl->m_original_tile_width,
    m_impl->m_original_tile_height,
    board_position,
    width,
    height
  );
  return std::make_pair(p.x(), p.y());
}

bool Skin::is_empty() const { return m_impl->is_empty(); }

vector<CellOrientation> Skin::cell_orientations() const {
  return m_impl->m_format->cell_orientations();
}

const Image &Skin::floor(CellOrientation orientation) const {
  if (is_empty())
    return m_impl->m_empty_image;
  return m_impl->m_tilesets.at(orientation).floor;
}

const Image &Skin::non_playable_floor(CellOrientation orientation) const {
  if (is_empty())
    return m_impl->m_empty_image;
  return m_impl->m_tilesets.at(orientation).non_playable_floor;
}

const Image &Skin::goal(CellOrientation orientation) const {
  if (is_empty())
    return m_impl->m_empty_image;
  return m_impl->m_tilesets.at(orientation).goal;
}

const Image &Skin::pusher(CellOrientation orientation) const {
  if (is_empty())
    return m_impl->m_empty_image;
  return m_impl->m_tilesets.at(orientation).pusher;
}

const Image &Skin::pusher_on_goal(CellOrientation orientation) const {
  if (is_empty())
    return m_impl->m_empty_image;
  return m_impl->m_tilesets.at(orientation).pusher_on_goal;
}

const Image &Skin::box(CellOrientation orientation) const {
  if (is_empty())
    return m_impl->m_empty_image;
  return m_impl->m_tilesets.at(orientation).box;
}

const Image &Skin::box_on_goal(CellOrientation orientation) const {
  if (is_empty())
    return m_impl->m_empty_image;
  return m_impl->m_tilesets.at(orientation).box_on_goal;
}

const Image &Skin::wall(CellOrientation orientation) const {
  if (is_empty())
    return m_impl->m_empty_image;
  return m_impl->m_tilesets.at(orientation).wall;
}

const Image &Skin::wall_cap(CellOrientation orientation) const {
  if (is_empty())
    return m_impl->m_empty_image;
  return m_impl->m_tilesets.at(orientation).wall_cap;
}

const Skin::directional_pushers_t &Skin::directional_pushers(CellOrientation orientation
) const {
  return m_impl->m_tilesets.at(orientation).directional_pushers;
}

const Image &Skin::pusher(Direction looking_at, CellOrientation orientation) const {
  if (is_empty())
    return m_impl->m_empty_image;
  return m_impl->m_tilesets.at(orientation).directional_pushers.at(looking_at);
}

const Skin::directional_pushers_t &
Skin::directional_pushers_on_goal(CellOrientation orientation) const {
  return m_impl->m_tilesets.at(orientation).directional_pushers_on_goal;
}

const Image &
Skin::pusher_on_goal(Direction looking_at, CellOrientation orientation) const {
  if (is_empty())
    return m_impl->m_empty_image;
  return m_impl->m_tilesets.at(orientation).directional_pushers_on_goal.at(looking_at);
}

const Skin::directional_walls_t &Skin::directional_walls(CellOrientation orientation
) const {
  return m_impl->m_tilesets.at(orientation).directional_walls;
}

const Skin::animation_frames_t &Skin::animated_pusher(CellOrientation orientation
) const {
  return m_impl->m_tilesets.at(orientation).animated_pusher;
}

const Skin::animation_frames_t &
Skin::animated_pusher_on_goal(CellOrientation orientation) const {
  return m_impl->m_tilesets.at(orientation).animated_pusher_on_goal;
}

const Skin::animation_frames_t &Skin::animated_box(CellOrientation orientation) const {
  return m_impl->m_tilesets.at(orientation).animated_box;
}

const Skin::animation_frames_t &Skin::animated_box_on_goal(CellOrientation orientation
) const {
  return m_impl->m_tilesets.at(orientation).animated_box_on_goal;
}

void Skin::dump_tiles(const std::string &dir) const {
  fs::path dir_path(dir);
  fs::path originals           = dir_path / "originals";
  fs::path directional_pushers = dir_path / "directional_pushers";
  fs::path directional_walls   = dir_path / "directional_walls";
  fs::path animations          = dir_path / "animations";

  fs::create_directories(originals);

  auto direction_to_str = [](Direction d) {
    switch (d) {
      case Direction::UP:
        return string("UP");
      case Direction::DOWN:
        return string("DOWN");
      case Direction::LEFT:
        return string("LEFT");
      case Direction::RIGHT:
        return string("RIGHT");
      case Direction::NORTH_EAST:
        return string("NORTH_EAST");
      case Direction::NORTH_WEST:
        return string("NORTH_WEST");
      case Direction::SOUTH_EAST:
        return string("SOUTH_EAST");
      case Direction::SOUTH_WEST:
        return string("SOUTH_WEST");
    }
    throw std::invalid_argument("Unhandled Direction!");
  };

  auto orientation_to_str = [](CellOrientation o) {
    switch (o) {
      case CellOrientation::DEFAULT:
        return string("DEFAULT");
      case CellOrientation::OCTAGON:
        return string("OCTAGON");
      case CellOrientation::TRIANGLE_DOWN:
        return string("TRIANGLE_DOWN");
    }
    throw std::invalid_argument("Unhandled CellOrientation!");
  };

  auto tile_path = [&](const string &tile, CellOrientation co) {
    return (dir_path / (orientation_to_str(co) + "_" + tile + ".png")).string();
    ;
  };

  auto directional_pusher_path = [&](
                                   Direction d, CellOrientation co, const string &tile
                                 ) {
    return (directional_pushers
            / (orientation_to_str(co) + "_" + direction_to_str(d) + "_" + tile + ".png")
    )
      .string();
  };

  auto directional_wall_path = [&](const Directions &dirs, CellOrientation co) {
    std::vector<string> l;
    for (auto d : dirs) {
      l.push_back(direction_to_str(d));
    }

    return (directional_walls
            / (orientation_to_str(co) + "_" + boost::join(l, "-") + ".png"))
      .string();
  };

  auto src_tile_path = [&](int row, int col) {
    return (originals / (std::to_string(row) + "-" + std::to_string(col) + ".png"))
      .string();
  };

  auto animation_path = [&](CellOrientation co, const string &tile, int idx) {
    return (animations
            / (orientation_to_str(co) + "_" + tile + "_" + std::to_string(idx) + ".png")
    )
      .string();
  };

  auto save = [](const Image &tile, const string &path) {
    if (!tile.is_empty()) {
      tile.save(path);
    }
  };

  for (CellOrientation o : cell_orientations()) {
    const auto &tileset = m_impl->m_tilesets.at(o);

    save(tileset.floor, tile_path("floor", o));
    save(tileset.non_playable_floor, tile_path("non_playable_floor", o));
    save(tileset.goal, tile_path("goal", o));
    save(tileset.pusher, tile_path("pusher", o));
    save(tileset.pusher_on_goal, tile_path("pusher_on_goal", o));
    save(tileset.box, tile_path("box", o));
    save(tileset.box_on_goal, tile_path("box_on_goal", o));
    save(tileset.wall, tile_path("wall", o));
    save(tileset.wall_cap, tile_path("wall_cap", o));

    if (tileset.directional_pushers.size() > 0 || tileset.directional_pushers_on_goal.size() > 0)
      fs::create_directories(directional_pushers);

    for (const auto &[direction, tile] : tileset.directional_pushers) {
      save(tile, directional_pusher_path(direction, o, "p"));
    }
    for (const auto &[direction, tile] : tileset.directional_pushers_on_goal) {
      save(tile, directional_pusher_path(direction, o, "pog"));
    }

    if (tileset.directional_walls.size() > 0)
      fs::create_directories(directional_walls);
    for (const auto &dirwall : tileset.directional_walls) {
      save(dirwall.second, directional_wall_path(dirwall.first, o));
    }

    if(
      tileset.animated_pusher.size() > 0
      || tileset.animated_pusher_on_goal.size() > 0
      || tileset.animated_box.size() > 0
      || tileset.animated_box_on_goal.size() > 0
    ) {
      fs::create_directories(animations);
    }

    int i = 0;
    for (const Image &tile : tileset.animated_pusher) {
      save(tile, animation_path(o, "pusher", i));
      i++;
    }
    i = 0;
    for (const Image &tile : tileset.animated_pusher_on_goal) {
      save(tile, animation_path(o, "pusher_on_goal", i));
      i++;
    }
    i = 0;
    for (const Image &tile : tileset.animated_box) {
      save(tile, animation_path(o, "box", i));
      i++;
    }
    i = 0;
    for (const Image &tile : tileset.animated_box_on_goal) {
      save(tile, animation_path(o, "box_on_goal", i));
      i++;
    }
  }

  for (size_t r = 0; r < m_impl->m_original_tiles.size(); r++) {
    for (size_t c = 0; c < m_impl->m_original_tiles[r].size(); c++) {
      save(m_impl->m_original_tiles[r][c], src_tile_path(r, c));
    }
  }
}

} // namespace skins
} // namespace sokoengine
