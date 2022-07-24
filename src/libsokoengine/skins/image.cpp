#include "image.hpp"

#include "image_impl.hpp"

using sokoengine::implementation::ImageImpl;
using std::string;

namespace sokoengine {
namespace skins {

Image::Image()
  : m_impl(std::make_unique<ImageImpl>()) {}

Image::Image(const Image &rv)
  : m_impl(std::make_unique<ImageImpl>(*rv.m_impl)) {}

Image &Image::operator=(const Image &rv) {
  if (this != &rv)
    m_impl = std::make_unique<ImageImpl>(*rv.m_impl);
  return *this;
}

Image::Image(Image &&rv)            = default;
Image &Image::operator=(Image &&rv) = default;
Image::~Image()                     = default;

void Image::save(const std::string &path) const { m_impl->save(path); }

void Image::save(std::ostream &dest) const { m_impl->save(dest); }

uint32_t Image::width() const { return m_impl->width(); }

uint32_t Image::height() const { return m_impl->height(); }

pixel_t Image::pixel(uint32_t x, uint32_t y) const { return m_impl->pixel(x, y); }

void Image::swap(Image &img) { m_impl.swap(img.m_impl); }

bool Image::is_empty() const { return m_impl->height() <= 0 || m_impl->width() <= 0; }

} // namespace skins
} // namespace sokoengine
