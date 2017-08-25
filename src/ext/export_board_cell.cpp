#include <boost/python.hpp>
#include <sokoengine.hpp>

using namespace boost::python;
using namespace sokoengine;

struct BoardCellPickle : boost::python::pickle_suite {
  static boost::python::tuple getinitargs(BoardCell const& bc) {
    return boost::python::make_tuple(
      bc.str(), bc.is_in_playable_area(), bc.is_deadlock()
    );
  }
};

void export_board_cell() {
  class_<BoardCell>(
      // class Python name
      "BoardCell",
      // __init__
      init<optional<char, bool, bool> >((
        // Without this static_cast extension segfaults on import
        arg("character")=static_cast<char>(BoardCell::FLOOR),
        arg("is_in_playable_area")=false,
        arg("is_deadlock")=false
      ))
    )

    // pickle support
    .def_pickle(BoardCellPickle())

    // @classmethod
    .def("is_pusher_chr", &BoardCell::is_pusher_chr, (arg("character")))
    .staticmethod("is_pusher_chr")
    .def("is_box_chr", &BoardCell::is_box_chr, (arg("character")))
    .staticmethod("is_box_chr")
    .def("is_goal_chr", &BoardCell::is_goal_chr, (arg("character")))
    .staticmethod("is_goal_chr")
    .def("is_empty_floor_chr", &BoardCell::is_empty_floor_chr, (arg("character")))
    .staticmethod("is_empty_floor_chr")
    .def("is_wall_chr", &BoardCell::is_wall_chr, (arg("character")))
    .staticmethod("is_wall_chr")

    // protocols
    .def("__eq__", &BoardCell::operator==)
    .def("__ne__", &BoardCell::operator!=)
    .def("__str__", &BoardCell::str)
    .def("__repr__", &BoardCell::repr)

    // instance methods and properties
    .def("to_str", &BoardCell::to_str, (arg("use_visible_floor")))
    .def("clear", &BoardCell::clear)
    .add_property("has_piece", &BoardCell::has_piece)
    .add_property("is_empty_floor", &BoardCell::is_empty_floor)
    .add_property("is_border_element", &BoardCell::is_border_element)
    .add_property("can_put_pusher_or_box", &BoardCell::can_put_pusher_or_box)
    .add_property("has_box", &BoardCell::has_box, &BoardCell::set_has_box)
    .def("put_box", &BoardCell::put_box)
    .def("remove_box", &BoardCell::remove_box)
    .add_property("has_goal", &BoardCell::has_goal, &BoardCell::set_has_goal)
    .def("put_goal", &BoardCell::put_goal)
    .def("remove_goal", &BoardCell::remove_goal)
    .add_property("has_pusher", &BoardCell::has_pusher, &BoardCell::set_has_pusher)
    .def("put_pusher", &BoardCell::put_pusher)
    .def("remove_pusher", &BoardCell::remove_pusher)
    .add_property("is_wall", &BoardCell::is_wall, &BoardCell::set_is_wall)
    .add_property("is_in_playable_area", &BoardCell::is_in_playable_area, &BoardCell::set_is_in_playable_area)
    .add_property("is_deadlock", &BoardCell::is_deadlock, &BoardCell::set_is_deadlock)
  ;

}
