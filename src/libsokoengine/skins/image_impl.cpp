#include "image_impl.hpp"

#include "image.hpp"

#include <boost/algorithm/string.hpp>
#include <boost/geometry/algorithms/covered_by.hpp>
#include <boost/geometry/algorithms/within.hpp>
#include <boost/geometry/strategies/cartesian/point_in_poly_crossings_multiply.hpp>
#include <boost/geometry/strategies/cartesian/point_in_poly_franklin.hpp>
#include <boost/geometry/strategies/cartesian/point_in_poly_winding.hpp>
#include <boost/geometry/strategies/default_strategy.hpp>
#include <boost/gil/extension/io/bmp.hpp>
#include <boost/gil/extension/io/png.hpp>
#include <boost/gil/image.hpp>
#include <boost/gil/pixel.hpp>
#include <boost/gil/rgba.hpp>
#include <fstream>

using std::ifstream;
using std::ios;
using std::istream;
using std::ofstream;
using std::ostream;
using std::string;
using std::vector;

namespace gil       = boost::gil;
using image_t       = gil::rgba8_image_t;
using rgba8_pixel_t = gil::rgba8_pixel_t;
using gil::get_color;

namespace sokoengine {
namespace implementation {

static constexpr auto red_tag   = gil::red_t();
static constexpr auto green_tag = gil::green_t();
static constexpr auto blue_tag  = gil::blue_t();
static constexpr auto alpha_tag = gil::alpha_t();

class LIBSOKOENGINE_LOCAL ImageImpl::PIMPL {
public:
  image_t m_img;

  PIMPL()
    : PIMPL(0, 0) {}

  PIMPL(uint32_t width, uint32_t height)
    : m_img(width, height) {}

  PIMPL(uint32_t width, uint32_t height, const pixel_t &fill)
    : PIMPL(width, height) {
    auto          view = gil::view(m_img);
    rgba8_pixel_t gil_fill(fill.r, fill.g, fill.b, 255);
    gil::fill_pixels(view, gil_fill);
  }

  PIMPL(const PIMPL &rv)            = default;
  PIMPL &operator=(const PIMPL &rv) = default;
  PIMPL(PIMPL &&rv)                 = default;
  PIMPL &operator=(PIMPL &&rv)      = default;
};

ImageImpl::ImageImpl()
  : ImageImpl(0, 0) {}

ImageImpl::ImageImpl(uint32_t width, uint32_t height)
  : m_impl(std::make_unique<PIMPL>(width, height)) {}

ImageImpl::ImageImpl(uint32_t width, uint32_t height, const pixel_t &fill)
  : m_impl(std::make_unique<PIMPL>(width, height, fill)) {}

void ImageImpl::swap(ImageImpl &img) { m_impl->m_img.swap(img.m_impl->m_img); }

void ImageImpl::swap(Image &img) { swap(*img.m_impl); }

ImageImpl::ImageImpl(const ImageImpl &rv)
  : m_impl(std::make_unique<PIMPL>(*rv.m_impl)) {}

ImageImpl &ImageImpl::operator=(const ImageImpl &rv) {
  if (this != &rv) {
    *m_impl = *rv.m_impl;
  }
  return *this;
}

ImageImpl::ImageImpl(ImageImpl &&rv)            = default;
ImageImpl &ImageImpl::operator=(ImageImpl &&rv) = default;
ImageImpl::~ImageImpl()                         = default;

uint32_t ImageImpl::width() const { return m_impl->m_img.width(); }

uint32_t ImageImpl::height() const { return m_impl->m_img.height(); }

ImageImpl ImageImpl::load(const string &path) {
  bool maybe_png = boost::ends_with(boost::to_lower_copy(path), ".png");
  bool maybe_bmp = boost::ends_with(boost::to_lower_copy(path), ".bmp");

  if (maybe_png) {
    ifstream src(path, ios::binary);
    return load(src, ImageFormats::PNG);
  } else if (maybe_bmp) {
    ifstream src(path, ios::binary);
    return load(src, ImageFormats::BMP);
  } else {
    throw std::invalid_argument("Only supports loading PNG and BMP images!");
  }
}

ImageImpl ImageImpl::load(istream &src, ImageFormats format) {
  if (format != ImageFormats::PNG && format != ImageFormats::BMP) {
    throw std::invalid_argument("Only BMP and PNG format images are supported!");
  }

  ImageImpl retv;

  gil::image_read_settings<gil::png_tag> png_settings;
  png_settings._read_transparency_data   = true;
  png_settings._read_background          = true;
  png_settings._read_physical_resolution = true;

  gil::image_read_settings<gil::bmp_tag> bmp_settings;

  retv.m_impl->m_img = image_t();

  try {
    switch (format) {
      case ImageFormats::PNG:
        gil::read_and_convert_image(src, retv.m_impl->m_img, png_settings);
        break;
      case ImageFormats::BMP:
      default:
        gil::read_and_convert_image(src, retv.m_impl->m_img, bmp_settings);
        break;
    }
  } catch (ios::failure &e) {
    throw std::invalid_argument(
      string("Failed loading image. Check file permissions and also note that ")
      + "only PNG and BMP images are supported. (" + e.what() + ")"
    );
  }

  return retv;
}

void ImageImpl::save(const string &path) const {
  ofstream dest(path, ios::binary);
  save(dest);
}

void ImageImpl::save(ostream &dest) const {
  gil::write_view(dest, gil::const_view(m_impl->m_img), gil::png_tag{});
}

ImageImpl::tiles_t ImageImpl::slice(uint16_t columns_count, uint16_t rows_count) const {
  tiles_t retv(rows_count, vector<ImageImpl>(columns_count));

  size_t columns_width = m_impl->m_img.width() / columns_count;
  size_t rows_height   = m_impl->m_img.height() / rows_count;

  for (size_t row = 0; row < rows_count; ++row) {
    vector<ImageImpl> &row_data = retv[row];

    for (size_t column = 0; column < columns_count; ++column) {
      implementation::rect_t tile_rect(
        column * columns_width, row * rows_height, columns_width, rows_height
      );
      row_data[column] = subimage(tile_rect);
    }
  }

  return retv;
}

ImageImpl ImageImpl::subimage(const rect_t &rect) const {
  ImageImpl retv(rect.width(), rect.height());

  gil::copy_pixels(
    gil::subimage_view(
      gil::const_view(m_impl->m_img),
      rect.top_left().x(),
      rect.top_left().y(),
      rect.width(),
      rect.height()
    ),
    gil::view(retv.m_impl->m_img)
  );

  return retv;
}

void ImageImpl::replace(const ImageImpl &src, const rect_t &where) {
  gil::copy_pixels(
    gil::subimage_view(
      gil::const_view(src.m_impl->m_img),
      where.top_left().x(),
      where.top_left().y(),
      where.width(),
      where.height()
    ),
    gil::subimage_view(
      gil::view(m_impl->m_img),
      where.top_left().x(),
      where.top_left().y(),
      where.width(),
      where.height()
    )
  );
}

void ImageImpl::grayscale() {
  gil::transform_pixels(
    gil::view(m_impl->m_img),
    gil::view(m_impl->m_img),
    [](rgba8_pixel_t &pix) {
      uint8_t val =
        (get_color(pix, red_tag) + get_color(pix, blue_tag) + get_color(pix, green_tag))
        / 3;
      return rgba8_pixel_t(val, val, val, get_color(pix, alpha_tag));
    }
  );
}

void ImageImpl::subtract(const ImageImpl &bottom) {
  auto top_v    = gil::view(m_impl->m_img);
  auto bottom_v = gil::const_view(bottom.m_impl->m_img);

  if (bottom_v.width() != top_v.width() || bottom_v.height() != top_v.height()) {
    throw std::invalid_argument(
      "Subtracting images works only for images with same dimensions!"
    );
  }

  // auto non_fuzzy_eq = [](const rgba8_pixel_t &lv, const rgba8_pixel_t &rv, uint32_t
  // delta)
  // {
  //   return (get_color(lv, red_tag) == get_color(rv, red_tag))
  //       && (get_color(lv, blue_tag) == get_color(rv, blue_tag))
  //       && (get_color(lv, green_tag) == get_color(rv, green_tag));
  // };

  auto fuzzy_eq = [](const rgba8_pixel_t &lv, const rgba8_pixel_t &rv, uint32_t delta) {
    auto component_in_range = [&](uint32_t s, uint32_t d) {
      uint32_t low = d > delta ? d - delta : 0;
      uint32_t hi  = d + delta >= 255 ? 255 : d + delta;
      return s >= low && s <= hi;
    };

    return component_in_range(get_color(lv, red_tag), get_color(rv, red_tag))
        && component_in_range(get_color(lv, blue_tag), get_color(rv, blue_tag))
        && component_in_range(get_color(lv, green_tag), get_color(rv, green_tag));
  };

  auto w = bottom.width();
  auto h = bottom.height();

  // auto eq = non_fuzzy_eq;
  auto eq = fuzzy_eq;

  for (uint32_t y = 0; y < h; ++y) {
    boost::gil::rgba8_ptr_t  top_it    = top_v.row_begin(y);
    boost::gil::rgba8c_ptr_t bottom_it = bottom_v.row_begin(y);

    for (uint32_t x = 0; x < w; ++x) {
      rgba8_pixel_t       &p1 = top_it[x];
      const rgba8_pixel_t &p2 = bottom_it[x];

      if (eq(p1, p2, 3)) {
        p1 = rgba8_pixel_t(0, 0, 0, 0);
      }
    }
  }
}

void ImageImpl::crop_to_bounding_box(const polygon_t &p) {
  rect_t box = bounding_rect(p).to_aligned_rect();

  point_t offset(0, 0);
  if (m_impl->m_img.height() > box.height()) {
    offset.y(m_impl->m_img.height() - box.height());
  }
  box = box.translated(offset.x(), offset.y());

  image_t result(box.width(), box.height());

  gil::copy_pixels(
    gil::subimage_view(
      gil::const_view(m_impl->m_img),
      box.top_left().x(),
      box.top_left().y(),
      box.width(),
      box.height()
    ),
    gil::view(result)
  );

  m_impl->m_img.swap(result);
}

void ImageImpl::set_outer_pixels_transparent(const polygon_t &polygon) {
  auto img_v = gil::view(m_impl->m_img);
  auto w     = img_v.width();
  auto h     = img_v.height();

  // auto strategy = boost::geometry::default_strategy();
  // auto strategy = boost::geometry::strategy::covered_by::cartesian_box_box();
  // auto strategy =
  // boost::geometry::strategy::covered_by::cartesian_point_box_by_side();

  // auto strategy =
  //   boost::geometry::strategy::within::franklin<point_t, polygon_t, uint64_t>();
  // auto strategy = boost::geometry::strategy::within::crossings_multiply<point_t,
  // polygon_t, uint32_t>();
  // auto strategy = boost::geometry::strategy::within::cartesian_point_box();

  for (uint32_t y = 0; y < h; ++y) {
    boost::gil::rgba8_ptr_t it = img_v.row_begin(y);
    for (uint32_t x = 0; x < w; ++x) {
      if (!boost::geometry::covered_by(pointf_t(x, y), polygon)) {
        get_color(it[x], alpha_tag) = 0;
      }
    }
  }
}

pixel_t ImageImpl::pixel(uint32_t x, uint32_t y) const {
  rgba8_pixel_t pixel = *(gil::const_view(m_impl->m_img).at(x, y));
  return pixel_t(
    get_color(pixel, red_tag),
    get_color(pixel, green_tag),
    get_color(pixel, blue_tag),
    get_color(pixel, alpha_tag)
  );
}

void ImageImpl::copy(const ImageImpl &src, const point_t &top_left) {
  gil::copy_pixels(
    gil::const_view(src.m_impl->m_img),
    gil::subimage_view(
      gil::view(m_impl->m_img), top_left.x(), top_left.y(), src.width(), src.height()
    )
  );
}

void ImageImpl::copy(const Image &src, const point_t &top_left) {
  copy(*src.m_impl, top_left);
}

void ImageImpl::overlay(const ImageImpl &src, const point_t &top_left) {
  auto top_v    = gil::const_view(src.m_impl->m_img);
  auto bottom_v = gil::subimage_view(
    gil::view(m_impl->m_img), top_left.x(), top_left.y(), src.width(), src.height()
  );

  auto w = src.m_impl->m_img.width();
  auto h = src.m_impl->m_img.height();

  for (int y = 0; y < h; ++y) {
    boost::gil::rgba8c_ptr_t top_it    = top_v.row_begin(y);
    boost::gil::rgba8_ptr_t  bottom_it = bottom_v.row_begin(y);

    for (int x = 0; x < w; ++x) {
      // should actually be multiplied, but this is good enough for our needs
      if (get_color(top_it[x], alpha_tag) == 255)
        bottom_it[x] = top_it[x];
    }
  }
}

void ImageImpl::overlay(const Image &src, const point_t &top_left) {
  overlay(*src.m_impl, top_left);
}

} // namespace implementation
} // namespace sokoengine
