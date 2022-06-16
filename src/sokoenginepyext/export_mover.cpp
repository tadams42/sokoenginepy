#include "sokoenginepyext.hpp"

using namespace std;
using sokoengine::game::BoardGraph;
using sokoengine::game::Mover;
using sokoengine::game::PusherStep;
using sokoengine::game::PusherSteps;
using sokoengine::game::SolvingMode;

void export_mover(py::module &m) {
  py::enum_<SolvingMode>(m, "SolvingMode")
    .value("FORWARD", SolvingMode::FORWARD)
    .value("REVERSE", SolvingMode::REVERSE)
    // We don't want constants be available in module scope
    // .export_values()
    ;

  py::class_<Mover>(m, "Mover")
    .def(py::init<BoardGraph &, SolvingMode>(), py::arg("board"),
         py::arg("solving_mode") = SolvingMode::FORWARD)

    .def_property_readonly("board", &Mover::board, py::return_value_policy::reference)

    .def_property_readonly("solving_mode", &Mover::solving_mode)

    .def_property_readonly("board_manager", &Mover::board_manager,
                           py::return_value_policy::reference_internal)

    .def_property_readonly("selected_pusher", &Mover::selected_pusher)
    .def_property("pulls_boxes", &Mover::pulls_boxes, &Mover::set_pulls_boxes)

    .def_property(
      "last_move",
      [](const Mover &self) {
        py::list retv;
        for (const auto &val : self.last_move())
          retv.append(val);
        return retv;
      },
      [](Mover &self, const py::object &value) {
        if (value.is_none()) {
          self.set_last_move(PusherSteps());
        } else {
          PusherSteps moves;
          for (auto am : value)
            moves.push_back(am.cast<PusherStep>());
          self.set_last_move(moves);
        }
      })

    .def("select_pusher", &Mover::select_pusher, py::arg("pusher_id"))
    .def("move", &Mover::move, py::arg("direction"))
    .def("jump", &Mover::jump, py::arg("new_position"))
    .def("undo_last_move", &Mover::undo_last_move);
}
