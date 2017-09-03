#include <pybind11/pybind11.h>
#include <sokoengine.hpp>

using namespace std;
namespace py = pybind11;
using namespace sokoengine;

void export_atomic_move(py::module& m) {
  py::class_<AtomicMove>(m, "AtomicMove")
    .def(
      py::init([](
        const Direction& direction, bool box_moved, bool is_jump,
        bool is_pusher_selection, piece_id_t pusher_id,
        const py::object& moved_box_id
      ) {
        int moved_box_id_converted = NULL_ID;

        if (!moved_box_id.is_none())
          moved_box_id_converted = moved_box_id.cast<piece_id_t>();

        return make_unique<AtomicMove>(
          direction, box_moved, is_jump, is_pusher_selection, pusher_id,
          moved_box_id_converted
        );
      }),
      py::arg("direction")=Direction::LEFT,
      py::arg("box_moved")=false,
      py::arg("is_jump")=false,
      py::arg("is_pusher_selection")=false,
      py::arg("pusher_id")=DEFAULT_PIECE_ID,
      py::arg("moved_box_id")=py::none()
    )

    // @classmethod
    .def_static(
      "is_atomic_move_chr",
      &AtomicMove::is_atomic_move_chr, py::arg("character")
    )

    // protocols
    .def("__eq__", &AtomicMove::operator==)
    .def("__ne__", &AtomicMove::operator!=)
    .def("__str__", &AtomicMove::str)
    .def("__repr__", &AtomicMove::repr)

    .def(py::pickle(
      [](const AtomicMove &self) { // __getstate__
        return py::make_tuple(
          self.direction(), self.is_push_or_pull(), self.is_jump(),
          self.is_pusher_selection(), self.pusher_id(), self.moved_box_id()
        );
      },
      [](py::tuple t) { // __setstate__
        if (t.size() != 6) throw std::runtime_error("Invalid state!");
        return make_unique<AtomicMove>(
          t[0].cast<Direction>(),
          t[1].cast<bool>(), t[2].cast<bool>(), t[3].cast<bool>(),
          t[4].cast<piece_id_t>(), t[5].cast<piece_id_t>()
        );
      }
    ))

    // instance methods and properties
    .def_property(
      "moved_box_id",
      [](const AtomicMove& self) -> py::object {
        if (self.moved_box_id() == NULL_ID) return py::none();  // return None
        else return py::cast(self.moved_box_id());
      },
      [](AtomicMove& self, const py::object& val) {
        if (val.is_none()) self.set_moved_box_id(NULL_ID);
        else self.set_moved_box_id(val.cast<piece_id_t>());
      }
    )

    // instance methods and properties
    .def_property(
      "pusher_id",
      [](const AtomicMove& self) -> py::object {
        if (self.pusher_id() == NULL_ID) return py::none();  // return None
        else return py::cast(self.pusher_id());
      },
      [](AtomicMove& self, const py::object& val) {
        if (val.is_none()) self.set_pusher_id(NULL_ID);
        else self.set_pusher_id(val.cast<piece_id_t>());
      }
    )

    .def_property("is_move", &AtomicMove::is_move, &AtomicMove::set_is_move)
    .def_property(
      "is_push_or_pull",
      &AtomicMove::is_push_or_pull, &AtomicMove::set_is_push_or_pull
    )
    .def_property(
      "is_pusher_selection",
      &AtomicMove::is_pusher_selection, &AtomicMove::set_is_pusher_selection
    )
    .def_property("is_jump", &AtomicMove::is_jump, &AtomicMove::set_is_jump)
    .def_property(
      "direction",
      &AtomicMove::direction, &AtomicMove::set_direction,
      py::return_value_policy::reference
    )
  ;
}
