#include "sokoenginepyext.hpp"

using namespace std;
using namespace sokoengine;

void export_direction(py::module &m) {
  py::enum_<Direction>(m, "Direction")
    .value("UP", Direction::UP)
    .value("DOWN", Direction::DOWN)
    .value("LEFT", Direction::LEFT)
    .value("RIGHT", Direction::RIGHT)
    .value("SOUTH_EAST", Direction::SOUTH_EAST)
    .value("SOUTH_WEST", Direction::SOUTH_WEST)
    .value("NORTH_EAST", Direction::NORTH_EAST)
    .value("NORTH_WEST", Direction::NORTH_WEST)
    // We don't want constants be available in module scope
    // .export_values()
    .def_property_readonly(
      "opposite",
      [](const Direction &self) { return opposite(self); },
      py::return_value_policy::reference_internal
    )

    .def_static("__len__", []() { return DIRECTIONS_COUNT; })

    .def(
      "__str__",
      [](const Direction &self) { return repr_direction(self); },
      py::return_value_policy::reference
    )

    .def(
      "__repr__",
      [](const Direction &self) { return str_direction(self); },
      py::return_value_policy::reference
    )
    ;
}
