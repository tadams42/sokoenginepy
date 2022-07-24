#ifndef GAME_CONFIG_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define GAME_CONFIG_0FEA723A_C86F_6753_04ABD475F6FCA5FB
/// @file

#include "numeric_types.hpp"

namespace sokoengine {

enum class ImageFormats : uint8_t { BMP = 1, PNG = 2 };

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
  static constexpr piece_id_t DEFAULT_ID = 1;

  ///
  /// Invalid, non-existing ID of a piece.
  ///
  /// @sa
  /// - BoardManager
  /// - PusherStep
  ///
  static constexpr piece_id_t NO_ID = 0;
  static_assert(NO_ID < DEFAULT_ID, "NO_ID must be less than DEFAULT_ID");
};

} // namespace sokoengine

#endif // HEADER_GUARD
