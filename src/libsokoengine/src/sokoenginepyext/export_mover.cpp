#include <pybind11/pybind11.h>
#include <sokoengine.hpp>

using namespace std;
namespace py = pybind11;
using namespace sokoengine;

void export_mover(py::module& m) {
  py::enum_<SolvingMode>(m, "SolvingMode")
    .value("FORWARD", SolvingMode::FORWARD)
    .value("REVERSE", SolvingMode::REVERSE)
    // We don't want constants be available in module scope
    // .export_values()
  ;

  py::class_<Mover>(m, "Mover")
    .def(
      py::init([](VariantBoard& board, const SolvingMode& solving_mode) {
        return make_unique<Mover>(board, solving_mode);
      }),
      py::arg("board"), py::arg("solving_mode")=SolvingMode::FORWARD
    )

    .def_property_readonly(
      "board", &Mover::board, py::return_value_policy::reference
    )

    .def_property_readonly("solving_mode", &Mover::solving_mode)

    .def_property_readonly(
      "state", &Mover::state, py::return_value_policy::reference_internal
    )

    .def_property_readonly("selected_pusher", &Mover::selected_pusher)
    .def_property("pulls_boxes", &Mover::pulls_boxes, &Mover::set_pulls_boxes)

    .def_property(
      "last_move",
      [](const Mover& self) {
        auto native_retv = self.last_move();
        py::list retv;
        for (auto am : native_retv) retv.append(am);
        return retv;
      },
      [](Mover& self, const py::object& value) {
        if (value.is_none()) {
          self.set_last_move(Mover::Moves());
        } else {
          Mover::Moves moves;
          for (auto am : value) moves.push_back(am.cast<AtomicMove>());
          self.set_last_move(moves);
        }
      }
    )

    .def("select_pusher", &Mover::select_pusher, py::arg("pusher_id"))
    .def("move", &Mover::move, py::arg("direction"))
    .def("jump", &Mover::jump, py::arg("new_position"))
    .def("undo_last_move", &Mover::undo_last_move)
  ;
}
