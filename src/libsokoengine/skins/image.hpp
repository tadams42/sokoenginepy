#ifndef IMAGE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define IMAGE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

namespace sokoengine {

namespace implementation {
class ImageImpl;
} // namespace implementation

namespace skins {

struct LIBSOKOENGINE_API pixel_t {
  uint8_t r, g, b, a;

  constexpr pixel_t(uint8_t r_ = 0, uint8_t g_ = 0, uint8_t b_ = 0, uint8_t a_ = 255)
    : r(r_)
    , g(g_)
    , b(b_)
    , a(a_) {}
};

///
/// Read only, 8 bit, RGBA image.
///
/// - image loading from PNG and BMP formats
/// - read-only access to individual pixels
/// - image saving into PNG
///
/// It is simple and limited in features by design. Intended to be used as image data
/// storage for small images of Sokoban skins.
///
///
class LIBSOKOENGINE_API Image {
public:
  Image();
  Image(const Image &rv);
  Image &operator=(const Image &rv);
  Image(Image &&rv);
  Image &operator=(Image &&rv);
  ~Image();

  void swap(Image &img);

  size_t  width() const;
  size_t  height() const;
  pixel_t pixel(size_t x, size_t y) const;
  bool    is_empty() const;

  ///
  /// Saves image to @a path
  ///
  /// Format is always PNG, regardless of file name in @a path.
  ///
  void save(const std::string &path) const;

private:
  std::unique_ptr<implementation::ImageImpl> m_impl;
  friend class implementation::ImageImpl;
};

} // namespace skins

using skins::Image;
using skins::pixel_t;

} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
