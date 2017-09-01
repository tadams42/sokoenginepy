#include <pybind11/pybind11.h>
#include <memory>
#include <sokoengine.hpp>

#include "pybind11_addons.hpp"

using namespace std;
namespace py = pybind11;
using namespace sokoengine;

void export_boards(py::module& m) {
  py::class_<VariantBoard, std::shared_ptr<VariantBoard> >(m, "VariantBoard")
    .def_static(
      "instance_from", [](
        const py::object& tessellation_or_description, size_t board_width,
        size_t board_height, const py::object& board_str
      ) -> py::object {
        py::extract<string> string_obj(tessellation_or_description);
        py::extract<const Tessellation&> tessellation_obj(tessellation_or_description);

        string description;
        if (string_obj.check()) {
          description = string_obj();
        } else if (tessellation_obj.check()) {
          const Tessellation& tessellation = tessellation_obj();
          description = tessellation.str();
        } else throw UnknownTessellationError(
          string() + "tessellation_or_description can't be converted to " + 
          "known tessellation type"
        );

        shared_ptr<VariantBoard> retv;

        if (!board_str.is_none()) {
          string board_str_converted = py::extract<string>(board_str)();
          retv = std::move(
            VariantBoard::instance_from(description, board_str_converted)
          );
        } else {
          retv = std::move(
            VariantBoard::instance_from(description, board_width, board_height)
          );
        }

        if (description == "sokoban")
          return py::cast<shared_ptr<SokobanBoard> >(
            dynamic_pointer_cast<SokobanBoard>(retv)
          );
        else if (description == "trioban")
          return py::cast<shared_ptr<TriobanBoard> >(
            dynamic_pointer_cast<TriobanBoard>(retv)
          );
        else if (description == "octoban")
          return py::cast<shared_ptr<OctobanBoard> >(
            dynamic_pointer_cast<OctobanBoard>(retv)
          );
        else if (description == "hexoban")
          return py::cast<shared_ptr<HexobanBoard> >(
            dynamic_pointer_cast<HexobanBoard>(retv)
          );
        else throw UnknownTessellationError(
          "Don't know about tessellation: " + description
        );

        return py::none();
      },
      py::arg("tessellation_or_description")=py::cast<string>("sokoban"),
      py::arg("board_width")=0,
      py::arg("board_height")=0,
      py::arg("board_str")=py::none()
    )

    .def_static(
      "is_board_string", &VariantBoard::is_board_string, py::arg("line")
    )

    .def_static(
      "parse_board_string", [](const string& line) {
        auto native_retv = VariantBoard::parse_board_string(line);
        py::list retv;
        for(auto str: native_retv) retv.append(str);
        return retv;
      },
      py::arg("line")
    )

    .def_property_readonly(
      "_graph", &VariantBoard::graph,
      py::return_value_policy::reference_internal
    )

    .def_property_readonly(
      "tessellation", &VariantBoard::tessellation,
      py::return_value_policy::reference
    )

    // protocols
    .def(
      "__getitem__", [](VariantBoard& self, position_t position) -> BoardCell& {
        return self.cell_at(position);
      },
      py::return_value_policy::reference_internal,
      py::arg("position")
    )

    .def(
      "__setitem__", [](
        VariantBoard& self, position_t position, const BoardCell& board_cell
      ) {
        self.cell_at(position) = board_cell;
      },
      py::arg("position"), py::arg("board_cell")
    )

    .def(
      "__setitem__", [](
        VariantBoard& self, position_t position, char board_cell
      ) {
        self.cell_at(position) = BoardCell(board_cell);
      },
      py::arg("position"), py::arg("board_cell")
    )

    .def(
      "__contains__", &VariantBoard::contains, py::arg("position")
    )

    .def("__str__", &VariantBoard::str)
    .def("__repr__", &VariantBoard::repr)

    .def(
      "to_str", &SokobanBoard::to_str,
      py::arg("use_visible_floor")=false, py::arg("rle_encode")=false
    )

    .def_property_readonly("width", &VariantBoard::width)
    .def_property_readonly("height", &VariantBoard::height)
    .def_property_readonly("size", &VariantBoard::size)

    .def(
      "neighbor", [](
        const VariantBoard& self, position_t from_position,
        const Direction& direction
      ) -> py::object {
        auto retv = self.neighbor_at(from_position, direction);
        if (retv == NULL_POSITION) return py::none();
        else return py::cast(retv);
      },
      py::arg("from_position"), py::arg("direction")
    )

    .def(
      "wall_neighbors", [](
        const VariantBoard& self, position_t from_position
      ) {
        auto native_retv = self.wall_neighbors(from_position);
        py::list retv;
        for(auto val : native_retv) retv.append(py::cast(val));
        return retv;
      },
      py::arg("from_position")
    )

    .def(
      "all_neighbors", [](
        const VariantBoard& self, position_t from_position) {
        auto native_retv = self.all_neighbors(from_position);
        py::list retv;
        for(auto val : native_retv) retv.append(py::cast(val));
        return retv;
      },
      py::arg("from_position")
    )

    .def("clear", &VariantBoard::clear)
    .def("mark_play_area", &VariantBoard::mark_play_area)

    .def(
      "positions_reachable_by_pusher", [](
        const VariantBoard& self, position_t pusher_position,
        const py::object& excluded_positions
      ) {
        Positions excluded_positions_converted;
        if (!excluded_positions.is_none())
          for (auto pos : excluded_positions)
            excluded_positions_converted.push_back(pos.cast<position_t>());
        Positions native_retv = self.positions_reachable_by_pusher(
          pusher_position, excluded_positions_converted
        );
        py::list retv;
        for (auto val : native_retv) retv.append(py::cast(val));
        return retv;
      },
      py::arg("pusher_position"), py::arg("excluded_positions")=py::none()
    )

    .def(
      "normalized_pusher_position", [](
        const VariantBoard& self, position_t pusher_position,
        const py::object& excluded_positions
      ) -> position_t {
        Positions excluded_positions_converted;
        if (!excluded_positions.is_none())
          for (auto pos : excluded_positions)
            excluded_positions_converted.push_back(pos.cast<position_t>());
        return self.normalized_pusher_position(
          pusher_position, excluded_positions_converted
        );
      },
      py::arg("pusher_position"), py::arg("excluded_positions")=py::none()
    )

    .def(
      "path_destination", [](
        const VariantBoard& self, position_t start_position,
        const py::object& directions_path
      ) -> position_t {
        Directions directions_path_converted;

        if (!directions_path.is_none())
          for (auto d : directions_path)
            directions_path_converted.push_back(d.cast<Direction>());

        return self.path_destination(start_position, directions_path_converted);
      },
      py::arg("start_position"), py::arg("directions_path")
    )

    .def(
      "find_move_path", [](
        const VariantBoard& self, position_t start_position,
        position_t end_position
      ) {
        auto native_retv = self.find_move_path(start_position, end_position);
        py::list retv;
        for(auto val : native_retv) retv.append(py::cast(val));
        return retv;
      },
      py::arg("start_position"), py::arg("end_position")
    )

    .def(
      "find_jump_path", [](
        const VariantBoard& self, position_t start_position,
        position_t end_position
      ) {
        auto native_retv = self.find_jump_path(start_position, end_position);
        py::list retv;
        for(auto val : native_retv) retv.append(py::cast(val));
        return retv;
      },
      py::arg("start_position"), py::arg("end_position")
    )

    .def(
      "positions_path_to_directions_path", [](
        const VariantBoard& self, const py::list& positions_path
      ) {
        Positions path;
        for(auto val : positions_path) path.push_back(val.cast<position_t>());
        auto native_retv = self.positions_path_to_directions_path(path);
        py::list retv;
        for(auto val : native_retv) retv.append(py::cast(val));
        return retv;
      },
      py::arg("positions_path")
    )

    .def(
      "cell_orientation", &VariantBoard::cell_orientation, py::arg("position")
    )

    .def("add_row_top", &VariantBoard::add_row_top)
    .def("add_row_bottom", &VariantBoard::add_row_bottom)
    .def("add_column_left", &VariantBoard::add_column_left)
    .def("add_column_right", &VariantBoard::add_column_right)
    .def("remove_row_top", &VariantBoard::remove_row_top)
    .def("remove_row_bottom", &VariantBoard::remove_row_bottom)
    .def("remove_column_left", &VariantBoard::remove_column_left)
    .def("remove_column_right", &VariantBoard::remove_column_right)
    .def("trim_left", &VariantBoard::trim_left)
    .def("trim_right", &VariantBoard::trim_right)
    .def("trim_top", &VariantBoard::trim_top)
    .def("trim_bottom", &VariantBoard::trim_bottom)
    .def("reverse_rows", &VariantBoard::reverse_rows)
    .def("reverse_columns", &VariantBoard::reverse_columns)

    .def(
      "resize", &VariantBoard::resize,
      py::arg("new_width"), py::arg("new_height")
    )

    .def(
      "resize_and_center", &VariantBoard::resize_and_center,
      py::arg("new_width"), py::arg("new_height")
    )

    .def("trim", &VariantBoard::trim)
  ;

  py::class_<SokobanBoard, VariantBoard, std::shared_ptr<SokobanBoard> >(m, "SokobanBoard")
    .def(
      py::init([](
        size_t board_width, size_t board_height, const py::object& board_str
      ) {
        if (!board_str.is_none()) {
          string board_str_converted = board_str.cast<string>();
          return make_unique<SokobanBoard>(board_str_converted);
        } else {
          return make_unique<SokobanBoard>(board_width, board_height);
        }
      }),
      py::arg("board_width")=0,
      py::arg("board_height")=0,
      py::arg("board_str")=py::none()
    )

    // protocols
    .def("__eq__", &SokobanBoard::operator==)
    .def("__ne__", &SokobanBoard::operator!=)
  ;

  py::class_<HexobanBoard, VariantBoard, std::shared_ptr<HexobanBoard> >(m, "HexobanBoard")
    .def(
      py::init([](
        size_t board_width, size_t board_height, const py::object& board_str
      ) {
        if (!board_str.is_none()) {
          string board_str_converted = board_str.cast<string>();
          return make_unique<HexobanBoard>(board_str_converted);
        } else {
          return make_unique<HexobanBoard>(board_width, board_height);
        }
      }),
      py::arg("board_width")=0,
      py::arg("board_height")=0,
      py::arg("board_str")=py::none()
    )

    // protocols
    .def("__eq__", &HexobanBoard::operator==)
    .def("__ne__", &HexobanBoard::operator!=)
  ;

  py::class_<TriobanBoard, VariantBoard, std::shared_ptr<TriobanBoard> >(m, "TriobanBoard")
    .def(
      py::init([](
        size_t board_width, size_t board_height, const py::object& board_str
      ) {
        if (!board_str.is_none()) {
          string board_str_converted = board_str.cast<string>();
          return make_unique<TriobanBoard>(board_str_converted);
        } else {
          return make_unique<TriobanBoard>(board_width, board_height);
        }
      }),
      py::arg("board_width")=0,
      py::arg("board_height")=0,
      py::arg("board_str")=py::none()
    )

    // protocols
    .def("__eq__", &TriobanBoard::operator==)
    .def("__ne__", &TriobanBoard::operator!=)
  ;

  py::class_<OctobanBoard, VariantBoard, std::shared_ptr<OctobanBoard> >(m, "OctobanBoard")
    .def(
      py::init([](
        size_t board_width, size_t board_height, const py::object& board_str
      ) {
        if (!board_str.is_none()) {
          string board_str_converted = board_str.cast<string>();
          return make_unique<OctobanBoard>(board_str_converted);
        } else {
          return make_unique<OctobanBoard>(board_width, board_height);
        }
      }),
      py::arg("board_width")=0,
      py::arg("board_height")=0,
      py::arg("board_str")=py::none()
    )

    // protocols
    .def("__eq__", &OctobanBoard::operator==)
    .def("__ne__", &OctobanBoard::operator!=)
  ;
}
