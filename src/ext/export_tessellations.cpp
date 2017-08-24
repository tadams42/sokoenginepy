#include <boost/python.hpp>
#include <sokoengine.hpp>

using namespace boost::python;
using namespace sokoengine;

object neighbor_position_wraper(
  TessellationBase& tessellation, position_t position,
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
  enum_<CellOrientation>("CellOrientation")
    .value("DEFAULT", CellOrientation::DEFAULT)
    .value("TRIANGLE_DOWN", CellOrientation::TRIANGLE_DOWN)
    .value("OCTAGON", CellOrientation::OCTAGON)
    // We don't want constants be available in module scope
    // .export_values()
  ;

  class_<TessellationBase , boost::noncopyable>("TessellationBase", no_init);

  class_<SokobanTessellation, bases<TessellationBase> >(
    "SokobanTessellation"
  ) //, no_init())
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
      "neighbor_position", &neighbor_position_wraper,
      (arg("position"), arg("direction"), arg("board_width"), arg("board_height"))
    )
    .add_property("graph_type", &SokobanTessellation::graph_type)
    .def(
      "char_to_atomic_move",
      &SokobanTessellation::char_to_atomic_move,
      (arg("input_chr"))
    )
    .def(
      "atomic_move_to_char",
      &SokobanTessellation::atomic_move_to_char,
      (arg("atomic_move"))
    )
    .def(
      "cell_orientation",
      &SokobanTessellation::cell_orientation,
      (arg("position"), arg("board_width"), arg("board_height"))
    )
  ;

  class_<HexobanTessellation, bases<TessellationBase> >(
    "HexobanTessellation"
  ) //, no_init())
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
      "neighbor_position", &neighbor_position_wraper,
      (arg("position"), arg("direction"), arg("board_width"), arg("board_height"))
    )
    .add_property("graph_type", &HexobanTessellation::graph_type)
    .def(
      "char_to_atomic_move",
      &HexobanTessellation::char_to_atomic_move,
      (arg("input_chr"))
    )
    .def(
      "atomic_move_to_char",
      &HexobanTessellation::atomic_move_to_char,
      (arg("atomic_move"))
    )
    .def(
      "cell_orientation",
      &HexobanTessellation::cell_orientation,
      (arg("position"), arg("board_width"), arg("board_height"))
    )
  ;

  class_<OctobanTessellation, bases<TessellationBase> >(
    "OctobanTessellation"
  ) //, no_init())
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
      "neighbor_position", &neighbor_position_wraper,
      (arg("position"), arg("direction"), arg("board_width"), arg("board_height"))
    )
    .add_property("graph_type", &OctobanTessellation::graph_type)
    .def(
      "char_to_atomic_move",
      &OctobanTessellation::char_to_atomic_move,
      (arg("input_chr"))
    )
    .def(
      "atomic_move_to_char",
      &OctobanTessellation::atomic_move_to_char,
      (arg("atomic_move"))
    )
    .def(
      "cell_orientation",
      &OctobanTessellation::cell_orientation,
      (arg("position"), arg("board_width"), arg("board_height"))
    )
  ;

  class_<TriobanTessellation, bases<TessellationBase> >(
    "TriobanTessellation"
  ) //, no_init())
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
      "neighbor_position", &neighbor_position_wraper,
      (arg("position"), arg("direction"), arg("board_width"), arg("board_height"))
    )
    .add_property("graph_type", &TriobanTessellation::graph_type)
    .def(
      "char_to_atomic_move",
      &TriobanTessellation::char_to_atomic_move,
      (arg("input_chr"))
    )
    .def(
      "atomic_move_to_char",
      &TriobanTessellation::atomic_move_to_char,
      (arg("atomic_move"))
    )
    .def(
      "cell_orientation",
      &TriobanTessellation::cell_orientation,
      (arg("position"), arg("board_width"), arg("board_height"))
    )
  ;
}
