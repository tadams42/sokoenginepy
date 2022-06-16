#include "sokoenginepyext.hpp"

using namespace std;
using sokoengine::game::BoardCell;
using sokoengine::io::Puzzle;

void export_board_cell(py::module &m) {
  py::class_<BoardCell> pyBoardCell(m, "BoardCell");

  pyBoardCell
    .def(py::init<char, bool, bool>(), py::arg("character") = Puzzle::FLOOR,
         py::arg("is_in_playable_area") = false, py::arg("is_deadlock") = false)

    // protocols
    .def("__eq__",
         [](const BoardCell &self, const BoardCell &rv) -> bool { return self == rv; })
    .def("__ne__",
         [](const BoardCell &self, const BoardCell &rv) -> bool { return self != rv; })
    .def("__eq__", [](const BoardCell &self, char rv) -> bool { return self == rv; })
    .def("__ne__", [](const BoardCell &self, char rv) -> bool { return self != rv; })

    .def("__str__", &BoardCell::str)
    .def("__repr__", &BoardCell::repr)

    .def(py::pickle(
      [](const BoardCell &self) { // __getstate__
        return py::make_tuple(self.str(), self.is_in_playable_area(),
                              self.is_deadlock());
      },
      [](py::tuple t) { // __setstate__
        if (t.size() != 3) throw std::runtime_error("Invalid state!");
        return make_unique<BoardCell>(t[0].cast<char>(), t[1].cast<bool>(),
                                      t[2].cast<bool>());
      }))

    // instance methods and properties
    .def("to_str", &BoardCell::to_str, py::arg("use_visible_floor") = false)
    .def("clear", &BoardCell::clear)
    .def_property_readonly("has_piece", &BoardCell::has_piece)
    .def_property_readonly("is_empty_floor", &BoardCell::is_empty_floor)
    .def_property_readonly("is_border_element", &BoardCell::is_border_element)
    .def_property_readonly("can_put_pusher_or_box", &BoardCell::can_put_pusher_or_box)
    .def_property("has_box", &BoardCell::has_box, &BoardCell::set_has_box)
    .def("put_box", &BoardCell::put_box)
    .def("remove_box", &BoardCell::remove_box)
    .def_property("has_goal", &BoardCell::has_goal, &BoardCell::set_has_goal)
    .def("put_goal", &BoardCell::put_goal)
    .def("remove_goal", &BoardCell::remove_goal)
    .def_property("has_pusher", &BoardCell::has_pusher, &BoardCell::set_has_pusher)
    .def("put_pusher", &BoardCell::put_pusher)
    .def("remove_pusher", &BoardCell::remove_pusher)
    .def_property("is_wall", &BoardCell::is_wall, &BoardCell::set_is_wall)
    .def_property("is_in_playable_area", &BoardCell::is_in_playable_area,
                  &BoardCell::set_is_in_playable_area)
    .def_property("is_deadlock", &BoardCell::is_deadlock, &BoardCell::set_is_deadlock);
}
