#ifndef SKIN_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define SKIN_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "cell_orientation.hpp"
#include "direction.hpp"
#include "game_config.hpp"
#include "tessellation.hpp"

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
  typedef std::vector<std::vector<Image>> tiles_matrix_t;
  typedef std::map<Direction, Image>      directional_pushers_t;
  typedef std::pair<Directions, Image>    directional_wall_t;
  typedef std::vector<directional_wall_t> directional_walls_t;
  typedef std::vector<Image>              animation_frames_t;
  typedef std::pair<double, double>       point_t;
  typedef std::vector<point_t>            polygon_t;

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

  ///
  /// Constructs empty skin.
  ///
  /// Empty skin doesn't have any image data but is able to give correct info on tile
  /// sizes, cell orientations and tile polygons.
  ///
  Skin(
    Tessellation tessellation,
    uint16_t     original_tile_width,
    uint16_t     original_tile_height
  );

  Skin(const Skin &);
  Skin &operator=(const Skin &);
  Skin(Skin &&);
  Skin &operator=(Skin &&);
  ~Skin();

  ///
  /// Source file path.
  ///
  const std::string &path() const;

  ///
  /// Number of tile rows in image.
  ///
  uint16_t rows_count() const;

  ///
  /// Number of tile columns in image.
  ///
  uint16_t columns_count() const;

  ///
  /// Size of each original, unprocessed tile image.
  ///
  uint16_t original_tile_width() const;

  ///
  /// Size of each original, unprocessed tile image.
  ///
  uint16_t original_tile_height() const;

  ///
  /// Original, unprocessed tile images extracted from source image.
  ///
  const tiles_matrix_t &tiles() const;

  ///
  /// Size of processed and cropped tile image.
  ///
  /// @note This doesn't have to be equal to original_tile_size() but is same for each
  /// processed tile (ie. floor(), pusher(), box()...).
  ///
  uint16_t tile_width() const;

  ///
  /// Size of processed and cropped tile image.
  ///
  /// @note This doesn't have to be equal to original_tile_size() but is same for each
  /// processed tile (ie. floor(), pusher(), box()...).
  ///
  uint16_t tile_height() const;

  ///
  /// polygon_t for this skin and cell orientation.
  ///
  /// Bounding box of this polygon is always `tile_width() * tile_height()`.
  ///
  /// polygon_t is always closed: `polygon.front() == polygon.back()`.
  ///
  /// This polygon precisely traces tile shape for given Tessellation and
  /// CellOrientation. For example, in Trioban tessellation with `orientation ==
  /// CellOrientation::TRIANGLE_DOWN` this method will return polygon with 4 points
  /// defining equilateral triangle with side length equal to tile_width().
  ///
  polygon_t tile_polygon(CellOrientation orientation) const;

  ///
  /// Position of top left corner of (processed and cropped) tile image for purposes of
  /// tile placement in rendered board scene.
  ///
  point_t tile_position(
    position_t board_position, board_size_t width, board_size_t height
  ) const;

  ///
  /// All cell orientations for which this skin has tile images.
  ///
  std::vector<CellOrientation> cell_orientations() const;

  ///
  /// Empty skin doesn't have any image data but is able to give correct info on tile
  /// sizes, cell orientations and tile polygons.
  ///
  /// Methods returning tile images will return empty images if skin is empty.
  ///
  bool is_empty() const;

  ///
  /// Cropped and processed tile image for board floor.
  ///
  const Image &floor(CellOrientation orientation) const;

  ///
  /// Cropped and processed tile image for board floor in non-playable area of board.
  ///
  const Image &non_playable_floor(CellOrientation orientation) const;

  ///
  /// Cropped and processed tile image for goal.
  ///
  const Image &goal(CellOrientation orientation) const;

  ///
  /// Cropped and processed tile image for non-directional pusher (on floor).
  ///
  const Image &pusher(CellOrientation orientation) const;

  ///
  /// Tries to find image for pusher looking at given @param looking_at.
  ///
  /// If there is no such image, returns regular pusher image.
  ///
  const Image &pusher(Direction looking_at, CellOrientation orientation) const;

  ///
  /// Cropped and processed tile image for non-directional pusher on goal.
  ///
  const Image &pusher_on_goal(CellOrientation orientation) const;

  ///
  /// Tries to find image for pusher looking at given @param looking_at.
  ///
  /// If there is no such image, returns regular pusher on goal image.
  ///
  const Image &pusher_on_goal(Direction looking_at, CellOrientation orientation) const;

  ///
  /// Cropped and processed tile image for box (on floor).
  ///
  const Image &box(CellOrientation orientation) const;

  ///
  /// Cropped and processed tile image for box on goal.
  ///
  const Image &box_on_goal(CellOrientation orientation) const;

  ///
  /// Cropped and processed tile image for non-directional wall.
  ///
  const Image &wall(CellOrientation orientation) const;

  ///
  /// Tries to find directional wall that has neighbors in all directions specified by
  /// @param neighbor_walls. If there is no such directional wall, returns regular,
  /// non directional wall.
  ///
  const Image &
  wall(const Directions &neighbor_walls, CellOrientation orientation) const;

  ///
  /// Cropped and processed tile image for wall cap in skins that use directional
  /// walls.
  ///
  const Image &wall_cap(CellOrientation orientation) const;

  ///
  /// Cropped and processed tile images for directional pusher.
  /// Each image represents pusher looking in Direction.
  ///
  const directional_pushers_t &directional_pushers(CellOrientation orientation) const;

  ///
  /// Cropped and processed tile images for directional pusher.
  /// Each image represents pusher looking in Direction.
  ///
  const directional_pushers_t &directional_pushers_on_goal(CellOrientation orientation
  ) const;

  ///
  /// Cropped and processed tile image for directional goal.
  /// Each image represents wall having neighbor walls in given Directions.
  ///
  const directional_walls_t &directional_walls(CellOrientation orientation) const;

  ///
  /// Animated pusher tiles.
  ///
  const animation_frames_t &animated_pusher(CellOrientation orientation) const;

  ///
  /// Animated pusher on goal tiles.
  ///
  const animation_frames_t &animated_pusher_on_goal(CellOrientation orientation) const;

  ///
  /// Animated box tiles.
  ///
  const animation_frames_t &animated_box(CellOrientation orientation) const;

  ///
  /// Animated box on goal tiles.
  ///
  const animation_frames_t &animated_box_on_goal(CellOrientation orientation) const;

  ///
  /// Saves all, original and processed, tiles into `dir`.
  /// For debugging purposes.
  ///
  void dump_tiles(const std::string &dir) const;

  Image render_board(const io::Puzzle &puzzle) const;
  Image render_board(const game::BoardGraph &board) const;

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace skins

using skins::Skin;

} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
