#include "sokoenginepyext.hpp"

using sokoengine::game::BoardGraph;
using sokoengine::game::Mover;
using sokoengine::game::PusherStep;
using sokoengine::game::PusherSteps;
using sokoengine::game::Selectors;
using sokoengine::game::SolvingMode;

void export_mover(py::module &m) {
  py::enum_<SolvingMode>(m, "SolvingMode")
    .value("FORWARD", SolvingMode::FORWARD)
    .value("REVERSE", SolvingMode::REVERSE);

  py::class_<Mover>(m, "Mover")
    .def(
      py::init<BoardGraph &, SolvingMode>(),
      py::arg("board"),
      py::arg("solving_mode") = SolvingMode::FORWARD
    )

    .def_property_readonly("board", &Mover::board, py::return_value_policy::reference)

    .def_property_readonly("solving_mode", &Mover::solving_mode)

    .def_property_readonly(
      "board_manager",
      &Mover::board_manager,
      py::return_value_policy::reference_internal
    )

    .def_property_readonly("selected_pusher", &Mover::selected_pusher)
    .def_property("pulls_boxes", &Mover::pulls_boxes, &Mover::set_pulls_boxes)

    .def_property(
      "last_move",
      &Mover::last_move,
      &Mover::set_last_move,
      // must be copied, otherwise Python side object will be corrupted
      // once mover makes next move
      py::return_value_policy::copy
    )
    .def(
      "select_pusher",
      [](Mover &self, py_int_t pusher_id) {
        return self.select_pusher(piece_or_throw(Selectors::PUSHERS, pusher_id));
      },
      py::arg("pusher_id")
    )
    .def("move", &Mover::move, py::arg("direction"))
    .def(
      "jump",
      [](Mover &self, py_int_t new_position) {
        return self.jump(position_or_throw(new_position));
      },
      py::arg("new_position")
    )
    .def("undo_last_move", &Mover::undo_last_move);
}
