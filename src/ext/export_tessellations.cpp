#include <boost/python.hpp>
#include <sokoengine.hpp>

using namespace boost::python;
using namespace sokoengine;


object sokoban_neighbor_position_wraper(
  SokobanTessellation& tessellation, position_t position,
  const Direction& direction, size_t board_width, size_t board_height
) {
  position_t retv = tessellation.neighbor_position(
    position, direction, board_width, board_height
  );
  if (retv == NULL_POSITION) {
    return object();  // return None
  }
  return object(retv);
}

object trioban_neighbor_position_wraper(
  TriobanTessellation& tessellation, position_t position,
  const Direction& direction, size_t board_width, size_t board_height
) {
  position_t retv = tessellation.neighbor_position(
    position, direction, board_width, board_height
  );
  if (retv == NULL_POSITION) {
    return object();  // return None
  }
  return object(retv);
}

object octoban_neighbor_position_wraper(
  OctobanTessellation& tessellation, position_t position,
  const Direction& direction, size_t board_width, size_t board_height
) {
  position_t retv = tessellation.neighbor_position(
    position, direction, board_width, board_height
  );
  if (retv == NULL_POSITION) {
    return object();  // return None
  }
  return object(retv);
}

object hexoban_neighbor_position_wraper(
  HexobanTessellation& tessellation, position_t position,
  const Direction& direction, size_t board_width, size_t board_height
) {
  position_t retv = tessellation.neighbor_position(
    position, direction, board_width, board_height
  );
  if (retv == NULL_POSITION) {
    return object();  // return None
  }
  return object(retv);
}

void export_tessellations() {
  class_<SokobanTessellation>("SokobanTessellation") //, no_init())
    // protocols
    .def("__eq__", &SokobanTessellation::operator==)
    .def("__ne__", &SokobanTessellation::operator!=)
    .def("__str__", &SokobanTessellation::str)
    .def("__repr__", &SokobanTessellation::repr)

    .add_property(
      "legal_directions",
      make_function(
        &SokobanTessellation::legal_directions,
        return_internal_reference<>()
      )
    )
    .def(
      "neighbor_position", &sokoban_neighbor_position_wraper,
      args("position", "direction", "board_width", "board_height")
    )
    .add_property("graph_type", &SokobanTessellation::graph_type)
    .def(
      "char_to_atomic_move",
      &SokobanTessellation::char_to_atomic_move,
      args("input_chr")
    )
    .def(
      "atomic_move_to_char",
      &SokobanTessellation::atomic_move_to_char,
      args("atomic_move")
    )
    .def(
      "cell_orientation",
      &SokobanTessellation::cell_orientation,
      args("position", "board_width", "board_height")
    )
  ;

  class_<HexobanTessellation>("HexobanTessellation") //, no_init())
    // protocols
    .def("__eq__", &HexobanTessellation::operator==)
    .def("__ne__", &HexobanTessellation::operator!=)
    .def("__str__", &HexobanTessellation::str)
    .def("__repr__", &HexobanTessellation::repr)

    .add_property(
      "legal_directions",
      make_function(
        &HexobanTessellation::legal_directions, return_internal_reference<>()
      )
    )
    .def(
      "neighbor_position", &hexoban_neighbor_position_wraper,
      args("position", "direction", "board_width", "board_height")
    )
    .add_property("graph_type", &HexobanTessellation::graph_type)
    .def(
      "char_to_atomic_move",
      &HexobanTessellation::char_to_atomic_move,
      args("input_chr")
    )
    .def(
      "atomic_move_to_char",
      &HexobanTessellation::atomic_move_to_char,
      args("atomic_move")
    )
    .def(
      "cell_orientation",
      &HexobanTessellation::cell_orientation,
      args("position", "board_width", "board_height")
    )
  ;

  class_<OctobanTessellation>("OctobanTessellation") //, no_init())
    // protocols
    .def("__eq__", &OctobanTessellation::operator==)
    .def("__ne__", &OctobanTessellation::operator!=)
    .def("__str__", &OctobanTessellation::str)
    .def("__repr__", &OctobanTessellation::repr)

    .add_property(
      "legal_directions",
      make_function(
        &OctobanTessellation::legal_directions, return_internal_reference<>()
      )
    )
    .def(
      "neighbor_position", &octoban_neighbor_position_wraper,
      args("position", "direction", "board_width", "board_height")
    )
    .add_property("graph_type", &OctobanTessellation::graph_type)
    .def(
      "char_to_atomic_move",
      &OctobanTessellation::char_to_atomic_move,
      args("input_chr")
    )
    .def(
      "atomic_move_to_char",
      &OctobanTessellation::atomic_move_to_char,
      args("atomic_move")
    )
    .def(
      "cell_orientation",
      &OctobanTessellation::cell_orientation,
      args("position", "board_width", "board_height")
    )
  ;

  class_<TriobanTessellation>("TriobanTessellation") //, no_init())
    // protocols
    .def("__eq__", &TriobanTessellation::operator==)
    .def("__ne__", &TriobanTessellation::operator!=)
    .def("__str__", &TriobanTessellation::str)
    .def("__repr__", &TriobanTessellation::repr)

    .add_property(
      "legal_directions",
      make_function(
        &TriobanTessellation::legal_directions, return_internal_reference<>()
      )
    )
    .def(
      "neighbor_position", &trioban_neighbor_position_wraper,
      args("position", "direction", "board_width", "board_height")
    )
    .add_property("graph_type", &TriobanTessellation::graph_type)
    .def(
      "char_to_atomic_move",
      &TriobanTessellation::char_to_atomic_move,
      args("input_chr")
    )
    .def(
      "atomic_move_to_char",
      &TriobanTessellation::atomic_move_to_char,
      args("atomic_move")
    )
    .def(
      "cell_orientation",
      &TriobanTessellation::cell_orientation,
      args("position", "board_width", "board_height")
    )
  ;
}
