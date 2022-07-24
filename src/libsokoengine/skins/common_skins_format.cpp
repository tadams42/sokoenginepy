#include "common_skins_format.hpp"

#include <boost/numeric/conversion/cast.hpp>

#include "hexoban_common_skins_format.hpp"
#include "octoban_common_skins_format.hpp"
#include "sokoban_common_skins_format.hpp"
#include "tessellation.hpp"
#include "trioban_common_skins_format.hpp"

using boost::numeric_cast;
using std::map;

namespace sokoengine {
namespace implementation {

CommonSkinsFormat::CommonSkinsFormat(
  uint8_t rows_count_hint, uint8_t columns_count_hint
)
  : m_rows_count_hint(rows_count_hint)
  , m_cols_count_hint(columns_count_hint) {}

CommonSkinsFormat::~CommonSkinsFormat() = default;

std::unique_ptr<CommonSkinsFormat> CommonSkinsFormat::instance(
  Tessellation tessellation, uint8_t rows_count_hint, uint8_t columns_count_hint
) {
  switch (tessellation) {
    case Tessellation::SOKOBAN:
      return std::make_unique<SokobanCommonSkinsFormat>(
        rows_count_hint, columns_count_hint
      );
      break;
    case Tessellation::HEXOBAN:
      return std::make_unique<HexobanCommonSkinsFormat>(
        rows_count_hint, columns_count_hint
      );
      break;
    case Tessellation::TRIOBAN:
      return std::make_unique<TriobanCommonSkinsFormat>(
        rows_count_hint, columns_count_hint
      );
      break;
    case Tessellation::OCTOBAN:
      return std::make_unique<OctobanCommonSkinsFormat>(
        rows_count_hint, columns_count_hint
      );
      break;
      // Don't use default so we get compiler warning
  };
  throw std::invalid_argument("Unknown tessellation!");
}

point_t CommonSkinsFormat::canvas_size(
  board_size_t board_width, board_size_t board_height
) const {
  return point_t(board_width * m_columns_width, board_height * m_rows_height);
}

uint32_t CommonSkinsFormat::img_width() const { return m_img_width; }

uint32_t CommonSkinsFormat::img_height() const { return m_img_height; }

uint16_t CommonSkinsFormat::columns_width() const { return m_columns_count; }

uint16_t CommonSkinsFormat::rows_height() const { return m_rows_height; }

uint16_t CommonSkinsFormat::tile_width() const { return m_tile_width; }

uint16_t CommonSkinsFormat::tile_height() const { return m_tile_height; }

uint8_t CommonSkinsFormat::rows_count() const { return m_rows_count; }

uint8_t CommonSkinsFormat::columns_count() const { return m_columns_count; }

uint8_t CommonSkinsFormat::rows_count_hint() const { return m_rows_count_hint; }

uint8_t CommonSkinsFormat::columns_count_hint() const { return m_cols_count_hint; }

void CommonSkinsFormat ::set_image(uint32_t img_width_, uint32_t img_height_) {
  m_img_width  = img_width_;
  m_img_height = img_height_;
  guess_tile_sizes();
}

void CommonSkinsFormat::guess_tile_sizes() {
  // The following code is a derivative work of the code from the SokobanYASC project,
  // which is licensed GPLv2. This code therefore is also licensed under the terms of
  // the GNU Public License, version 2.
  //
  // SokobanYASC Copyright by briandamgaard and SokobanYASC contributors under GPLv2.
  // https://sourceforge.net/projects/sokobanyasc/
  // https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html

  // Algorithm implemented here was translated to C++ using implementation from
  // SokobanYASC TSkins.GuessColumnsAndRows

  if (m_img_height == 0 || m_img_width == 0) {
    m_rows_count_hint = 0;
    m_cols_count_hint = 0;
    m_columns_width   = 0;
    m_rows_height     = 0;
    m_tile_width      = 0;
    m_tile_height     = 0;
    m_rows_count      = 0;
    m_columns_count   = 0;
    return;
  }

  long img_width               = numeric_cast<long>(m_img_width);
  long img_height              = numeric_cast<long>(m_img_height);
  long cols_count              = m_cols_count_hint == 0 ? 4 : m_cols_count_hint;
  long rows_count              = m_rows_count_hint == 0 ? 1 : m_rows_count_hint;
  long col_width               = 0;
  long row_height              = 0;
  bool success                 = false;
  long start_col_count         = cols_count;
  long oblonged_tile_col_count = 0;

  while (!success && rows_count <= img_height) {
    while (rows_count <= img_height && img_height % rows_count != 0)
      rows_count += 1;

    row_height = std::div(img_height, rows_count).quot;
    cols_count = start_col_count;

    while (!success && cols_count < img_width) {
      if (img_width % cols_count == 0) {
        if (
          // 'True': a square tile
          std::div(img_width, cols_count).quot == row_height
          && (
            // '<=256': tiles are probably not bigger than 256x256 pixels
            row_height <= 256
            || (
              // check if it looks like a 1-row skin with very large tiles up to 512x512
              rows_count == 1 && cols_count >= 7 && row_height <= 512
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
      img_width % std::div(img_width, (long)4).quot == 0
    )
    && (
      (  img_height % std::div(img_height,  (long)4).quot == 0 )
      || (  img_height % std::div(img_height, (long)6).quot == 0 )
    )
  ) {
    // 'True' : assume the skin has 4 x 4 or 4 x 6 non-square tiles
    cols_count = 4;
    if (img_height % std::div(img_height, (long)4).quot == 0) {
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
  row_height = std::div(img_height, rows_count).quot;

  if (rows_count * row_height != img_height || cols_count * col_width != img_width)
    throw std::invalid_argument(
      "Skin image width and height not divisible by tile width and height!"
    );

  m_columns_width = numeric_cast<uint16_t>(col_width);
  m_rows_height   = numeric_cast<uint16_t>(row_height);
  m_rows_count    = numeric_cast<uint8_t>(rows_count);
  m_columns_count = numeric_cast<uint8_t>(cols_count);

  auto processed_tile =
    bounding_rect(tile_polygon(TileShape::DEFAULT)).to_aligned_rect();
  m_tile_width  = numeric_cast<uint16_t>(processed_tile.width());
  m_tile_height = numeric_cast<uint16_t>(processed_tile.height());
}

} // namespace implementation
} // namespace sokoengine
