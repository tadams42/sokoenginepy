#include "skin.hpp"

#include "board_cell.hpp"
#include "board_graph.hpp"
#include "common_skins_format.hpp"
#include "image.hpp"
#include "puzzle.hpp"
#include "tessellation_impl.hpp"

#include <boost/algorithm/string.hpp>

using sokoengine::implementation::bounding_rect;
using sokoengine::implementation::CommonSkinsFormat;
using sokoengine::implementation::ImageImpl;
using sokoengine::implementation::TessellationImpl;
using sokoengine::implementation::tile_map_t;
using std::istream;
using std::map;
using std::string;
using std::unique_ptr;
using std::vector;

namespace fs = std::filesystem;

namespace sokoengine {
namespace skins {

typedef std::map<Direction, Image>    directional_pushers_t;
typedef std::map<directions_t, Image> directional_walls_t;

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

  directional_pushers_t directional_pushers;
  directional_pushers_t directional_pushers_on_goal;
  directional_walls_t   directional_walls;

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

  tiles_t                                         m_original_tiles;
  Image                                           m_empty_image;
  map<CellOrientation, tileset_t>                 m_tilesets;
  map<CellOrientation, implementation::polygon_t> m_polygons;

  PIMPL(
    Tessellation  tessellation,
    const string &path,
    uint16_t      rows_count_hint,
    uint16_t      columns_count_hint
  )
    : PIMPL(tessellation, ImageImpl::load(path), rows_count_hint, columns_count_hint) {
    m_path = path;
  }

  PIMPL(
    Tessellation tessellation,
    istream     &src,
    ImageFormats format,
    uint8_t      rows_count_hint,
    uint8_t      columns_count_hint
  )
    : PIMPL(
      tessellation, ImageImpl::load(src, format), rows_count_hint, columns_count_hint
    ) {}

  PIMPL(
    Tessellation tessellation,
    uint32_t     image_width,
    uint32_t     image_height,
    uint8_t      rows_count_hint,
    uint8_t      columns_count_hint
  )
    : m_tessellation(tessellation)
    , m_format(
        CommonSkinsFormat::instance(tessellation, rows_count_hint, columns_count_hint)
      ) {
    m_format->set_image(image_width, image_height);
    const TessellationImpl &tess_obj = TessellationImpl::instance(m_tessellation);
    for (auto orientation : tess_obj.cell_orientations()) {
      m_polygons.try_emplace(orientation, m_format->tile_polygon(orientation));
    }
  }

  PIMPL(const PIMPL &rv)
    : m_tessellation(rv.m_tessellation)
    , m_format(rv.m_format->clone())
    , m_path(rv.m_path)
    , m_original_tiles(rv.m_original_tiles)
    , m_tilesets(rv.m_tilesets)
    , m_polygons(rv.m_polygons) {}

  PIMPL &operator=(const PIMPL &rv) {
    if (this != &rv) {
      m_tessellation   = rv.m_tessellation;
      m_format         = rv.m_format->clone();
      m_path           = rv.m_path;
      m_original_tiles = rv.m_original_tiles;
      m_polygons       = rv.m_polygons;
      m_tilesets       = rv.m_tilesets;
    }
    return *this;
  }

  PIMPL(PIMPL &&)            = default;
  PIMPL &operator=(PIMPL &&) = default;
  ~PIMPL()                   = default;

private:
  PIMPL(
    Tessellation     tessellation,
    const ImageImpl &from,
    uint8_t          rows_count_hint,
    uint8_t          columns_count_hint
  )
    : m_tessellation(tessellation)
    , m_format(
        CommonSkinsFormat::instance(tessellation, rows_count_hint, columns_count_hint)
      ) {
    m_format->set_image(from.width(), from.height());

    auto rows_c = m_format->rows_count();
    auto cols_c = m_format->columns_count();

    ImageImpl::tiles_t raw_tiles = from.slice(cols_c, rows_c);

    const TessellationImpl &tess_obj = TessellationImpl::instance(m_tessellation);
    for (auto orientation : tess_obj.cell_orientations()) {
      m_polygons.try_emplace(orientation, m_format->tile_polygon(orientation));
    }

    auto tile_maps = m_format->categorize_tiles(raw_tiles);

    for (const auto &[orientation, tile_map] : tile_maps) {
      m_tilesets.try_emplace(orientation);

      const implementation::polygon_t &polygon      = m_polygons.at(orientation);
      tileset_t                       &dest_tileset = m_tilesets.at(orientation);

      apply_tileset(raw_tiles, tile_maps.at(orientation), dest_tileset, polygon);
    }

    m_original_tiles = tiles_t(rows_c, vector<Image>(cols_c));
    for (size_t row = 0; row < rows_c; ++row) {
      for (size_t column = 0; column < cols_c; ++column) {
        raw_tiles[row][column].swap(m_original_tiles[row][column]);
      }
    }
  }

  static void apply_tileset(
    const ImageImpl::tiles_t       &from,
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
      into.directional_walls.try_emplace(dir_wall.first);
      crop(dir_wall.second, into.directional_walls.at(dir_wall.first));
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
  Tessellation tessellation,
  uint32_t     image_width,
  uint32_t     image_height,
  uint8_t      rows_count_hint,
  uint8_t      columns_count_hint
)
  : m_impl(std::make_unique<PIMPL>(
    tessellation, image_width, image_height, rows_count_hint, columns_count_hint
  )) {}

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

uint32_t Skin::img_width() const { return m_impl->m_format->img_width(); }

uint32_t Skin::img_height() const { return m_impl->m_format->img_height(); }

uint16_t Skin::rows_count() const { return m_impl->m_format->rows_count(); }

uint16_t Skin::columns_count() const { return m_impl->m_format->columns_count(); }

uint16_t Skin::original_tile_width() const { return m_impl->m_format->columns_width(); }

uint16_t Skin::original_tile_height() const { return m_impl->m_format->rows_height(); }

const Skin::tiles_t &Skin::tiles() const { return m_impl->m_original_tiles; }

uint16_t Skin::tile_width() const { return m_impl->m_format->tile_width(); }

uint16_t Skin::tile_height() const { return m_impl->m_format->tile_height(); }

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
  auto p = m_impl->m_format->tile_position(board_position, width, height);
  return std::make_pair(p.x(), p.y());
}

bool Skin::is_empty() const {
  return m_impl->m_original_tiles.size() == 0 || m_impl->m_tilesets.size() == 0;
}

cell_orientations_t Skin::cell_orientations() const {
  return TessellationImpl::instance(m_impl->m_tessellation).cell_orientations();
}

const Image &Skin::floor(CellOrientation orientation) const {
  return m_impl->m_tilesets.at(orientation).floor;
}

const Image &Skin::non_playable_floor(CellOrientation orientation) const {
  return m_impl->m_tilesets.at(orientation).non_playable_floor;
}

const Image &Skin::goal(CellOrientation orientation) const {
  return m_impl->m_tilesets.at(orientation).goal;
}

const Image &Skin::pusher(CellOrientation orientation) const {
  return m_impl->m_tilesets.at(orientation).pusher;
}

const Image &Skin::pusher(Direction looking_at, CellOrientation orientation) const {
  const auto &tileset = m_impl->m_tilesets.at(orientation);

  auto found = tileset.directional_pushers.find(looking_at);
  if (found != tileset.directional_pushers.cend()) {
    return tileset.directional_pushers.at(looking_at);
  } else {
    return tileset.pusher;
  }
}

const Image &Skin::pusher_on_goal(CellOrientation orientation) const {
  return m_impl->m_tilesets.at(orientation).pusher_on_goal;
}

const Image &
Skin::pusher_on_goal(Direction looking_at, CellOrientation orientation) const {
  const auto &tileset = m_impl->m_tilesets.at(orientation);

  auto found = tileset.directional_pushers_on_goal.find(looking_at);
  if (found != tileset.directional_pushers_on_goal.cend()) {
    return tileset.directional_pushers_on_goal.at(looking_at);
  } else {
    return tileset.pusher_on_goal;
  }
}

const Image &Skin::box(CellOrientation orientation) const {
  return m_impl->m_tilesets.at(orientation).box;
}

const Image &Skin::box_on_goal(CellOrientation orientation) const {
  return m_impl->m_tilesets.at(orientation).box_on_goal;
}

const Image &Skin::wall(CellOrientation orientation) const {
  return m_impl->m_tilesets.at(orientation).wall;
}

const Image &
Skin::wall(const directions_t &neighbor_walls, CellOrientation orientation) const {
  const auto &tileset = m_impl->m_tilesets.at(orientation);

  for (const auto &[directions, img] : tileset.directional_walls) {
    if (directions == neighbor_walls) {
      return img;
    }
  }

  return tileset.wall;
}

const Image &Skin::wall_cap(CellOrientation orientation) const {
  return m_impl->m_tilesets.at(orientation).wall_cap;
}

const Skin::directional_pusher_directions_t
Skin::directional_pushers(CellOrientation orientation) const {
  directional_pusher_directions_t retv;

  const tileset_t &tileset = m_impl->m_tilesets.at(orientation);

  for (const auto &[direction, img] : tileset.directional_pushers) {
    retv.insert(direction);
  }

  return retv;
}

const Skin::directional_pusher_directions_t
Skin::directional_pushers_on_goal(CellOrientation orientation) const {
  directional_pusher_directions_t retv;

  const tileset_t &tileset = m_impl->m_tilesets.at(orientation);

  for (const auto &[direction, img] : tileset.directional_pushers_on_goal) {
    retv.insert(direction);
  }

  return retv;
}

const Skin::directional_walls_directions_t
Skin::directional_walls(CellOrientation orientation) const {
  directional_walls_directions_t retv;

  const tileset_t &tileset = m_impl->m_tilesets.at(orientation);

  for (const auto &[directions, img] : tileset.directional_walls) {
    retv.insert(directions);
  }

  return retv;
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

  auto directional_wall_path = [&](const directions_t &dirs, CellOrientation co) {
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

  for (const auto &[o, tileset] : m_impl->m_tilesets) {
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

    for (const auto &[directions, img] : tileset.directional_walls) {
      save(img, directional_wall_path(directions, o));
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

Image Skin::render_board(const io::Puzzle &puzzle) const {
  BoardGraph g(puzzle);
  return render_board(g);
}

Image Skin::render_board(const game::BoardGraph &board) const {
  uint16_t w = static_cast<uint16_t>(board.board_width());
  uint16_t h = static_cast<uint16_t>(board.board_height());

  auto      canvas_size = m_impl->m_format->canvas_size(w, h);
  ImageImpl retv(canvas_size.x(), canvas_size.y(), pixel_t(255, 255, 255));

  const_cast<BoardGraph &>(board).mark_play_area();

  for (size_t row = 0; row < h; ++row) {
    for (size_t col = 0; col < w; ++col) {
      position_t pos    = index_1d(col, row, w);
      point_t    corner = tile_position(pos, w, h);

      CellOrientation  orientation = board.cell_orientation(pos);
      const BoardCell &cell        = board[pos];
      const Image     *selected    = nullptr;

      implementation::point_t top_left(corner.first, corner.second);

      if (cell.is_wall()) {
        selected = &wall(board.wall_neighbor_directions(pos), orientation);
      } else if (!cell.is_in_playable_area()) {
        selected = &non_playable_floor(orientation);
      } else if (cell.has_goal()) {
        selected = &goal(orientation);
      } else {
        selected = &floor(orientation);
      }
      retv.overlay(*selected, top_left);
      selected = nullptr;

      if (cell.has_box() && cell.has_goal()) {
        selected = &box_on_goal(orientation);
      } else if (cell.has_pusher() && cell.has_goal()) {
        selected = &pusher_on_goal(orientation);
      } else if (cell.has_pusher()) {
        selected = &pusher(orientation);
      } else if (cell.has_box()) {
        selected = &box(orientation);
      }
      if (selected)
        retv.overlay(*selected, top_left);
    }
  }

  Image img;
  retv.swap(img);
  return img;
}

} // namespace skins
} // namespace sokoengine
