#include "sokoenginepyext.hpp"

using sokoengine::position_t;
using sokoengine::game::BoardCell;
using sokoengine::game::BoardGraph;
using sokoengine::game::Config;
using sokoengine::game::Direction;
using sokoengine::game::Directions;
using sokoengine::game::Edge;
using sokoengine::game::Edges;
using sokoengine::game::GraphType;
using sokoengine::game::Positions;
using sokoengine::io::Puzzle;

void export_board_graph(py::module &m) {
  py::enum_<GraphType>(m, "GraphType")
    .value("DIRECTED", GraphType::DIRECTED)
    .value("DIRECTED_MULTI", GraphType::DIRECTED_MULTI);

  py::class_<Config>(m, "Config")
    .def_readonly_static("MAX_WIDTH", &Config::MAX_WIDTH)
    .def_readonly_static("MAX_HEIGHT", &Config::MAX_HEIGHT)
    .def_readonly_static("DEFAULT_ID", &Config::DEFAULT_ID)
    .def_readonly_static("NO_ID", &Config::NO_ID)
    .def_readonly_static("NO_POS", &Config::NO_POS);

  py::class_<Edge>(m, "Edge")
    .def(
      py::init<position_t, position_t, Direction>(),
      py::arg("u"),
      py::arg("v"),
      py::arg("direction")
    )

    .def("__str__", &Edge::str)
    .def("__repr__", &Edge::repr)
    .def("__eq__", &Edge::operator==)
    .def("__ne__", &Edge::operator!=)

    .def_property(
      "u",
      [](const Edge &self) {
        return self.u;
      },
      [](Edge &self, position_t rv) {
        self.u = rv;
      }
    )
    .def_property(
      "v",
      [](const Edge &self) {
        return self.v;
      },
      [](Edge &self, position_t rv) {
        self.v = rv;
      }
    )
    .def_property(
      "direction",
      [](const Edge &self) {
        return self.direction;
      },
      [](Edge &self, Direction rv) {
        self.direction = rv;
      }
    );

  py::class_<BoardGraph>(m, "BoardGraph")
    .def(py::init<const Puzzle &>(), py::arg("puzzle"))

    .def(
      "__getitem__",
      [](BoardGraph &self, py_int_t position) -> BoardCell & {
        return self.cell_at(position_or_throw(position));
      },
      py::return_value_policy::reference_internal,
      py::arg("position")
    )

    .def(
      "__setitem__",
      [](BoardGraph &self, py_int_t position, const BoardCell &board_cell) {
        self.cell_at(position_or_throw(position)) = board_cell;
      },
      py::arg("position"),
      py::arg("board_cell")
    )

    .def(
      "__setitem__",
      [](BoardGraph &self, py_int_t position, char board_cell) {
        self.cell_at(position_or_throw(position)) = BoardCell(board_cell);
      },
      py::arg("position"),
      py::arg("board_cell")
    )

    .def(
      "__contains__",
      [](const BoardGraph &self, py_int_t position) {
        if (position < 0 || position >= std::numeric_limits<sokoengine::position_t>::max())
          return false;
        return self.contains(static_cast<position_t>(position));
      },
      py::arg("position")
    )

    .def("__str__", &BoardGraph::str)

    .def_property_readonly("size", &BoardGraph::size)
    .def_property_readonly("edges_count", &BoardGraph::edges_count)
    .def_property_readonly("board_width", &BoardGraph::board_width)
    .def_property_readonly("board_height", &BoardGraph::board_height)
    .def_property_readonly("tessellation", &BoardGraph::tessellation)

    .def(
      "cell_orientation",
      [](const BoardGraph &self, py_int_t position) {
        return self.cell_orientation(position_or_throw(position));
      },
      py::arg("position")
    )

    .def(
      "out_edges",
      [](const BoardGraph &self, py_int_t src) {
        return self.out_edges(position_or_throw(src));
      },
      py::arg("src")
    )

    // .def("unsafe", [](const BoardGraph &self, position_t pos,
    //                   const Direction &d) { return self.neighbor(pos, d); })

    .def(
      "to_board_str",
      &BoardGraph::to_board_str,
      py::arg("use_visible_floor") = false,
      py::arg("rle_encode")        = false
    )

    .def(
      "neighbor",
      [](const BoardGraph &self, py_int_t src, const Direction &direction) {
        return self.neighbor_at(position_or_throw(src), direction);
      },
      py::arg("src"),
      py::arg("direction")
    )

    .def(
      "wall_neighbors",
      [](const BoardGraph &self, py_int_t src) {
        return self.wall_neighbors(position_or_throw(src));
      },
      py::arg("src")
    )

    .def(
      "wall_neighbor_directions",
      [](const BoardGraph &self, py_int_t src) {
        return self.wall_neighbor_directions(position_or_throw(src));
      },
      py::arg("src")
    )

    .def(
      "all_neighbors",
      [](const BoardGraph &self, py_int_t src) {
        return self.all_neighbors(position_or_throw(src));
      },
      py::arg("src")
    )

    .def(
      "shortest_path",
      [](const BoardGraph &self, py_int_t src, py_int_t dst) {
        return self.shortest_path(position_or_throw(src), position_or_throw(dst));
      },
      py::arg("src"),
      py::arg("dst")
    )

    .def(
      "dijkstra_path",
      [](const BoardGraph &self, py_int_t src, py_int_t dst) {
        return self.dijkstra_path(position_or_throw(src), position_or_throw(dst));
      },
      py::arg("src"),
      py::arg("dst")
    )

    .def(
      "find_move_path",
      [](const BoardGraph &self, py_int_t src, py_int_t dst) {
        return self.find_move_path(position_or_throw(src), position_or_throw(dst));
      },
      py::arg("src"),
      py::arg("dst")
    )

    .def(
      "find_jump_path",
      [](const BoardGraph &self, py_int_t src, py_int_t dst) {
        return self.find_jump_path(position_or_throw(src), position_or_throw(dst));
      },
      py::arg("src"),
      py::arg("dst")
    )

    .def(
      "positions_path_to_directions_path",
      [](const BoardGraph &self, const py_int_vect_t &positions) {
        return self.positions_path_to_directions_path(positions_or_throw(positions));
      },
      py::arg("positions")
    )

    .def("mark_play_area", &BoardGraph::mark_play_area)

    .def(
      "positions_reachable_by_pusher",
      [](
        const BoardGraph    &self,
        py_int_t             pusher_position,
        const py_int_vect_t &excluded_positions
      ) {
        return self.positions_reachable_by_pusher(
          position_or_throw(pusher_position), positions_no_throw(excluded_positions)
        );
      },
      py::arg("pusher_position"),
      py::arg("excluded_positions") = py_int_vect_t()
    )

    .def(
      "normalized_pusher_position",
      [](
        const BoardGraph    &self,
        py_int_t             pusher_position,
        const py_int_vect_t &excluded_positions
      ) {
        return self.normalized_pusher_position(
          position_or_throw(pusher_position), positions_no_throw(excluded_positions)
        );
      },
      py::arg("pusher_position"),
      py::arg("excluded_positions") = py_int_vect_t()
    )

    .def(
      "path_destination",
      [](const BoardGraph &self, py_int_t src, const Directions &directions) {
        return self.path_destination(position_or_throw(src), directions);
      },
      py::arg("src"),
      py::arg("directions")
    );
}
