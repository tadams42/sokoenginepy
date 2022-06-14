#include "sokoenginepyext.hpp"

using namespace std;
using sokoengine::position_t;
using sokoengine::game::BoardCell;
using sokoengine::game::BoardGraph;
using sokoengine::game::Config;
using sokoengine::game::Direction;
using sokoengine::game::GraphType;
using sokoengine::io::Puzzle;

void export_board_graph(py::module &m) {
  py::enum_<GraphType>(m, "GraphType")
    .value("DIRECTED", GraphType::DIRECTED)
    .value("DIRECTED_MULTI", GraphType::DIRECTED_MULTI)
    // We don't want constants be available in module scope
    // .export_values()
    ;

  py::class_<Config>(m, "Config")
    .def_readonly_static("MAX_WIDTH", &Config::MAX_WIDTH)
    .def_readonly_static("MAX_HEIGHT", &Config::MAX_HEIGHT)
    .def_readonly_static("MAX_POS", &Config::MAX_POS)
    .def_readonly_static("DEFAULT_PIECE_ID", &Config::DEFAULT_PIECE_ID)
    .def_readonly_static("NULL_ID", &Config::NULL_ID);

  py::class_<BoardGraph>(m, "BoardGraph")
    .def(py::init<const Puzzle &>(), py::arg("puzzle"))

    .def(
      "__getitem__",
      [](BoardGraph &self, position_t position) -> BoardCell & {
        return self.cell_at(position);
      },
      py::return_value_policy::reference_internal, py::arg("position"))

    .def(
      "__setitem__",
      [](BoardGraph &self, position_t position, const BoardCell &board_cell) {
        self.cell_at(position) = board_cell;
      },
      py::arg("position"), py::arg("board_cell"))

    .def(
      "__setitem__",
      [](BoardGraph &self, position_t position, char board_cell) {
        self.cell_at(position) = BoardCell(board_cell);
      },
      py::arg("position"), py::arg("board_cell"))

    .def(
      "__contains__",
      [](BoardGraph &self, const py::object &position) -> bool {
        return self.contains(py::receive_position(position));
      },
      py::arg("position"))

    .def("__str__", &BoardGraph::str)

    .def_property_readonly("vertices_count", &BoardGraph::vertices_count)
    .def_property_readonly("size", &BoardGraph::size)
    .def_property_readonly("edges_count", &BoardGraph::edges_count)
    .def_property_readonly("board_width", &BoardGraph::board_width)
    .def_property_readonly("board_height", &BoardGraph::board_height)
    .def_property_readonly("tessellation", &BoardGraph::tessellation)

    .def("to_board_str", &BoardGraph::to_board_str,
         py::arg("use_visible_floor") = false, py::arg("rle_encode") = false)

    .def(
      "has_edge",
      [](BoardGraph &self, const py::object &src, const py::object &dst,
         const Direction &direction) {
        return self.has_edge(py::receive_position(src), py::receive_position(dst),
                             direction);
      },
      py::arg("src"), py::arg("dst"), py::arg("direction"))
    .def(
      "out_edges_count",
      [](BoardGraph &self, const py::object &src, const py::object &dst) {
        return self.out_edges_count(py::receive_position(src),
                                    py::receive_position(dst));
      },
      py::arg("src"), py::arg("dst"))
    .def("remove_all_edges", &BoardGraph::remove_all_edges)
    .def("add_edge", &BoardGraph::add_edge, py::arg("src"), py::arg("neighbor"),
         py::arg("direction"))
    .def("out_edge_weight", &BoardGraph::out_edge_weight, py::arg("target_position"))

    .def(
      "neighbor",
      [](const BoardGraph &self, position_t from_position,
         const Direction &direction) -> py::object {
        position_t retv = self.neighbor_at(from_position, direction);
        if (retv > Config::MAX_POS) return py::none();
        return py::cast(retv);
      },
      py::arg("src"), py::arg("direction"))

    .def("wall_neighbors", &BoardGraph::wall_neighbors, py::arg("src"))
    .def("all_neighbors", &BoardGraph::all_neighbors, py::arg("src"))
    .def("shortest_path", &BoardGraph::shortest_path, py::arg("src"), py::arg("dst"))
    .def("dijkstra_path", &BoardGraph::dijkstra_path, py::arg("src"), py::arg("dst"))
    .def("find_move_path", &BoardGraph::find_move_path, py::arg("src"), py::arg("dst"))
    .def("find_jump_path", &BoardGraph::find_jump_path, py::arg("src"), py::arg("dst"))
    .def("positions_path_to_directions_path",
         &BoardGraph::positions_path_to_directions_path, py::arg("positions"))
    .def("mark_play_area", &BoardGraph::mark_play_area)
    .def("positions_reachable_by_pusher", &BoardGraph::positions_reachable_by_pusher,
         py::arg("pusher_position"), py::arg("excluded_positions") = py::list())
    .def("normalized_pusher_position", &BoardGraph::normalized_pusher_position,
         py::arg("pusher_position"), py::arg("excluded_positions") = py::list())
    .def("path_destination", &BoardGraph::path_destination, py::arg("src"),
         py::arg("directions"))
    .def("reconfigure_edges", &BoardGraph::reconfigure_edges);
}
