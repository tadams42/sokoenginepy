#include "sokoenginepyext.hpp"
#include <memory>

using namespace std;
using namespace sokoengine;

void export_boards(py::module &m) {
  py::class_<VariantBoard, std::shared_ptr<VariantBoard>>(m, "VariantBoard")
    .def_static(
      "instance_from",
      [](const py::object &tessellation_or_description, board_size_t board_width,
         board_size_t board_height, const py::object &board_str) -> py::object {
        py::extract<string> string_obj(tessellation_or_description);
        py::extract<const Tessellation &> tessellation_obj(tessellation_or_description);

        string description;
        if (string_obj.check()) {
          description = string_obj();
        } else if (tessellation_obj.check()) {
          const Tessellation &tessellation = tessellation_obj();
          description = tessellation.str();
        } else
          throw invalid_argument(string() +
                                 "tessellation_or_description can't be converted to " +
                                 "known tessellation type");

        shared_ptr<VariantBoard> retv;

        if (board_str.is_none()) {
          retv = VariantBoard::instance_from(description, board_width, board_height);
        } else {
          string board_str_converted = py::extract<string>(board_str)();
          retv = VariantBoard::instance_from(description, board_str_converted);
        }

        if (description == "sokoban")
          return py::cast<shared_ptr<SokobanBoard>>(
            dynamic_pointer_cast<SokobanBoard>(retv));
        else if (description == "trioban")
          return py::cast<shared_ptr<TriobanBoard>>(
            dynamic_pointer_cast<TriobanBoard>(retv));
        else if (description == "octoban")
          return py::cast<shared_ptr<OctobanBoard>>(
            dynamic_pointer_cast<OctobanBoard>(retv));
        else if (description == "hexoban")
          return py::cast<shared_ptr<HexobanBoard>>(
            dynamic_pointer_cast<HexobanBoard>(retv));
        throw invalid_argument("Don't know about tessellation: " + description);
      },
      py::arg("tessellation_or_description") = py::cast<string>("sokoban"),
      py::arg("board_width") = 0, py::arg("board_height") = 0,
      py::arg("board_str") = py::none())

    .def_static("is_board_string", &VariantBoard::is_board_string, py::arg("line"))

    .def_static("parse_board_string",
                [](const string &line) {
                  auto native_retv = VariantBoard::parse_board_string(line);
                  py::list retv;
                  for (auto str : native_retv)
                    retv.append(str);
                  return retv;
                },
                py::arg("line"))

    .def_property_readonly("graph", &VariantBoard::graph,
                           py::return_value_policy::reference_internal)

    .def_property_readonly("tessellation", &VariantBoard::tessellation,
                           py::return_value_policy::reference)

    // protocols
    .def("__getitem__",
         [](VariantBoard &self, position_t position) -> BoardCell & {
           return self.cell_at(position);
         },
         py::return_value_policy::reference_internal, py::arg("position"))

    .def("__setitem__",
         [](VariantBoard &self, position_t position, const BoardCell &board_cell) {
           self.cell_at(position) = board_cell;
         },
         py::arg("position"), py::arg("board_cell"))

    .def("__setitem__",
         [](VariantBoard &self, position_t position, char board_cell) {
           self.cell_at(position) = BoardCell(board_cell);
         },
         py::arg("position"), py::arg("board_cell"))

    .def("__contains__", &VariantBoard::contains, py::arg("position"))

    .def("__str__", &VariantBoard::str)
    .def("__repr__", &VariantBoard::repr)

    .def("to_str", &SokobanBoard::to_str, py::arg("use_visible_floor") = false,
         py::arg("rle_encode") = false)

    .def_property_readonly("width", &VariantBoard::width)
    .def_property_readonly("height", &VariantBoard::height)
    .def_property_readonly("size", &VariantBoard::size)

    .def("neighbor",
         [](const VariantBoard &self, position_t src,
            const Direction &direction) -> py::object {
           auto retv = self.neighbor_at(src, direction);
           if (retv > MAX_POS) return py::none();
           return py::cast(retv);
         },
         py::arg("src"), py::arg("direction"))

    .def("wall_neighbors", &VariantBoard::wall_neighbors, py::arg("src"))
    .def("all_neighbors", &VariantBoard::all_neighbors, py::arg("src"))
    .def("clear", &VariantBoard::clear)
    .def("mark_play_area", &VariantBoard::mark_play_area)
    .def("positions_reachable_by_pusher", &VariantBoard::positions_reachable_by_pusher,
         py::arg("pusher_position"), py::arg("excluded_positions") = py::list())
    .def("normalized_pusher_position", &VariantBoard::normalized_pusher_position,
         py::arg("pusher_position"), py::arg("excluded_positions") = py::list())
    .def("path_destination", &VariantBoard::path_destination, py::arg("src"), py::arg("directions"))
    .def("find_move_path", &VariantBoard::find_move_path, py::arg("src"), py::arg("dst"))
    .def("find_jump_path", &VariantBoard::find_jump_path, py::arg("src"), py::arg("dst"))
    .def("positions_path_to_directions_path",
         &VariantBoard::positions_path_to_directions_path, py::arg("positions"))
    .def("cell_orientation", &VariantBoard::cell_orientation, py::arg("position"))
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
    .def("resize", &VariantBoard::resize, py::arg("new_width"), py::arg("new_height"))
    .def("resize_and_center", &VariantBoard::resize_and_center, py::arg("new_width"), py::arg("new_height"))
    .def("trim", &VariantBoard::trim);

  py::class_<SokobanBoard, VariantBoard, std::shared_ptr<SokobanBoard>>(m,
                                                                        "SokobanBoard")
    .def(py::init([](board_size_t board_width, board_size_t board_height,
                     const py::object &board_str) {
           if (board_str.is_none())
             return make_unique<SokobanBoard>(board_width, board_height);
           string board_str_converted = board_str.cast<string>();
           return make_unique<SokobanBoard>(board_str_converted);
         }),
         py::arg("board_width") = 0, py::arg("board_height") = 0,
         py::arg("board_str") = py::none())

    // protocols
    .def("__eq__", &SokobanBoard::operator==)
    .def("__ne__", &SokobanBoard::operator!=);

  py::class_<HexobanBoard, VariantBoard, std::shared_ptr<HexobanBoard>>(m,
                                                                        "HexobanBoard")
    .def(py::init([](board_size_t board_width, board_size_t board_height,
                     const py::object &board_str) {
           if (board_str.is_none())
             return make_unique<HexobanBoard>(board_width, board_height);
           string board_str_converted = board_str.cast<string>();
           return make_unique<HexobanBoard>(board_str_converted);
         }),
         py::arg("board_width") = 0, py::arg("board_height") = 0,
         py::arg("board_str") = py::none())

    // protocols
    .def("__eq__", &HexobanBoard::operator==)
    .def("__ne__", &HexobanBoard::operator!=);

  py::class_<TriobanBoard, VariantBoard, std::shared_ptr<TriobanBoard>>(m,
                                                                        "TriobanBoard")
    .def(py::init([](board_size_t board_width, board_size_t board_height,
                     const py::object &board_str) {
           if (board_str.is_none())
             return make_unique<TriobanBoard>(board_width, board_height);
           string board_str_converted = board_str.cast<string>();
           return make_unique<TriobanBoard>(board_str_converted);
         }),
         py::arg("board_width") = 0, py::arg("board_height") = 0,
         py::arg("board_str") = py::none())

    // protocols
    .def("__eq__", &TriobanBoard::operator==)
    .def("__ne__", &TriobanBoard::operator!=);

  py::class_<OctobanBoard, VariantBoard, std::shared_ptr<OctobanBoard>>(m,
                                                                        "OctobanBoard")
    .def(py::init([](board_size_t board_width, board_size_t board_height,
                     const py::object &board_str) {
           if (board_str.is_none())
             return make_unique<OctobanBoard>(board_width, board_height);
           string board_str_converted = board_str.cast<string>();
           return make_unique<OctobanBoard>(board_str_converted);
         }),
         py::arg("board_width") = 0, py::arg("board_height") = 0,
         py::arg("board_str") = py::none())

    // protocols
    .def("__eq__", &OctobanBoard::operator==)
    .def("__ne__", &OctobanBoard::operator!=);
}
