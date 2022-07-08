#include "sokoenginepyext.hpp"

#include <map>

using sokoengine::board_size_t;
using sokoengine::position_t;
using sokoengine::game::BaseTessellation;
using sokoengine::game::Direction;
using sokoengine::game::Directions;
using sokoengine::game::GraphType;
using sokoengine::game::HexobanTessellation;
using sokoengine::game::OctobanTessellation;
using sokoengine::game::PusherStep;
using sokoengine::game::SokobanTessellation;
using sokoengine::game::Tessellation;
using sokoengine::game::TriobanTessellation;
using sokoengine::io::CellOrientation;

void export_tessellations(py::module &m) {
  py::enum_<Tessellation>(m, "Tessellation")
    .value("SOKOBAN", Tessellation::SOKOBAN)
    .value("HEXOBAN", Tessellation::HEXOBAN)
    .value("TRIOBAN", Tessellation::TRIOBAN)
    .value("OCTOBAN", Tessellation::OCTOBAN);

  auto pyBaseTessellation =
    py::class_<BaseTessellation>(m, "BaseTessellation", py::is_final());

  pyBaseTessellation
    .def_static(
      "instance", &BaseTessellation::instance, py::return_value_policy::reference
    )

    .def_property_readonly("legal_directions", &BaseTessellation::legal_directions)

    .def(
      "neighbor_position",
      [](
        const BaseTessellation &self,
        py_int_t                position,
        const Direction        &direction,
        py_int_t                width,
        py_int_t                height
      ) {
        return self.neighbor_position(
          position_or_throw(position),
          direction,
          size_or_throw(width),
          size_or_throw(height)
        );
      },
      py::arg("position"),
      py::arg("direction"),
      py::arg("board_width"),
      py::arg("board_height")
    )
    .def_property_readonly("graph_type", &BaseTessellation::graph_type)
    .def(
      "char_to_pusher_step",
      &BaseTessellation::char_to_pusher_step,
      py::arg("input_chr")
    )
    .def(
      "pusher_step_to_char",
      &BaseTessellation::pusher_step_to_char,
      py::arg("pusher_step")
    )
    .def(
      "cell_orientation",
      [](
        const BaseTessellation &self, py_int_t position, py_int_t width, py_int_t height
      ) {
        return self.cell_orientation(
          position_or_throw(position), size_or_throw(width), size_or_throw(height)
        );
      },
      py::arg("position"),
      py::arg("board_width"),
      py::arg("board_height")
    );

  py::class_<SokobanTessellation>(
    m, "SokobanTessellation", pyBaseTessellation, py::is_final()
  )
    .def(py::init<>());

  py::class_<HexobanTessellation>(
    m, "HexobanTessellation", pyBaseTessellation, py::is_final()
  )
    .def(py::init<>());

  py::class_<OctobanTessellation>(
    m, "OctobanTessellation", pyBaseTessellation, py::is_final()
  )
    .def(py::init<>());

  py::class_<TriobanTessellation>(
    m, "TriobanTessellation", pyBaseTessellation, py::is_final()
  )
    .def(py::init<>());
}
