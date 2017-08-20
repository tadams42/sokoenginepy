#include <boost/python.hpp>
#include <sokoengine.hpp>

using namespace boost::python;
using namespace sokoengine;

object neighbor_wraper(
  BoardGraph &board_graph, position_t from_position, Direction direction
) {
  position_t retv = board_graph.neighbor(from_position, direction);
  if (retv == NULL_POSITION) {
    return object();  // return None
  }
  return object(retv);
}

boost::python::list wall_neighbors_wrapper(
  BoardGraph &board_graph, position_t from_position
) {
  Positions retv = board_graph.wall_neighbors(from_position);
  return boost::python::list(retv);
}

boost::python::list all_neighbors_wrapper(
  BoardGraph &board_graph, position_t from_position
) {
  Positions retv = board_graph.all_neighbors(from_position);
  return boost::python::list(retv);
}

boost::python::list shortest_path_wrapper(
  BoardGraph &board_graph, position_t start_position, position_t end_position
) {
  Positions retv = board_graph.shortest_path(
    start_position, end_position
  );
  return boost::python::list(retv);
}

boost::python::list dijkstra_path_wrapper(
  BoardGraph &board_graph, position_t start_position, position_t end_position
) {
  Positions retv = board_graph.dijkstra_path(
    start_position, end_position
  );
  return boost::python::list(retv);
}

boost::python::list find_move_path_wrapper(
  BoardGraph &board_graph, position_t start_position, position_t end_position
) {
  Positions retv = board_graph.find_move_path(
    start_position, end_position
  );
  return boost::python::list(retv);
}

boost::python::list find_jump_path_wrapper(
  BoardGraph &board_graph, position_t start_position, position_t end_position
) {
  Positions retv = board_graph.find_jump_path(
    start_position, end_position
  );
  return boost::python::list(retv);
}

boost::python::list positions_path_to_directions_path_wrapper(
  BoardGraph &board_graph, const boost::python::list& positions_path
) {
  Positions positions_path_converted;

  for (size_t i = 0; i < len(positions_path); ++i) {
    positions_path_converted.push_back(
      boost::python::extract<position_t>(positions_path[i])
    );
  }

  Directions retv = board_graph.positions_path_to_directions_path(
    positions_path_converted
  );
  return boost::python::list(retv);
}

boost::python::list positions_reachable_by_pusher_wrapper2(
  BoardGraph &board_graph, position_t pusher_position,
  const boost::python::list& excluded_positions
) {
  Positions excluded_positions_converted;

  for (size_t i = 0; i < len(excluded_positions); ++i) {
    excluded_positions_converted.push_back(
      boost::python::extract<position_t>(excluded_positions[i])
    );
  }

  Positions retv = board_graph.positions_reachable_by_pusher(
    pusher_position, excluded_positions_converted
  );
  return boost::python::list(retv);
}

boost::python::list positions_reachable_by_pusher_wrapper0(
  BoardGraph &board_graph, position_t pusher_position,
  object excluded_positions = object()
) {
  return positions_reachable_by_pusher_wrapper2(
    board_graph, pusher_position, boost::python::list()
  );
}

boost::python::list positions_reachable_by_pusher_wrapper1(
  BoardGraph &board_graph, position_t pusher_position
) {
  return positions_reachable_by_pusher_wrapper2(
    board_graph, pusher_position, boost::python::list()
  );
}

position_t normalized_pusher_position_wrapper2(
  BoardGraph &board_graph, position_t pusher_position,
  const boost::python::list& excluded_positions
) {
  Positions excluded_positions_converted;

  for (size_t i = 0; i < len(excluded_positions); ++i) {
    excluded_positions_converted.push_back(
      boost::python::extract<position_t>(excluded_positions[i])
    );
  }

  return board_graph.normalized_pusher_position(
    pusher_position, excluded_positions_converted
  );
}

position_t normalized_pusher_position_wrapper0(
  BoardGraph &board_graph, position_t pusher_position,
  object excluded_positions = object()
) {
  return normalized_pusher_position_wrapper2(
    board_graph, pusher_position, boost::python::list()
  );
}

position_t normalized_pusher_position_wrapper1(
  BoardGraph &board_graph, position_t pusher_position
) {
  return normalized_pusher_position_wrapper2(
    board_graph, pusher_position, boost::python::list()
  );
}

position_t path_destination_wrapper(
  BoardGraph &board_graph, position_t start_position,
  const boost::python::list& directions_path
) {
  Directions directions_path_converted;

  for (size_t i = 0; i < len(directions_path); ++i) {
    directions_path_converted.push_back(
      boost::python::extract<Direction>(directions_path[i])
    );
  }

  return board_graph.path_destination(
    start_position, directions_path_converted
  );
}

BoardCell& get_cell_wrapper(BoardGraph &board_graph, position_t position) {
  return board_graph.cell_at(position);
}

void set_cell_wrapper(
  BoardGraph &board_graph, position_t position, const BoardCell& board_cell
) {
  board_graph.cell_at(position) = board_cell;
}

void export_board_graph() {
  object BoardGraph_class = class_<BoardGraph>(
      // class name
      "BoardGraph",
      // __init__
      init<optional<size_t, GraphType> >(args("number_of_vertices", "graph_type"))
    )

    .def(
      "__getitem__", &get_cell_wrapper, args("position"),
      return_internal_reference<>()
    )
    .def(
      "__setitem__", &set_cell_wrapper, args("position", "board_cell")
    )

    .def("__contains__", &BoardGraph::contains, args("position"))

    .def("vertices_count", &BoardGraph::vertices_count)
    .def("edges_count", &BoardGraph::edges_count)

    .def(
      "has_edge", &BoardGraph::has_edge,
      args("source_vertex", "target_vertex", "direction")
    )
    .def(
      "out_edges_count", &BoardGraph::out_edges_count,
      args("source_vertex", "target_vertex")
    )

    .def("remove_all_edges", &BoardGraph::remove_all_edges)

    .def(
      "add_edge", &BoardGraph::add_edge,
      args("source_vertex", "neighbor_vertex", "direction")
    )

    .def(
      "out_edge_weight", &BoardGraph::out_edge_weight, args("target_position")
    )

    .def("neighbor", &neighbor_wraper, args("from_position", "direction"))

    .def("wall_neighbors", &wall_neighbors_wrapper, args("from_position"))
    .def("all_neighbors", &all_neighbors_wrapper, args("from_position"))
    .def(
      "shortest_path", &shortest_path_wrapper,
      args("start_position", "end_position")
    )
    .def(
      "dijkstra_path", &dijkstra_path_wrapper,
      args("start_position", "end_position")
    )
    .def(
      "find_move_path", &find_move_path_wrapper,
      args("start_position", "end_position")
    )
    .def(
      "find_jump_path", &find_jump_path_wrapper,
      args("start_position", "end_position")
    )
    .def(
      "positions_path_to_directions_path",
      &positions_path_to_directions_path_wrapper,
      args("positions_path")
    )
    .def("mark_play_area", &BoardGraph::mark_play_area)
    .def(
      "positions_reachable_by_pusher", &positions_reachable_by_pusher_wrapper1,
      args("pusher_position")
    )
    .def(
      "positions_reachable_by_pusher", &positions_reachable_by_pusher_wrapper0,
      args("pusher_position", "excluded_positions")
    )
    .def(
      "positions_reachable_by_pusher", &positions_reachable_by_pusher_wrapper2,
      args("pusher_position", "excluded_positions")
    )
    .def(
      "normalized_pusher_position",
      &normalized_pusher_position_wrapper1,
      args("pusher_position")
    )
    .def(
      "normalized_pusher_position",
      &normalized_pusher_position_wrapper0,
      args("pusher_position", "excluded_positions")
    )
    .def(
      "normalized_pusher_position",
      &normalized_pusher_position_wrapper2,
      args("pusher_position", "excluded_positions")
    )
    .def(
      "path_destination", &path_destination_wrapper,
      args("start_position", "directions_path")
    )
  ;

  BoardGraph_class.attr("_MAX_EDGE_WEIGHT") = BoardGraph::_MAX_EDGE_WEIGHT;
}
