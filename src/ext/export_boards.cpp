#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <sokoengine.hpp>

using namespace boost::python;
using namespace sokoengine;
using namespace std;

object neighbor_wraper(
  VariantBoard& board, position_t from_position, Direction direction
) {
  position_t retv = board.neighbor_at(from_position, direction);
  if (retv == NULL_POSITION) {
    return object();  // return None
  }
  return object(retv);
}

BoardCell& get_cell_wrapper(VariantBoard& board, position_t position) {
  return board.cell_at(position);
}

void set_cell_wrapper1(
  VariantBoard& board, position_t position, const BoardCell& board_cell
) {
  board.cell_at(position) = board_cell;
}

void set_cell_wrapper2(
  VariantBoard& board, position_t position, char board_cell
) {
  board.cell_at(position) = BoardCell(board_cell);
}

boost::python::list wall_neighbors_wrapper(
  VariantBoard& board, position_t from_position
) {
  Positions retv = board.wall_neighbors(from_position);
  return boost::python::list(retv);
}

boost::python::list all_neighbors_wrapper(
  VariantBoard& board, position_t from_position
) {
  Positions retv = board.all_neighbors(from_position);
  return boost::python::list(retv);
}

boost::python::list positions_reachable_by_pusher_wrapper(
  VariantBoard& board, position_t pusher_position,
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
    return boost::python::list(board.positions_reachable_by_pusher(
      pusher_position, excluded_positions_converted
    ));
  } else {
    return boost::python::list(
      board.positions_reachable_by_pusher(pusher_position
    ));
  }
}

boost::python::list find_move_path_wrapper(
  VariantBoard& board, position_t start_position, position_t end_position
) {
  Positions retv = board.find_move_path(
    start_position, end_position
  );
  return boost::python::list(retv);
}

boost::python::list find_jump_path_wrapper(
  VariantBoard& board, position_t start_position, position_t end_position
) {
  Positions retv = board.find_jump_path(
    start_position, end_position
  );
  return boost::python::list(retv);
}

position_t normalized_pusher_position_wrapper(
  VariantBoard& board, position_t pusher_position,
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
    return board.normalized_pusher_position(
      pusher_position, excluded_positions_converted
    );
  } else {
    return board.normalized_pusher_position(pusher_position);
  }
}

position_t path_destination_wrapper(
  VariantBoard& board, position_t start_position,
  const boost::python::list& directions_path
) {
  Directions directions_path_converted;

  for (size_t i = 0; i < len(directions_path); ++i) {
    directions_path_converted.push_back(
      boost::python::extract<Direction>(directions_path[i])
    );
  }

  return board.path_destination(
    start_position, directions_path_converted
  );
}

boost::python::list parse_board_string_wrapper(const std::string& the_line) {
  StringList retv = VariantBoard::parse_board_string(the_line);
  return boost::python::list(retv);
}

boost::python::list positions_path_to_directions_path_wrapper(
  VariantBoard& board, const boost::python::list& positions_path
) {
  Positions positions_path_converted;

  for (size_t i = 0; i < len(positions_path); ++i) {
    positions_path_converted.push_back(
      boost::python::extract<position_t>(positions_path[i])
    );
  }

  Directions retv = board.positions_path_to_directions_path(
    positions_path_converted
  );
  return boost::python::list(retv);
}

shared_ptr<SokobanBoard> SokobanBoard_init(
  size_t board_width, size_t board_height, const object& board_str
) {
  string board_str_converted;
  if (!board_str.is_none()) {
    board_str_converted = extract<string>(board_str);
    return make_shared<SokobanBoard>(board_str_converted);
  } else {
    return make_shared<SokobanBoard>(board_width, board_height);
  }
}

shared_ptr<HexobanBoard> HexobanBoard_init(
  size_t board_width, size_t board_height, const object& board_str
) {
  string board_str_converted;
  if (!board_str.is_none()) {
    board_str_converted = extract<string>(board_str);
    return make_shared<HexobanBoard>(board_str_converted);
  } else {
    return make_shared<HexobanBoard>(board_width, board_height);
  }
}

shared_ptr<TriobanBoard> TriobanBoard_init(
  size_t board_width, size_t board_height, const object& board_str
) {
  string board_str_converted;
  if (!board_str.is_none()) {
    board_str_converted = extract<string>(board_str);
    return make_shared<TriobanBoard>(board_str_converted);
  } else {
    return make_shared<TriobanBoard>(board_width, board_height);
  }
}

shared_ptr<OctobanBoard> OctobanBoard_init(
  size_t board_width, size_t board_height, const object& board_str
) {
  string board_str_converted;
  if (!board_str.is_none()) {
    board_str_converted = extract<string>(board_str);
    return make_shared<OctobanBoard>(board_str_converted);
  } else {
    return make_shared<OctobanBoard>(board_width, board_height);
  }
}

object instance_from_wrapper(
  const object& tessellation_or_description, size_t board_width,
  size_t board_height, const object& board_str
) {
  shared_ptr<VariantBoard> retv;

  extract<string> string_obj(tessellation_or_description);
  extract<const TessellationBase&> tessellation_obj(tessellation_or_description);

  if (string_obj.check()) {
    string description = string_obj;
    if (!board_str.is_none()) {
      string board_str_converted = extract<string>(board_str);
      retv = std::move(
        VariantBoard::instance_from(description, board_str_converted)
      );
    } else {
      retv = std::move(
        VariantBoard::instance_from(description, board_width, board_height)
      );
    }
    if (description == "sokoban")
      return object(dynamic_pointer_cast<SokobanBoard>(retv));
    else if (description == "trioban")
      return object(dynamic_pointer_cast<TriobanBoard>(retv));
    else if (description == "octoban")
      return object(dynamic_pointer_cast<OctobanBoard>(retv));
    else if (description == "hexoban")
      return object(dynamic_pointer_cast<HexobanBoard>(retv));
    else throw UnknownTessellationError(
      "Don't know about tessellation: " + description
    );
  } else if (tessellation_obj.check()) {
    const TessellationBase& tessellation = tessellation_obj;
    if (!board_str.is_none()) {
      string board_str_converted = extract<string>(board_str);
      retv = std::move(
        VariantBoard::instance_from(tessellation, board_str_converted)
      );
    } else {
      retv = std::move(
        VariantBoard::instance_from(tessellation, board_width, board_height)
      );
    }
    if (tessellation.str() == "sokoban")
      return object(dynamic_pointer_cast<SokobanBoard>(retv));
    else if (tessellation.str() == "trioban")
      return object(dynamic_pointer_cast<TriobanBoard>(retv));
    else if (tessellation.str() == "octoban")
      return object(dynamic_pointer_cast<OctobanBoard>(retv));
    else if (tessellation.str() == "hexoban")
      return object(dynamic_pointer_cast<HexobanBoard>(retv));
    else throw UnknownTessellationError(
      "Don't know about tessellation: " + tessellation.str()
    );
  } else throw UnknownTessellationError(
    string() + "tessellation_or_description can't be converted to known " +
    "tessellation type"
  );

  return object();
}

void export_boards() {
  class_<StringList>("StringList").def(vector_indexing_suite<StringList>());

  class_<VariantBoard , boost::noncopyable>("VariantBoard", no_init)
    // @classmethod
    .def(
      "instance_from", &instance_from_wrapper,
      (
        boost::python::arg("tessellation_or_description"),
        boost::python::arg("board_width")=0,
        boost::python::arg("board_height")=0,
        boost::python::arg("board_str")=object()
      )
    ).staticmethod("instance_from")
    .def(
      "is_board_string", &VariantBoard::is_board_string,
      (boost::python::arg("line"))
    ).staticmethod("is_board_string")
    .def(
      "parse_board_string", &parse_board_string_wrapper,
      (boost::python::arg("line"))
    ).staticmethod("parse_board_string")

    .add_property(
      "_graph", make_function(
        &VariantBoard::graph, return_internal_reference<>()
      )
    )
    .add_property(
      "tessellation", make_function(
        &VariantBoard::tessellation, return_internal_reference<>()
      )
    )

    // protocols
    .def(
      "__getitem__", &get_cell_wrapper, (boost::python::arg("position")),
      return_internal_reference<>()
    )
    .def(
      "__setitem__", &set_cell_wrapper1,
      (
        boost::python::arg("position"),
        boost::python::arg("board_cell")
      )
    )
    .def(
      "__setitem__", &set_cell_wrapper2,
      (
        boost::python::arg("position"),
        boost::python::arg("board_cell")
      )
    )
    .def(
      "__contains__", &VariantBoard::contains,
      (boost::python::arg("position"))
    )
    .def("__str__", &VariantBoard::str)
    .def("__repr__", &VariantBoard::repr)
    .def(
      "to_str", &SokobanBoard::to_str,
      (
        boost::python::arg("use_visible_floor")=false,
        boost::python::arg("rle_encode")=false
      )
    )

    .add_property("width", &VariantBoard::width)
    .add_property("height", &VariantBoard::height)
    .add_property("size", &VariantBoard::size)

    .def(
      "neighbor", &neighbor_wraper,
      (
        boost::python::arg("from_position"),
        boost::python::arg("direction")
      )
    )

    .def(
      "wall_neighbors", &wall_neighbors_wrapper,
      (boost::python::arg("from_position"))
    )
    .def(
      "all_neighbors", &all_neighbors_wrapper,
      (boost::python::arg("from_position"))
    )
    .def("clear", &VariantBoard::clear)
    .def("mark_play_area", &VariantBoard::mark_play_area)
    .def(
      "positions_reachable_by_pusher",
      &positions_reachable_by_pusher_wrapper,
      (boost::python::arg("pusher_position"), boost::python::arg("excluded_positions")=object())
    )
    .def(
      "normalized_pusher_position",
      &normalized_pusher_position_wrapper,
      (boost::python::arg("pusher_position"), boost::python::arg("excluded_positions")=object())
    )
    .def(
      "path_destination", &path_destination_wrapper,
      (boost::python::arg("start_position"), boost::python::arg("directions_path"))
    )
    .def(
      "find_move_path", &find_move_path_wrapper,
      (boost::python::arg("start_position"), boost::python::arg("end_position"))
    )
    .def(
      "find_jump_path", &find_jump_path_wrapper,
      (boost::python::arg("start_position"), boost::python::arg("end_position"))
    )
    .def(
      "positions_path_to_directions_path",
      &positions_path_to_directions_path_wrapper,
      (boost::python::arg("positions_path"))
    )
    .def(
      "cell_orientation", &VariantBoard::cell_orientation,
      (boost::python::arg("position"))
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
      (
        boost::python::arg("new_width"), boost::python::arg("new_height")
      )
    )
    .def(
      "resize_and_center", &VariantBoard::resize_and_center,
      (
        boost::python::arg("new_width"), boost::python::arg("new_height")
      )
    )
    .def("trim", &VariantBoard::trim)
  ;

  class_<SokobanBoard, bases<VariantBoard> >("SokobanBoard")
    .def("__init__", make_constructor(
      SokobanBoard_init,
      default_call_policies(),
      (
        boost::python::arg("board_width")=0,
        boost::python::arg("board_height")=0,
        boost::python::arg("board_str")=object()
      )
    ))

    // protocols
    .def("__eq__", &SokobanBoard::operator==)
    .def("__ne__", &SokobanBoard::operator!=)
  ;

  class_<HexobanBoard, bases<VariantBoard> >("HexobanBoard")
    .def("__init__", make_constructor(
      HexobanBoard_init,
      default_call_policies(),
      (
        boost::python::arg("board_width")=0,
        boost::python::arg("board_height")=0,
        boost::python::arg("board_str")=object()
      )
    ))

    // protocols
    .def("__eq__", &HexobanBoard::operator==)
    .def("__ne__", &HexobanBoard::operator!=)
  ;

  class_<TriobanBoard, bases<VariantBoard> >("TriobanBoard")
    .def("__init__", make_constructor(
      TriobanBoard_init,
      default_call_policies(),
      (
        boost::python::arg("board_width")=0,
        boost::python::arg("board_height")=0,
        boost::python::arg("board_str")=object()
      )
    ))

    // protocols
    .def("__eq__", &TriobanBoard::operator==)
    .def("__ne__", &TriobanBoard::operator!=)
  ;

  class_<OctobanBoard, bases<VariantBoard> >("OctobanBoard")
    .def("__init__", make_constructor(
      OctobanBoard_init,
      default_call_policies(),
      (
        boost::python::arg("board_width")=0,
        boost::python::arg("board_height")=0,
        boost::python::arg("board_str")=object()
      )
    ))

    // protocols
    .def("__eq__", &OctobanBoard::operator==)
    .def("__ne__", &OctobanBoard::operator!=)
  ;
}
