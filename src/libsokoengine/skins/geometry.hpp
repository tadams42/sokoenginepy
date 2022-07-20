#ifndef GEOMETRY_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define GEOMETRY_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"
#include <boost/geometry.hpp>
#include <boost/geometry/geometries/point_xy.hpp>

namespace sokoengine {
namespace implementation {

typedef boost::geometry::model::d2::point_xy<int>    point_t;
typedef boost::geometry::model::d2::point_xy<double> pointf_t;
typedef boost::geometry::model::polygon<pointf_t>    polygon_t;

class LIBSOKOENGINE_LOCAL rect_t {
public:
  explicit constexpr rect_t(int left = 0, int top = 0, int width = 0, int height = 0)
    : xp(left)
    , yp(top)
    , w(width)
    , h(height) {}

  constexpr point_t top_left() const { return point_t(xp, yp); }

  constexpr point_t top_right() const { return point_t(xp + w, yp); }

  constexpr point_t bottom_left() const { return point_t(xp, yp + h); }

  constexpr point_t bottom_right() const { return point_t(xp + w, yp + h); }

  constexpr int width() const { return w; }

  constexpr int height() const { return h; }

  constexpr rect_t translated(int dx, int dy) const {
    return rect_t(xp + dx, yp + dy, w, h);
  }

private:
  int xp, yp, w, h;
};

class LIBSOKOENGINE_LOCAL rectf_t {
public:
  explicit constexpr rectf_t(
    double left = 0, double top = 0, double width = 0, double height = 0
  )
    : xp(left)
    , yp(top)
    , w(width)
    , h(height) {}

  constexpr pointf_t top_left() const { return pointf_t(xp, yp); }

  constexpr pointf_t top_right() const { return pointf_t(xp + w, yp); }

  constexpr pointf_t bottom_left() const { return pointf_t(xp, yp + h); }

  constexpr pointf_t bottom_right() const { return pointf_t(xp + w, yp + h); }

  constexpr double width() const { return w; }

  constexpr double height() const { return h; }

  constexpr rectf_t translated(double dx, double dy) const {
    return rectf_t(xp + dx, yp + dy, w, h);
  }

  ///
  /// Returns a rect_t based on the values of this rectangle that is the smallest
  /// possible integer rectangle that completely contains this rectangle.
  ///
  rect_t to_aligned_rect() const;

private:
  double xp, yp, w, h;
};

rectf_t bounding_rect(const polygon_t &polygon);

} // namespace implementation
} // namespace sokoengine

#endif // HEADER_GUARD
