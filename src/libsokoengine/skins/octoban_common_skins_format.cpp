#include "octoban_common_skins_format.hpp"
#include "sokoban_common_skins_format.hpp"

namespace sokoengine {
namespace implementation {

OctobanCommonSkinsFormat::OctobanCommonSkinsFormat(
  uint8_t rows_count_hint, uint8_t columns_count_hint
)
  : CommonSkinsFormat(rows_count_hint, columns_count_hint) {}

OctobanCommonSkinsFormat::~OctobanCommonSkinsFormat() = default;

std::unique_ptr<CommonSkinsFormat> OctobanCommonSkinsFormat::clone() const {
  // TODO
  return SokobanCommonSkinsFormat(m_rows_count_hint, m_cols_count_hint).clone();
}

tile_maps_t OctobanCommonSkinsFormat::categorize_tiles(const ImageImpl::tiles_t &src
) const {
  // TODO
  return SokobanCommonSkinsFormat(m_rows_count_hint, m_cols_count_hint)
    .categorize_tiles(src);
}

polygon_t OctobanCommonSkinsFormat::tile_polygon(TileShape shape) const {
  // TODO
  return SokobanCommonSkinsFormat(m_rows_count_hint, m_cols_count_hint)
    .tile_polygon(shape);
}

pointf_t OctobanCommonSkinsFormat::tile_position(
  position_t board_position, board_size_t width, board_size_t height
) const {
  // TODO
  return SokobanCommonSkinsFormat(m_rows_count_hint, m_cols_count_hint)
    .tile_position(board_position, width, height);
}

} // namespace implementation
} // namespace sokoengine
