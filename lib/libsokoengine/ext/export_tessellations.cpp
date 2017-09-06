#include <pybind11/pybind11.h>
#include <sokoengine.hpp>
#include <map>

using namespace std;
namespace py = pybind11;
using namespace sokoengine;

void export_tessellations(py::module& m) {
  py::enum_<CellOrientation>(m, "CellOrientation")
    .value("DEFAULT", CellOrientation::DEFAULT)
    .value("TRIANGLE_DOWN", CellOrientation::TRIANGLE_DOWN)
    .value("OCTAGON", CellOrientation::OCTAGON)
    // We don't want constants be available in module scope
    // .export_values()
  ;

  py::class_<Tessellation>(m, "TessellationBase")
    // protocols
    .def("__eq__", &Tessellation::operator==)
    .def("__ne__", &Tessellation::operator!=)
    .def("__str__", &Tessellation::str)
    .def("__repr__", &Tessellation::repr)

    .def_property_readonly(
      "legal_directions",
      [](const Tessellation& self) -> py::list {
        auto native_retv = self.legal_directions();
        py::list retv;
        for(auto d : native_retv) retv.append(d);
        return retv;
      }
    )

    .def(
      "neighbor_position", [](
        const Tessellation& self, position_t position, const Direction& direction,
        size_t board_width, size_t board_height
      ) -> py::object {
        position_t retv = self.neighbor_position(
          position, direction, board_width, board_height
        );
        if (retv == NULL_POSITION) return py::none();
        else return py::cast(retv);
      },
      py::arg("position"), py::arg("direction"), py::arg("board_width"),
      py::arg("board_height")
    )

    .def_property_readonly("graph_type", &Tessellation::graph_type)

    .def(
      "char_to_atomic_move",
      &Tessellation::char_to_atomic_move,
      py::arg("input_chr")
    )

    .def(
      "atomic_move_to_char",
      &Tessellation::atomic_move_to_char,
      py::arg("atomic_move")
    )

    .def(
      "cell_orientation",
      &Tessellation::cell_orientation,
      py::arg("position"), py::arg("board_width"), py::arg("board_height")
    )
  ;

  py::class_<SokobanTessellation, Tessellation>(m, "SokobanTessellation")
    .def(
      py::init([]() { return Tessellation::SOKOBAN; }),
      py::return_value_policy::reference
    )
  ;

  py::class_<HexobanTessellation, Tessellation>(m, "HexobanTessellation")
    .def(
      py::init([]() { return Tessellation::HEXOBAN; }),
      py::return_value_policy::reference
    )
  ;

  py::class_<OctobanTessellation, Tessellation>(m, "OctobanTessellation")
    .def(
      py::init([]() { return Tessellation::OCTOBAN; }),
      py::return_value_policy::reference
    )
  ;

  py::class_<TriobanTessellation, Tessellation>(m, "TriobanTessellation")
    .def(
      py::init([]() { return Tessellation::TRIOBAN; }),
      py::return_value_policy::reference
    )
  ;
}
