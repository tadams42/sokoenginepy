#include <pybind11/pybind11.h>
#include <sokoengine.hpp>

using namespace std;
namespace py = pybind11;
using namespace sokoengine;

void export_board_graph(py::module& m) {
  py::enum_<GraphType>(m, "GraphType")
    .value("DIRECTED", GraphType::DIRECTED)
    .value("DIRECTED_MULTI", GraphType::DIRECTED_MULTI)
    // We don't want constants be available in module scope
    // .export_values()
  ;

  py::class_<BoardGraph>(m, "BoardGraph")

    .def(
      py::init<size_t, GraphType>(),
      py::arg("number_of_vertices")=0,
      py::arg("graph_type")=GraphType::DIRECTED
    )

    .def(
      "__getitem__", [](BoardGraph& self, position_t position) -> BoardCell& {
        return self.cell_at(position);
      },
      py::return_value_policy::reference_internal,
      py::arg("position")
    )

    .def(
      "__setitem__", [](
        BoardGraph& self, position_t position, const BoardCell& board_cell
      ) {
        self.cell_at(position) = board_cell;
      },
      py::arg("position"), py::arg("board_cell")
    )

    .def(
      "__setitem__", [](
        BoardGraph& self, position_t position, char board_cell
      ) {
        self.cell_at(position) = BoardCell(board_cell);
      },
      py::arg("position"), py::arg("board_cell")
    )

    .def("__contains__", &BoardGraph::contains, py::arg("position"))

    .def_property_readonly("vertices_count", &BoardGraph::vertices_count)
    .def_property_readonly("edges_count", &BoardGraph::edges_count)

    .def(
      "has_edge", &BoardGraph::has_edge,
      py::arg("source_vertex"), py::arg("target_vertex"), py::arg("direction")
    )

    .def(
      "out_edges_count", &BoardGraph::out_edges_count,
      py::arg("source_vertex"), py::arg("target_vertex")
    )

    .def("remove_all_edges", &BoardGraph::remove_all_edges)

    .def(
      "add_edge", &BoardGraph::add_edge,
      py::arg("source_vertex"), py::arg("neighbor_vertex"), py::arg("direction")
    )

    .def(
      "out_edge_weight", &BoardGraph::out_edge_weight,
      py::arg("target_position")
    )

    .def("neighbor", [](
        const BoardGraph& self, position_t from_position,
        const Direction& direction
      ) -> py::object {
        position_t retv = self.neighbor_at(from_position, direction);
        if (retv == NULL_POSITION) return py::none();
        else return py::cast(retv);
      },
      py::arg("from_position"), py::arg("direction")
    )

    .def(
      "wall_neighbors", [](
        const BoardGraph& self, position_t from_position
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
        const BoardGraph& self, position_t from_position
      ) {
        auto native_retv = self.all_neighbors(from_position);
        py::list retv;
        for(auto val : native_retv) retv.append(py::cast(val));
        return retv;
      },
      py::arg("from_position")
    )

    .def(
      "shortest_path", [](
        const BoardGraph& self, position_t start_position,
        position_t end_position
      ) {
        auto native_retv = self.shortest_path(start_position, end_position);
        py::list retv;
        for(auto val : native_retv) retv.append(py::cast(val));
        return retv;
      },
      py::arg("start_position"), py::arg("end_position")
    )

    .def(
      "dijkstra_path", [](
        const BoardGraph& self, position_t start_position,
        position_t end_position
      ) {
        auto native_retv = self.dijkstra_path(start_position, end_position);
        py::list retv;
        for(auto val : native_retv) retv.append(py::cast(val));
        return retv;
      },
      py::arg("start_position"), py::arg("end_position")
    )

    .def(
      "find_move_path", [](
        const BoardGraph& self, position_t start_position,
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
        const BoardGraph& self, position_t start_position,
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
        const BoardGraph& self, const py::list& positions_path
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

    .def("mark_play_area", &BoardGraph::mark_play_area)

    .def(
      "positions_reachable_by_pusher", [](
        const BoardGraph& self, position_t pusher_position,
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
        const BoardGraph& self, position_t pusher_position,
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
        const BoardGraph& self, position_t start_position,
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

    .def_property_readonly_static(
      "_MAX_EDGE_WEIGHT", [](const py::object&) {
        return BoardGraph::_MAX_EDGE_WEIGHT;
      }
    )
  ;
}
