#ifndef SKIN_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define SKIN_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "direction.hpp"
#include "game_config.hpp"
#include "tessellation.hpp"
#include "tile_shape.hpp"

namespace sokoengine {

namespace io {
class Puzzle;
} // namespace io

namespace game {
class BoardGraph;
} // namespace game

///
/// Working with board skin images.
///
namespace skins {

class Image;

///
/// Game board skin image in "Common skin format".
///
/// "Common skin format" is convention on how individual tiles are placed in skin image.
///
/// | tessellation | common skin format                   | skin image example      |
/// | ------------ | ------------------------------------ | ----------------------- |
/// | Sokoban      | ![](sokoban_common_skins_format.png) | ![](sokoban_skin.png)   |
///
/// Skin tries to guess individual tile dimensions and position from whole image width
/// and height. This guesswork requires that all tiles in image are squares. The only
/// exception for this rule are some older 4x4 Sokoban skins that are allowed to have
/// rectangular tiles:
///
/// | Sokoban rectangular skin  |
/// | ------------------------- |
/// | ![](rectangular_skin.png) |
///
/// There is no similar "standard" for other tessellations (Hexoban, Trioban, ...) so
/// libsokoengine implements it's own.
///
/// Bounding box of regular hexagon and equilateral triangle is not square.
/// libsokoengine still requires that individual tiles are square. Actual tile images
/// should then be aligned to bottom left of each square tile:
///
/// | tessellation | common skin format                   | skin image example      |
/// | ------------ | ------------------------------------ | ----------------------- |
/// | Hexoban      | ![](hexoban_common_skins_format.png) | ![](hexoban_skin.png)   |
/// | Trioban      | ![](trioban_common_skins_format.png) | ![](trioban_skin.png)   |
///
/// - regular triangles in Trioban skins must be aligned to bottom of bounding tile
///   square and width of triangle must be width of bounding square tile.
/// - regular hexagons in Hexoban skins must be aligned to left of bounding tile
///   square and height of hexagon must be height of bounding square.
/// - grid in below images is for illustration purposes only, and should not be present
///   in final skin image
/// - last pixel in image is grid pixel and image for ie. Hexoban is of width
///   300px. This is intentional. In final image, although the grid is not visible, we
///   still want whole image to be 300px wide (like there was a grid in image). Common
///   mistake is to remove grid before exporting skin design into skin image and then
///   end up with image that is 299px wide. That image fails Skin tile processing.
///   Same reasoning can be applied to Trioban image top row.
///   When making skins for these 2 variants in ie. InkScape, it is best to include the
///   grid object in .png export, but set opacity of grid stroke to zero. That way, grid
///   pixels will be preserved but transparent in final .png image.
///
/// @see
/// <a href="YASC_Skin_Tutorial_1_02.pdf" target="_blank">YASC skin tutorial</a>
///
class LIBSOKOENGINE_API Skin {
public:
  typedef std::vector<std::vector<Image>> tiles_t;
  typedef std::vector<Image>              animation_frames_t;
  typedef std::pair<double, double>       point_t;
  typedef std::vector<point_t>            polygon_t;
  typedef std::set<directions_t>          directional_walls_directions_t;
  typedef std::set<Direction>             directional_pusher_directions_t;

  ///
  /// Loads skin image from file.
  ///
  /// Expects skin to be in "Common skins format.". Supports only BMP and PNG files.
  ///
  /// Guesses number of tile rows and columns. To override this guesswork, use @a
  /// rows_count_hint and/or @a columns_count_hint.
  ///
  /// @throws std::invalid_argument if @a path can't be loaded for any reason:
  ///   - file doesn't exist / can't be read
  ///   - file doesn't contain correct image format (only PNG and BMP are supported)
  ///   -...
  ///
  Skin(
    Tessellation       tessellation,
    const std::string &path,
    uint8_t            rows_count_hint    = 0,
    uint8_t            columns_count_hint = 0
  );

  ///
  /// Loads skin image from input stream.
  ///
  /// Expects skin to be in "Common skins format.". Supports only BMP and PNG files.
  ///
  /// Guesses number of tile rows and columns. To override this guesswork, use @a
  /// rows_count_hint and/or @a columns_count_hint.
  ///
  /// @throws std::invalid_argument if @a path can't be loaded for any reason:
  ///   - file doesn't exist / can't be read
  ///   - file doesn't contain correct image format (only PNG and BMP are supported)
  ///   -...
  ///
  Skin(
    Tessellation  tessellation,
    std::istream &src,
    ImageFormats  format             = ImageFormats::PNG,
    uint8_t       rows_count_hint    = 0,
    uint8_t       columns_count_hint = 0
  );

  Skin(const Skin &);
  Skin &operator=(const Skin &);
  Skin(Skin &&);
  Skin &operator=(Skin &&);
  ~Skin();

  ///
  /// Creates copy of this skin without image data.
  ///
  /// This is useful in scenarios where image data had been converted into client's own
  /// image representation and instance of Skin is needed only for calculating tile
  /// positions and polygons. In that situation, creating a stripped copy saves memory
  /// but retains other useful capabilities (querying for ie. tile_position or
  /// tile_polygon).
  ///
  /// @warning Since stripped copy no longer contains images, querying it for image data
  /// (calling ie. `skin.box_on_goal(TileShape::DEFAULT))` will throw.
  ///
  std::unique_ptr<Skin> stripped_copy() const;

  ///
  /// Empty skin doesn't have any image data but is able to give correct info on tile
  /// sizes, tile shapes and tile polygons.
  ///
  bool is_empty() const;

  ///
  /// Source file path, if known when Skin was constructed.
  ///
  const std::string &path() const;

  ///
  /// Source image width.
  ///
  uint32_t img_width() const;

  ///
  /// Source image height.
  ///
  uint32_t img_height() const;

  ///
  /// Calculated number of tile rows in source image.
  ///
  uint16_t rows_count() const;

  ///
  /// Calculated number of tile columns in source image.
  ///
  uint16_t columns_count() const;

  ///
  /// Width of each original, unprocessed tile in source image.
  ///
  uint16_t original_tile_width() const;

  ///
  /// Height of each original, unprocessed tile in source image.
  ///
  uint16_t original_tile_height() const;

  ///
  /// Original, unprocessed tile images extracted from source image.
  ///
  const tiles_t &tiles() const;

  ///
  /// Width of each processed and cropped tile image.
  ///
  ///   tile_width <= original_tile_width
  ///
  uint16_t tile_width() const;

  ///
  /// Height of each processed and cropped tile image.
  ///
  ///   tile_height <= original_tile_height
  ///
  uint16_t tile_height() const;

  ///
  /// polygon_t for this skin and tile shape.
  ///
  /// - bounding box is `tile_width() x tile_height()`.
  /// - it is closed: `polygon.front() == polygon.back()`.
  ///
  /// This polygon precisely traces tile shape for given Tessellation and
  /// TileShape. For example, in Trioban tessellation with `shape ==
  /// TileShape::TRIANGLE_DOWN` this method will return polygon with 4 points
  /// defining equilateral triangle where side length is equal to tile_width().
  ///
  polygon_t tile_polygon(TileShape shape) const;

  ///
  /// Position of top left corner of (processed and cropped) tile image for purposes of
  /// tile placement in rendered board scene.
  ///
  point_t tile_position(
    position_t board_position, board_size_t width, board_size_t height
  ) const;

  ///
  /// All TileShape for tessellation of this Skin.
  ///
  tile_shapes_t tile_shapes() const;

  ///
  /// Cropped and processed tile image for board floor.
  ///
  const Image &floor(TileShape shape) const;

  ///
  /// Cropped and processed tile image for board floor in non-playable area of board.
  ///
  const Image &non_playable_floor(TileShape shape) const;

  ///
  /// Cropped and processed tile image for goal.
  ///
  const Image &goal(TileShape shape) const;

  ///
  /// Cropped and processed tile image for non-directional pusher (on floor).
  ///
  const Image &pusher(TileShape shape) const;

  ///
  /// Tries to find image for pusher looking at given direction.
  ///
  /// If there is no such image, returns regular pusher image.
  ///
  const Image &pusher(Direction looking_at, TileShape shape) const;

  ///
  /// Cropped and processed tile image for non-directional pusher on goal.
  ///
  const Image &pusher_on_goal(TileShape shape) const;

  ///
  /// Tries to find image for pusher looking at given direction.
  ///
  /// If there is no such image, returns regular pusher on goal image.
  ///
  const Image &pusher_on_goal(Direction looking_at, TileShape shape) const;

  ///
  /// Cropped and processed tile image for box (on floor).
  ///
  const Image &box(TileShape shape) const;

  ///
  /// Cropped and processed tile image for box on goal.
  ///
  const Image &box_on_goal(TileShape shape) const;

  ///
  /// Cropped and processed tile image for non-directional wall.
  ///
  const Image &wall(TileShape shape) const;

  ///
  /// Tries to find directional wall that has neighbors in all directions specified by
  /// `neighbor_walls`. If there is no such directional wall, returns non directional
  /// wall.
  ///
  const Image &wall(const directions_t &neighbor_walls, TileShape shape) const;

  ///
  /// Cropped and processed tile image for wall cap in skins that use directional
  /// walls.
  ///
  const Image &wall_cap(TileShape shape) const;

  ///
  /// All directions for which this skin has directional pusher image.
  ///
  const directional_pusher_directions_t directional_pushers(TileShape shape) const;

  ///
  /// All directions for which this skin has directional pusher on goal image.
  ///
  const directional_pusher_directions_t directional_pushers_on_goal(TileShape shape
  ) const;

  ///
  /// All directions combinations for which this skin has directional wall image.
  /// Each image represents wall having neighbor walls in given directions_t.
  ///
  const directional_walls_directions_t directional_walls(TileShape shape) const;

  ///
  /// Animated pusher tiles.
  ///
  const animation_frames_t &animated_pusher(TileShape shape) const;

  ///
  /// Animated pusher on goal tiles.
  ///
  const animation_frames_t &animated_pusher_on_goal(TileShape shape) const;

  ///
  /// Animated box tiles.
  ///
  const animation_frames_t &animated_box(TileShape shape) const;

  ///
  /// Animated box on goal tiles.
  ///
  const animation_frames_t &animated_box_on_goal(TileShape shape) const;

  ///
  /// Saves all, original and processed, tiles into `dir`.
  /// For debugging purposes.
  ///
  void dump_tiles(const std::string &dir) const;

  ///
  /// Renders image of board using skin tiles.
  ///
  Image render_board(const io::Puzzle &puzzle) const;

  ///
  /// Renders image of board using skin tiles.
  ///
  Image render_board(const game::BoardGraph &board) const;

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;

  Skin(Tessellation tessellation);
};

} // namespace skins

using skins::Skin;

} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
