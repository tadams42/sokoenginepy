#ifndef SOKOBAN_COMMON_SKINS_FORMAT_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define SOKOBAN_COMMON_SKINS_FORMAT_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "common_skins_format.hpp"

namespace sokoengine {
namespace implementation {

class LIBSOKOENGINE_LOCAL SokobanCommonSkinsFormat : public CommonSkinsFormat {
public:
  SokobanCommonSkinsFormat(uint8_t rows_count_hint, uint8_t columns_count_hint);
  SokobanCommonSkinsFormat(SokobanCommonSkinsFormat &)            = delete;
  SokobanCommonSkinsFormat &operator=(SokobanCommonSkinsFormat &) = delete;
  virtual ~SokobanCommonSkinsFormat();

  virtual std::unique_ptr<CommonSkinsFormat> clone() const override;
  virtual tile_maps_t categorize_tiles(const ImageImpl::tiles_t &src) const override;
  virtual polygon_t   tile_polygon(CellOrientation orientation) const override;
  virtual pointf_t    tile_position(
       position_t board_position, board_size_t width, board_size_t height
     ) const override;

private:
  static void generate_directional_walls(
    tile_map_t      &tile_map,
    const ImageImpl &isolated_wall,
    const ImageImpl &lr_wall,
    const ImageImpl &ud_wall,
    const ImageImpl &lurd_wall
  );
  static rect_t left_half(const ImageImpl &src);
  static rect_t right_half(const ImageImpl &src);
  static rect_t up_half(const ImageImpl &src);
  static rect_t down_half(const ImageImpl &src);
  static rect_t left_top_quarter(const ImageImpl &src);
  static rect_t right_top_quarter(const ImageImpl &src);
  static rect_t left_bottom_quarter(const ImageImpl &src);
  static rect_t right_bottom_quarter(const ImageImpl &src);
};

} // namespace implementation
} // namespace sokoengine

#endif // HEADER_GUARD
