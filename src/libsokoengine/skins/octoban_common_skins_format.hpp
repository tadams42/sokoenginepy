#ifndef OCTOBAN_COMMON_SKINS_FORMAT_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define OCTOBAN_COMMON_SKINS_FORMAT_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "common_skins_format.hpp"

namespace sokoengine {
namespace implementation {

class LIBSOKOENGINE_LOCAL OctobanCommonSkinsFormat : public CommonSkinsFormat {
public:
  OctobanCommonSkinsFormat(uint8_t rows_count_hint, uint8_t columns_count_hint);
  OctobanCommonSkinsFormat(OctobanCommonSkinsFormat &)            = delete;
  OctobanCommonSkinsFormat &operator=(OctobanCommonSkinsFormat &) = delete;
  virtual ~OctobanCommonSkinsFormat();

  virtual std::unique_ptr<CommonSkinsFormat> clone() const override;

  virtual tile_maps_t categorize_tiles(const ImageImpl::tiles_t &src) const override;
  virtual polygon_t   tile_polygon(TileShape shape) const override;
  virtual pointf_t    tile_position(
       position_t board_position, board_size_t width, board_size_t height
     ) const override;
};

} // namespace implementation
} // namespace sokoengine

#endif // HEADER_GUARD
