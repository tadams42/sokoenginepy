#ifndef IMAGE_BACKEND_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define IMAGE_BACKEND_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "geometry.hpp"

#include <boost/gil/image.hpp>

namespace sokoengine {

namespace skins {
struct pixel_t;
class Image;
} // namespace skins

namespace implementation {

class LIBSOKOENGINE_LOCAL ImageImpl {
public:
  typedef boost::gil::rgba8_image_t image_t;
  image_t                           m_img;

  ImageImpl();
  ImageImpl(uint16_t width, uint16_t height);

  ImageImpl(const ImageImpl &rv);
  ImageImpl &operator=(const ImageImpl &rv);
  ImageImpl(ImageImpl &&rv);
  ImageImpl &operator=(ImageImpl &&rv);
  ~ImageImpl();

  void swap(ImageImpl &img);
  void swap(skins::Image &img);

  int width() const;
  int height() const;

  ///
  /// Loads .png or .bmp image from @a path.
  ///
  /// @throws std::invalid_argument if @a path can't be loaded for any reason:
  ///   - file doesn't exist / can't be read
  ///   - file doesn't contain correct image format (only PNG and BMP are supported)
  ///   -...
  ///
  void load(const std::string &path);

  void load(const std::istream &stream);

  ///
  /// Saves image to @a path
  ///
  /// Saving format is always PNG, regardless of file name in @a path.
  ///
  void save(const std::string &path) const;

  ///
  /// Copies this image pixels that are inside of @a rect into new image.
  ///
  ImageImpl subimage(const rect_t &rect) const;

  ///
  /// Takes pixels from region @a where in @a src and uses them to replace pixels in
  /// same region of this image.
  ///
  /// @warning Doesn't validate if @a where is valid for both images.
  ///
  void replace(const ImageImpl &src, const rect_t &where);

  ///
  /// Converts this image to grayscale image.
  ///
  void grayscale();

  ///
  /// For each pixel in this image, subtracts corresponding pixel from @a bottom.
  /// If this and bottom dimensions are not exactly the same, does nothing.
  ///
  void subtract(const ImageImpl &bottom);

  ///
  /// Takes bounding box of @a p, aligns it to bottom - left ot this image and then
  /// returns new image from pixels in that bounding box.
  ///
  void crop_to_bounding_box(const polygon_t &p);

  ///
  /// Takes bounding box of @a p, aligns it to bottom - left ot this image and then sets
  /// alpha channel value for all pixels outside of @a p to zero (making them fully
  /// transparent).
  ///
  void set_outer_pixels_transparent(const polygon_t &p);

  skins::pixel_t pixel(size_t x, size_t y) const;
};

} // namespace implementation
} // namespace sokoengine

#endif // HEADER_GUARD
