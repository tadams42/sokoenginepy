#ifndef SOKOENGINE_CONFIG_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define SOKOENGINE_CONFIG_0FEA723A_C86F_6753_04ABD475F6FCA5FB

// #############################################################################
//                    Macros for symbols exporting
//                  https://gcc.gnu.org/wiki/Visibility
// #############################################################################
// clang-format off

// Generic helper definitions for shared library support
#if defined _WIN32 || defined __CYGWIN__
  #define LIBSOKOENGINE_HELPER_DLL_IMPORT __declspec(dllimport)
  #define LIBSOKOENGINE_HELPER_DLL_EXPORT __declspec(dllexport)
  #define LIBSOKOENGINE_HELPER_DLL_LOCAL
#else
  #if __GNUC__ >= 4 || defined __clang__
    #define LIBSOKOENGINE_HELPER_DLL_IMPORT __attribute__((visibility("default")))
    #define LIBSOKOENGINE_HELPER_DLL_EXPORT __attribute__((visibility("default")))
    #define LIBSOKOENGINE_HELPER_DLL_LOCAL  __attribute__((visibility("hidden")))
  #else
    #define LIBSOKOENGINE_HELPER_DLL_IMPORT
    #define LIBSOKOENGINE_HELPER_DLL_EXPORT
    #define LIBSOKOENGINE_HELPER_DLL_LOCAL
  #endif
#endif

// Now we use the generic helper definitions above to define LIBSOKOENGINE_API and
// LIBSOKOENGINE_LOCAL. LIBSOKOENGINE_API is used for the public API symbols. It either
// DLL imports or DLL exports (or does nothing for static build) LIBSOKOENGINE_LOCAL is
// used for non-api symbols.

#ifdef LIBSOKOENGINE_DLL         // defined if LIBSOKOENGINE is compiled as a DLL
  #ifdef LIBSOKOENGINE_DLL_EXPORTS // libsokoengine shared library is being built
    #define LIBSOKOENGINE_API LIBSOKOENGINE_HELPER_DLL_EXPORT
  #else // libsokoengine shared library is being used
    #define LIBSOKOENGINE_API LIBSOKOENGINE_HELPER_DLL_IMPORT
  #endif
  #define LIBSOKOENGINE_LOCAL LIBSOKOENGINE_HELPER_DLL_LOCAL
#else // LIBSOKOENGINE_DLL is not defined: this means LIBSOKOENGINE is a static lib.
  #define LIBSOKOENGINE_API
  #define LIBSOKOENGINE_LOCAL
#endif // LIBSOKOENGINE_DLL

// clang-format on

// #############################################################################
//                      typedefs and global constants
// #############################################################################

#include <cstdint>
#include <limits>
#include <string>
#include <vector>

///
/// Top namespace for libsokoengine
///
namespace sokoengine {

///
/// Board size type
///
typedef uint32_t board_size_t;

///
/// Board position type.
///
typedef uint32_t position_t;

///
/// Namespace for game engine part of sokoengine
///
namespace game {

///
/// Supported game tessellations.
///
enum class LIBSOKOENGINE_API Tessellation : uint8_t {
  ///
  /// @sa SokobanTessellation
  ///
  SOKOBAN = 0,
  ///
  /// @sa HexobanTessellation
  ///
  HEXOBAN,
  ///
  /// @sa TriobanTessellation
  ///
  TRIOBAN,
  ///
  /// @sa OctobanTessellation
  ///
  OCTOBAN
};

///
/// Converts 2D board position to 1D board position
///
constexpr position_t index_1d(position_t x, position_t y, board_size_t width) {
  return y * width + x;
}

///
/// Calculates x-axis position from 1D board position
///
constexpr position_t index_x(position_t index, board_size_t width) {
  return width == 0 ? 0 : index % width;
}

///
/// Calculates y-axis position from 1D board position
///
constexpr position_t index_y(position_t index, board_size_t width) {
  return width == 0 ? 0 : index / width;
}

///
/// Alias for index_y()
///
constexpr position_t index_row(position_t index, board_size_t width) {
  return index_y(index, width);
}

///
/// Alias for index_x()
///
constexpr position_t index_column(position_t index, board_size_t width) {
  return index_x(index, width);
}

///
/// Is position on given board?
///
constexpr bool
is_on_board_2d(position_t x, position_t y, board_size_t width, board_size_t height) {
  return x < width && y < height;
}

///
/// Is position on given board?
///
constexpr bool is_on_board_1d(position_t pos, board_size_t width, board_size_t height) {
  return is_on_board_2d(index_x(pos, width), index_y(pos, width), width, height);
}

///
/// Ordered collection of board positions usually describing continuous board
/// path.
///
typedef std::vector<position_t> Positions;

///
/// Piece ID and Sokoban+ ID type.
///
typedef uint16_t piece_id_t;

///
/// Zobrist hash type
///
typedef uint64_t zobrist_key_t;

///
/// Movement directions.
///
enum class LIBSOKOENGINE_API Direction : uint8_t {
  UP = 0,
  NORTH_EAST,
  RIGHT,
  SOUTH_EAST,
  DOWN,
  SOUTH_WEST,
  LEFT,
  NORTH_WEST
};

///
/// Ordered collection of Directions usually describing continuous board path.
///
typedef std::vector<Direction> Directions;

///
/// Packs Direction into 8-bit integer.
///
constexpr uint8_t direction_pack(const Direction &direction) {
  return static_cast<uint8_t>(direction);
}

///
/// Number of available Direction.
///
static constexpr uint8_t DIRECTIONS_COUNT = direction_pack(Direction::NORTH_WEST) + 1;

///
/// Opposite Direction lookup.
///
static constexpr const Direction DIRECTIONS[DIRECTIONS_COUNT] = {
  Direction::UP,
  Direction::NORTH_EAST,
  Direction::RIGHT,
  Direction::SOUTH_EAST,
  Direction::DOWN,
  Direction::SOUTH_WEST,
  Direction::LEFT,
  Direction::NORTH_WEST};

///
/// Opposite directions lookup
///
static constexpr const Direction OPPOSITE_DIRECTIONS[DIRECTIONS_COUNT] = {
  Direction::DOWN,
  Direction::SOUTH_WEST,
  Direction::LEFT,
  Direction::NORTH_WEST,
  Direction::UP,
  Direction::NORTH_EAST,
  Direction::RIGHT,
  Direction::SOUTH_EAST};

///
/// Reverse operation from direction_pack().
///
constexpr const Direction &direction_unpack(uint8_t val) { return DIRECTIONS[val]; }

///
/// Opposite Direction lookup.
///
LIBSOKOENGINE_API constexpr Direction opposite(const Direction d) {
  return OPPOSITE_DIRECTIONS[static_cast<uint8_t>(d)];
}

///
/// Types of BoardGraph.
///
enum class LIBSOKOENGINE_API GraphType : int {
  ///
  /// Directed graphs
  ///
  DIRECTED,

  ///
  /// Directed graphs with self loops and parallel edges
  ///
  DIRECTED_MULTI
};

///
/// Various constants used across game namespace. Since they are needed by many
/// modules it made more sense to place them here in their own class, than into one or
/// more other classes.
///
class LIBSOKOENGINE_API Config {
public:
  ///
  /// Max board width.
  ///
  static constexpr board_size_t MAX_WIDTH = 4096;

  ///
  /// Max board height.
  ///
  static constexpr board_size_t MAX_HEIGHT = 4096;

  static_assert(
    MAX_WIDTH * MAX_HEIGHT < std::numeric_limits<board_size_t>::max(),
    "MAX_HEIGHT * MAX_HEIGHT must be smaller than maximal representable "
    "board position!"
  );

  ///
  /// Value that represents invalid or unknown board position
  ///
  static constexpr position_t NO_POS = std::numeric_limits<position_t>::max();
  static_assert(
    NO_POS > MAX_WIDTH * MAX_HEIGHT,
    "NO_POS must be greater than any valid board position!"
  );

  ///
  /// Default ID for pieces for situations whe one is needed and **must** be provided.
  ///
  /// @sa
  /// - BoardManager
  /// - PusherStep
  ///
  static constexpr game::piece_id_t DEFAULT_ID = 1;

  ///
  /// Invalid, non-existing ID of a piece.
  ///
  /// @sa
  /// - BoardManager
  /// - PusherStep
  ///
  static constexpr game::piece_id_t NO_ID = 0;
  static_assert(NO_ID < DEFAULT_ID, "NO_ID must be less than DEFAULT_ID");
};
} // namespace game

///
/// Namespace for I/O part of sokoengine
///
namespace io {

///
/// For some types of games, individual board cell type depends on board position.
///
enum class LIBSOKOENGINE_API CellOrientation : int {
  DEFAULT,
  TRIANGLE_DOWN,
  OCTAGON,
};

///
/// Test if line is zero length or contains only spaces.
///
bool LIBSOKOENGINE_API is_blank(const std::string &line);

} // namespace io

namespace implementation {
typedef std::vector<std::string> Strings;
} // namespace implementation

} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
