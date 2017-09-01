#include <pybind11/pybind11.h>
#include <sokoengine.hpp>

using namespace std;
namespace py = pybind11;
using namespace sokoengine;


void export_direction(py::module& m) {
  py::enum_<EDirection>(m, "EDirection")
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

  py::class_<Direction>(m, "Direction")
    .def(py::init<const EDirection&>(), py::arg("value")=EDirection::UP)

    // protocols
    .def("__eq__", &Direction::operator==)
    .def("__ne__", &Direction::operator!=)
    .def("__str__", &Direction::str)
    .def("__repr__", &Direction::repr)

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

    .def(py::pickle(
      [](const Direction &self) { // __getstate__
        return py::make_tuple(self.m_direction);
      },
      [](py::tuple t) { // __setstate__
        if (t.size() != 1) throw std::runtime_error("Invalid state!");
        return make_unique<Direction>(t[0].cast<EDirection>());
      }
    ))
  ;
}
