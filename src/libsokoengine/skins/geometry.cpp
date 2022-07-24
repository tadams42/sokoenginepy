#include "geometry.hpp"

#include <cmath>

using std::vector;

namespace sokoengine {
namespace implementation {

rect_t rectf_t::to_aligned_rect() const {
  int x_min = int(std::floor(xp));
  int x_max = int(std::ceil(xp + w));
  int y_min = int(std::floor(yp));
  int y_max = int(std::ceil(yp + h));
  return rect_t(x_min, y_min, x_max - x_min, y_max - y_min);
}

rectf_t bounding_rect(const polygon_t &polygon) {
  auto i    = polygon.outer().cbegin();
  auto iend = polygon.outer().cend();

  if (i == iend) {
    return rectf_t();
  }

  double minx, maxx = 0, miny, maxy = 0;
  minx = i->x();
  miny = i->y();

  for (; i != iend; ++i) {
    if (i->x() < minx)
      minx = i->x();
    else if (i->x() > maxx)
      maxx = i->x();
    if (i->y() < miny)
      miny = i->y();
    else if (i->y() > maxy)
      maxy = i->y();
  }

  return rectf_t(minx, miny, maxx - minx, maxy - miny);
}

} // namespace implementation
} // namespace sokoengine
