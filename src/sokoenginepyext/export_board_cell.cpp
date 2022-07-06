#include "sokoenginepyext.hpp"

using sokoengine::game::BoardCell;
using sokoengine::io::Puzzle;
using std::make_unique;

void export_board_cell(py::module &m) {
  py::class_<BoardCell> pyBoardCell(m, "BoardCell");

  pyBoardCell
    .def(py::init<char>(), py::arg("character") = Puzzle::FLOOR)

    // protocols
    .def(
      "__eq__",
      [](const BoardCell &self, const BoardCell &rv) -> bool {
        return self == rv;
      }
    )
    .def(
      "__ne__",
      [](const BoardCell &self, const BoardCell &rv) -> bool {
        return self != rv;
      }
    )
    .def(
      "__eq__",
      [](const BoardCell &self, char rv) -> bool {
        return self == rv;
      }
    )
    .def(
      "__ne__",
      [](const BoardCell &self, char rv) -> bool {
        return self != rv;
      }
    )

    .def("__str__", &BoardCell::str)
    .def("__repr__", &BoardCell::repr)

    .def(py::pickle(
      [](const BoardCell &self) { // __getstate__
        return py::make_tuple(self.str(), self.is_in_playable_area());
      },
      [](py::tuple t) { // __setstate__
        if (t.size() != 2)
          throw std::runtime_error("Invalid BoardCell pickling state!");
        auto retv = make_unique<BoardCell>(t[0].cast<char>());
        retv->set_is_in_playable_area(t[1].cast<bool>());
        return retv;
      }
    ))

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
    .def_property(
      "is_in_playable_area",
      &BoardCell::is_in_playable_area,
      &BoardCell::set_is_in_playable_area
    );
}
