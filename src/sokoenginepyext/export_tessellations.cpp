#include "sokoenginepyext.hpp"

#include <map>

using namespace std;
using sokoengine::board_size_t;
using sokoengine::Config;
using sokoengine::game::CellOrientation;
using sokoengine::game::Direction;
using sokoengine::game::HexobanTessellation;
using sokoengine::game::OctobanTessellation;
using sokoengine::game::position_t;
using sokoengine::game::SokobanTessellation;
using sokoengine::game::Tessellation;
using sokoengine::game::TriobanTessellation;

void export_tessellations(py::module &m) {
  py::enum_<CellOrientation>(m, "CellOrientation")
    .value("DEFAULT", CellOrientation::DEFAULT)
    .value("TRIANGLE_DOWN", CellOrientation::TRIANGLE_DOWN)
    .value("OCTAGON", CellOrientation::OCTAGON)
    // We don't want constants be available in module scope
    // .export_values()
    ;

  py::class_<Tessellation>(m, "CTessellationBase")
    // protocols
    .def("__eq__", &Tessellation::operator==)
    .def("__ne__", &Tessellation::operator!=)
    .def("__str__", &Tessellation::str)
    .def("__repr__", &Tessellation::repr)

    .def_property_readonly("legal_directions", &Tessellation::legal_directions)

    .def(
      "neighbor_position",
      [](const Tessellation &self, position_t position, const Direction &direction,
         board_size_t board_width, board_size_t board_height) -> py::object {
        auto retv =
          self.neighbor_position(position, direction, board_width, board_height);
        if (retv > Config::MAX_POS)
          return py::none();
        else
          return py::cast(retv);
      },
      py::arg("position"), py::arg("direction"), py::arg("board_width"),
      py::arg("board_height"))

    .def_property_readonly("graph_type", &Tessellation::graph_type)

    .def("char_to_pusher_step", &Tessellation::char_to_pusher_step,
         py::arg("input_chr"))

    .def("pusher_step_to_char", &Tessellation::pusher_step_to_char,
         py::arg("pusher_step"))

    .def("cell_orientation", &Tessellation::cell_orientation, py::arg("position"),
         py::arg("board_width"), py::arg("board_height"));

  py::class_<SokobanTessellation, Tessellation>(m, "SokobanTessellation")
    .def(py::init([]() { return Tessellation::SOKOBAN; }),
         py::return_value_policy::reference);

  py::class_<HexobanTessellation, Tessellation>(m, "HexobanTessellation")
    .def(py::init([]() { return Tessellation::HEXOBAN; }),
         py::return_value_policy::reference);

  py::class_<OctobanTessellation, Tessellation>(m, "OctobanTessellation")
    .def(py::init([]() { return Tessellation::OCTOBAN; }),
         py::return_value_policy::reference);

  py::class_<TriobanTessellation, Tessellation>(m, "TriobanTessellation")
    .def(py::init([]() { return Tessellation::TRIOBAN; }),
         py::return_value_policy::reference);
}
