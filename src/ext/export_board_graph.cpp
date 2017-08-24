#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <sokoengine.hpp>

using namespace boost::python;
using namespace sokoengine;

object neighbor_wraper(
  BoardGraph &board_graph, position_t from_position, Direction direction
) {
  position_t retv = board_graph.neighbor_at(from_position, direction);
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

boost::python::list positions_reachable_by_pusher_wrapper(
  BoardGraph &board_graph, position_t pusher_position,
  const object& excluded_positions = object()
) {
  if (!excluded_positions.is_none()) {
    Positions excluded_positions_converted;
    auto length = len(excluded_positions);
    for (size_t i = 0; i < length; ++i) {
      excluded_positions_converted.push_back(
        boost::python::extract<position_t>(excluded_positions[i])
      );
    }
    return boost::python::list(board_graph.positions_reachable_by_pusher(
      pusher_position, excluded_positions_converted
    ));
  } else {
    return boost::python::list(
      board_graph.positions_reachable_by_pusher(pusher_position
    ));
  }
}

position_t normalized_pusher_position_wrapper(
  BoardGraph &board_graph, position_t pusher_position,
  const object& excluded_positions = object()
) {
  if (!excluded_positions.is_none()) {
    Positions excluded_positions_converted;
    auto length = len(excluded_positions);
    for (size_t i = 0; i < length; ++i) {
      excluded_positions_converted.push_back(
        boost::python::extract<position_t>(excluded_positions[i])
      );
    }
    return board_graph.normalized_pusher_position(
      pusher_position, excluded_positions_converted
    );
  } else {
    return board_graph.normalized_pusher_position(pusher_position);
  }
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
  class_<Positions>("Positions").def(vector_indexing_suite<Positions>());

  class_<Directions>("Directions").def(vector_indexing_suite<Directions>());

  enum_<GraphType>("GraphType")
    .value("DIRECTED", GraphType::DIRECTED)
    .value("DIRECTED_MULTI", GraphType::DIRECTED_MULTI)
    // We don't want constants be available in module scope
    // .export_values()
  ;

  object BoardGraph_class = class_<BoardGraph>(
      // class name
      "BoardGraph",
      // __init__
      init<optional<size_t, GraphType> >((
        arg("number_of_vertices"), arg("graph_type")
      ))
    )

    .def(
      "__getitem__", &get_cell_wrapper, (arg("position")),
      return_internal_reference<>()
    )
    .def(
      "__setitem__", &set_cell_wrapper, (arg("position"), arg("board_cell"))
    )

    .def("__contains__", &BoardGraph::contains, (arg("position")))

    .add_property("vertices_count", &BoardGraph::vertices_count)
    .add_property("edges_count", &BoardGraph::edges_count)

    .def(
      "has_edge", &BoardGraph::has_edge,
      (arg("source_vertex"), arg("target_vertex"), arg("direction"))
    )
    .def(
      "out_edges_count", &BoardGraph::out_edges_count,
      (arg("source_vertex"), arg("target_vertex"))
    )

    .def("remove_all_edges", &BoardGraph::remove_all_edges)

    .def(
      "add_edge", &BoardGraph::add_edge,
      (arg("source_vertex"), arg("neighbor_vertex"), arg("direction"))
    )

    .def(
      "out_edge_weight", &BoardGraph::out_edge_weight, (arg("target_position"))
    )

    .def("neighbor", &neighbor_wraper, (arg("from_position"), arg("direction")))

    .def("wall_neighbors", &wall_neighbors_wrapper, (arg("from_position")))
    .def("all_neighbors", &all_neighbors_wrapper, (arg("from_position")))
    .def(
      "shortest_path", &shortest_path_wrapper,
      (arg("start_position"), arg("end_position"))
    )
    .def(
      "dijkstra_path", &dijkstra_path_wrapper,
      (arg("start_position"), arg("end_position"))
    )
    .def(
      "find_move_path", &find_move_path_wrapper,
      (arg("start_position"), arg("end_position"))
    )
    .def(
      "find_jump_path", &find_jump_path_wrapper,
      (arg("start_position"), arg("end_position"))
    )
    .def(
      "positions_path_to_directions_path",
      &positions_path_to_directions_path_wrapper,
      (arg("positions_path"))
    )
    .def("mark_play_area", &BoardGraph::mark_play_area)
    .def(
      "positions_reachable_by_pusher",
      &positions_reachable_by_pusher_wrapper,
      (arg("pusher_position"), arg("excluded_positions")=object())
    )

    .def(
      "normalized_pusher_position",
      &normalized_pusher_position_wrapper,
      (arg("pusher_position"), arg("excluded_positions")=object())
    )

    .def(
      "path_destination", &path_destination_wrapper,
      (arg("start_position"), arg("directions_path"))
    )
  ;

  BoardGraph_class.attr("_MAX_EDGE_WEIGHT") = BoardGraph::_MAX_EDGE_WEIGHT;
}
