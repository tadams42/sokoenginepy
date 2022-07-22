#include "image_impl.hpp"

#include "image.hpp"

#include <boost/algorithm/string.hpp>
#include <boost/geometry/strategies/default_strategy.hpp>
#include <boost/gil/extension/io/bmp.hpp>
#include <boost/gil/extension/io/png.hpp>
#include <boost/gil/pixel.hpp>
#include <boost/gil/rgba.hpp>
#include <fstream>

using std::ifstream;
using std::ios;
using std::istream;
using std::ofstream;
using std::ostream;
using std::string;

namespace gil       = boost::gil;
using image_t       = gil::rgba8_image_t;
using rgba8_pixel_t = gil::rgba8_pixel_t;
using gil::get_color;

namespace sokoengine {
namespace implementation {

static constexpr auto red_tag      = gil::red_t();
static constexpr auto green_tag    = gil::green_t();
static constexpr auto blue_tag     = gil::blue_t();
static constexpr auto alpha_tag    = gil::alpha_t();
static constexpr auto strategy_tag = boost::geometry::default_strategy();

ImageImpl::ImageImpl()
  : ImageImpl(0, 0) {}

ImageImpl::ImageImpl(uint16_t width, uint16_t height)
  : m_img(width, height) {}

void ImageImpl::swap(ImageImpl &img) { m_img.swap(img.m_img); }

void ImageImpl::swap(Image &img) { swap(*img.m_impl); }

ImageImpl::ImageImpl(const ImageImpl &rv)            = default;
ImageImpl &ImageImpl::operator=(const ImageImpl &rv) = default;
ImageImpl::ImageImpl(ImageImpl &&rv)                 = default;
ImageImpl &ImageImpl::operator=(ImageImpl &&rv)      = default;
ImageImpl::~ImageImpl()                              = default;

int ImageImpl::width() const { return m_img.width(); }

int ImageImpl::height() const { return m_img.height(); }

void ImageImpl::load(const string &path) {
  bool maybe_png = boost::ends_with(boost::to_lower_copy(path), ".png");
  bool maybe_bmp = boost::ends_with(boost::to_lower_copy(path), ".bmp");

  if (!maybe_bmp && !maybe_png) {
    throw std::invalid_argument("Only supports loading PNG and BMP images!");
  }

  ifstream src(path, ios::binary);

  if (maybe_png) {
    load(src, ImageFormats::PNG);
  } else if (maybe_bmp) {
    load(src, ImageFormats::PNG);
  }
}

void ImageImpl::load(istream &src, ImageFormats format) {
  bool found = false;

  gil::image_read_settings<gil::png_tag> png_settings;
  gil::image_read_settings<gil::bmp_tag> bmp_settings;

  try {
    switch (format) {
      case ImageFormats::PNG:
        png_settings._read_transparency_data   = true;
        png_settings._read_background          = true;
        png_settings._read_physical_resolution = true;
        m_img                                  = image_t();
        gil::read_and_convert_image(src, m_img, png_settings);
        found = true;
        break;
      case ImageFormats::BMP:
        m_img = image_t();
        gil::read_and_convert_image(src, m_img, bmp_settings);
        found = true;
        break;
        // Don't use default: to get compiler warning
    }
  } catch (ios::failure &e) {
    throw std::invalid_argument(
      string("Failed loading image. Check file permissions and also note that ")
      + "only PNG and BMP images are supported. (" + e.what() + ")"
    );
  }

  if (!found) {
    throw std::invalid_argument("Unknown image format!");
  }
}

void ImageImpl::save(const string &path) const {
  ofstream dest(path, ios::binary);
  save(dest);
}

void ImageImpl::save(ostream &dest) const {
  gil::write_view(dest, gil::const_view(m_img), gil::png_tag{});
}

ImageImpl ImageImpl::subimage(const rect_t &rect) const {
  ImageImpl retv(rect.width(), rect.height());

  gil::copy_pixels(
    gil::subimage_view(
      gil::const_view(m_img),
      rect.top_left().x(),
      rect.top_left().y(),
      rect.width(),
      rect.height()
    ),
    gil::view(retv.m_img)
  );

  return retv;
}

void ImageImpl::replace(const ImageImpl &src, const rect_t &where) {
  gil::copy_pixels(
    gil::subimage_view(
      gil::const_view(src.m_img),
      where.top_left().x(),
      where.top_left().y(),
      where.width(),
      where.height()
    ),
    gil::subimage_view(
      gil::view(m_img),
      where.top_left().x(),
      where.top_left().y(),
      where.width(),
      where.height()
    )
  );
}

void ImageImpl::grayscale() {
  gil::transform_pixels(gil::view(m_img), gil::view(m_img), [](rgba8_pixel_t &pix) {
    uint8_t val =
      (get_color(pix, red_tag) + get_color(pix, blue_tag) + get_color(pix, green_tag))
      / 3;
    return rgba8_pixel_t(val, val, val, get_color(pix, alpha_tag));
  });
}

void ImageImpl::subtract(const ImageImpl &bottom) {
  auto top_v    = gil::view(m_img);
  auto bottom_v = gil::const_view(bottom.m_img);

  if (bottom_v.width() != top_v.width() || bottom_v.height() != top_v.height()) {
    throw std::invalid_argument(
      "Subtracting images works only for images with same dimensions!"
    );
  }

  // auto non_fuzzy_eq = [](const rgba8_pixel_t &lv, const rgba8_pixel_t &rv, int delta)
  // {
  //   return (get_color(lv, red_tag) == get_color(rv, red_tag))
  //       && (get_color(lv, blue_tag) == get_color(rv, blue_tag))
  //       && (get_color(lv, green_tag) == get_color(rv, green_tag));
  // };

  auto fuzzy_eq = [](const rgba8_pixel_t &lv, const rgba8_pixel_t &rv, int delta) {
    auto component_in_range = [&](int s, int d) {
      int low = d > delta ? d - delta : 0;
      int hi  = d + delta >= 255 ? 255 : d + delta;
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

  for (int y = 0; y < h; ++y) {
    boost::gil::rgba8_ptr_t  top_it    = top_v.row_begin(y);
    boost::gil::rgba8c_ptr_t bottom_it = bottom_v.row_begin(y);

    for (int x = 0; x < w; ++x) {
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
  if (m_img.height() > box.height()) {
    offset.y(m_img.height() - box.height());
  }
  box = box.translated(offset.x(), offset.y());

  image_t result(box.width(), box.height());

  gil::copy_pixels(
    gil::subimage_view(
      gil::const_view(m_img),
      box.top_left().x(),
      box.top_left().y(),
      box.width(),
      box.height()
    ),
    gil::view(result)
  );

  m_img.swap(result);
}

void ImageImpl::set_outer_pixels_transparent(const polygon_t &polygon) {
  auto img_v = gil::view(m_img);
  auto w     = img_v.width();
  auto h     = img_v.height();

  for (int y = 0; y < h; ++y) {
    boost::gil::rgba8_ptr_t it = img_v.row_begin(y);
    for (int x = 0; x < w; ++x) {
      if (!boost::geometry::within(pointf_t(x, y), polygon, strategy_tag)) {
        get_color(it[x], alpha_tag) = 0;
      }
    }
  }
}

pixel_t ImageImpl::pixel(size_t x, size_t y) const {
  rgba8_pixel_t pixel = *(gil::const_view(m_img).at(x, y));
  return pixel_t(
    get_color(pixel, red_tag),
    get_color(pixel, green_tag),
    get_color(pixel, blue_tag),
    get_color(pixel, alpha_tag)
  );
}

} // namespace implementation
} // namespace sokoengine
