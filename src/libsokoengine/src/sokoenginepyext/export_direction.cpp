#include "sokoenginepyext.hpp"

using namespace std;
using namespace sokoengine;


void export_direction(py::module& m) {
  py::class_<Direction>(m, "Direction")
    .def(
      py::init(
        [](Direction::packed_t packed) { return Direction::unpack(packed); }
      ),
      py::return_value_policy::reference
    )

    // protocols
    .def("__eq__", &Direction::operator==)
    .def("__ne__", &Direction::operator!=)
    .def("__str__", &Direction::str)
    .def("__repr__", &Direction::repr)

    .def_static("__len__", []() { return static_cast<int>(Direction::len()); })

    .def_property_readonly(
      "opposite", &Direction::opposite, py::return_value_policy::reference
    )

    .def_readonly_static(
      "UP", &Direction::UP, py::return_value_policy::reference
    )
    .def_readonly_static(
      "DOWN", &Direction::DOWN, py::return_value_policy::reference
    )
    .def_readonly_static(
      "LEFT", &Direction::LEFT, py::return_value_policy::reference
    )
    .def_readonly_static(
      "RIGHT", &Direction::RIGHT, py::return_value_policy::reference
    )
    .def_readonly_static(
      "NORTH_EAST", &Direction::NORTH_EAST, py::return_value_policy::reference
    )
    .def_readonly_static(
      "NORTH_WEST", &Direction::NORTH_WEST, py::return_value_policy::reference
    )
    .def_readonly_static(
      "SOUTH_EAST", &Direction::SOUTH_EAST, py::return_value_policy::reference
    )
    .def_readonly_static(
      "SOUTH_WEST", &Direction::SOUTH_WEST, py::return_value_policy::reference
    )

    .def(
      py::pickle(
        [](const Direction &self) { // __getstate__
          return py::make_tuple(self.pack());
        },
        [](py::tuple t) { // __setstate__
          if (t.size() != 1) throw std::runtime_error("Invalid state!");
          return Direction::unpack(t[0].cast<Direction::packed_t>());
        }
      ),
      py::return_value_policy::reference
    )
  ;
}
