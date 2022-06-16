#include "sokoenginepyext.hpp"

#include <map>

using namespace std;
using sokoengine::board_size_t;
using sokoengine::position_t;
using sokoengine::game::BaseTessellation;
using sokoengine::game::Config;
using sokoengine::game::Direction;
using sokoengine::game::HexobanTessellation;
using sokoengine::game::OctobanTessellation;
using sokoengine::game::SokobanTessellation;
using sokoengine::game::Tessellation;
using sokoengine::game::TriobanTessellation;

void export_tessellations(py::module &m) {
  py::enum_<Tessellation>(m, "Tessellation")
    .value("SOKOBAN", Tessellation::SOKOBAN)
    .value("HEXOBAN", Tessellation::HEXOBAN)
    .value("TRIOBAN", Tessellation::TRIOBAN)
    .value("OCTOBAN", Tessellation::OCTOBAN)
    // We don't want constants be available in module scope
    // .export_values()
    ;

  py::class_<BaseTessellation>(m, "BaseTessellation", py::is_final())
    .def("instance", &BaseTessellation::instance, py::return_value_policy::reference)

    .def_property_readonly("legal_directions", &BaseTessellation::legal_directions)

    .def(
      "neighbor_position",
      [](const BaseTessellation &self, position_t position, const Direction &direction,
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

    .def_property_readonly("graph_type", &BaseTessellation::graph_type)

    .def("char_to_pusher_step", &BaseTessellation::char_to_pusher_step,
         py::arg("input_chr"))

    .def("pusher_step_to_char", &BaseTessellation::pusher_step_to_char,
         py::arg("pusher_step"))

    .def("cell_orientation", &BaseTessellation::cell_orientation, py::arg("position"),
         py::arg("board_width"), py::arg("board_height"));

  py::class_<SokobanTessellation, BaseTessellation>(m, "SokobanTessellation",
                                                    py::is_final())
    .def(py::init<>());

  py::class_<HexobanTessellation, BaseTessellation>(m, "HexobanTessellation",
                                                    py::is_final())
    .def(py::init<>());

  py::class_<OctobanTessellation, BaseTessellation>(m, "OctobanTessellation",
                                                    py::is_final())
    .def(py::init<>());

  py::class_<TriobanTessellation, BaseTessellation>(m, "TriobanTessellation",
                                                    py::is_final())
    .def(py::init<>());
}
