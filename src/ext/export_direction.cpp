#include <boost/python.hpp>
#include <sokoengine.hpp>

using namespace boost::python;
using namespace sokoengine;

struct DirectionPickle : boost::python::pickle_suite {
  static boost::python::tuple getinitargs(Direction const& d) {
    return boost::python::make_tuple(d.get_value());
  }
};

void export_direction() {
  enum_<EDirection>("EDirection")
    .value("UP", EDirection::UP)
    .value("NORTH_EAST", EDirection::NORTH_EAST)
    .value("RIGHT", EDirection::RIGHT)
    .value("SOUTH_EAST", EDirection::SOUTH_EAST)
    .value("DOWN", EDirection::DOWN)
    .value("SOUTH_WEST", EDirection::SOUTH_WEST)
    .value("LEFT", EDirection::LEFT)
    .value("NORTH_WEST", EDirection::NORTH_WEST)
    // We don't want constants be available in module scope
    // .export_values()
  ;

  scope Direction_class = class_<Direction>(
      "Direction",
      init<optional<EDirection> >((arg("value")=EDirection::UP))
    )
    // pickle support
    .def_pickle(DirectionPickle())

    // protocols
    .def("__eq__", &Direction::operator==)
    .def("__ne__", &Direction::operator!=)
    .def("__str__", &Direction::str)
    .def("__repr__", &Direction::repr)

    .def("_len", &Direction::len).staticmethod("_len")

    .add_property(
      "opposite",
      make_function(&Direction::opposite, return_internal_reference<>())
    )
  ;

  Direction_class.attr("UP") = object(ptr(&Direction::UP));
  Direction_class.attr("DOWN") = object(ptr(&Direction::DOWN));
  Direction_class.attr("LEFT") = object(ptr(&Direction::LEFT));
  Direction_class.attr("RIGHT") = object(ptr(&Direction::RIGHT));
  Direction_class.attr("NORTH_EAST") = object(ptr(&Direction::NORTH_EAST));
  Direction_class.attr("NORTH_WEST") = object(ptr(&Direction::NORTH_WEST));
  Direction_class.attr("SOUTH_EAST") = object(ptr(&Direction::SOUTH_EAST));
  Direction_class.attr("SOUTH_WEST") = object(ptr(&Direction::SOUTH_WEST));
}
