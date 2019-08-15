#include "sokoenginepyext.hpp"

using namespace std;
using namespace sokoengine;

piece_id_t receive_pusher_id(const py::object &pusher_id) {
  // Pusher ID setter in Python accepts any object
  //  - anything not integer or < DEFAULT_ID is treated as DEFAULT_ID
  piece_id_t retv = DEFAULT_PIECE_ID;
  py::extract<py::py_int_t> maybe_number(pusher_id);
  if (maybe_number.check()) {
    py::py_int_t tmp = maybe_number();
    if (tmp > DEFAULT_PIECE_ID && tmp < numeric_limits<piece_id_t>::max()) {
      retv = (piece_id_t)tmp;
    }
  }
  return retv;
}

piece_id_t receive_box_id(const py::object &box_id) {
  // Box ID setter in Python accepts any object
  //  - anything not integer or < DEFAULT_ID is treated as NULL_ID
  piece_id_t retv = NULL_ID;

  py::extract<py::py_int_t> maybe_number(box_id);
  if (maybe_number.check()) {
    py::py_int_t tmp = maybe_number();
    if (tmp > DEFAULT_PIECE_ID && tmp < numeric_limits<piece_id_t>::max()) {
      retv = (piece_id_t)tmp;
    }
  }

  return retv;
}

void export_atomic_move(py::module &m) {
  py::class_<AtomicMove>(m, "AtomicMove")
    .def(py::init([](const Direction &direction, bool box_moved, bool is_jump,
                     bool is_pusher_selection, const py::object &pusher_id,
                     const py::object &moved_box_id) {
           return make_unique<AtomicMove>(
             direction, box_moved, is_jump, is_pusher_selection,
             receive_pusher_id(pusher_id), receive_box_id(moved_box_id));
         }),
         py::arg("direction") = Direction::LEFT, py::arg("box_moved") = false,
         py::arg("is_jump") = false, py::arg("is_pusher_selection") = false,
         py::arg("pusher_id") = DEFAULT_PIECE_ID, py::arg("moved_box_id") = py::none())

    // @classmethod
    .def_static("is_atomic_move_chr", &AtomicMove::is_atomic_move_chr,
                py::arg("character"))

    // protocols
    .def("__eq__", &AtomicMove::operator==)
    .def("__ne__", &AtomicMove::operator!=)
    .def("__str__", &AtomicMove::str)
    .def("__repr__", &AtomicMove::repr)

    .def(py::pickle(
      [](const AtomicMove &self) { // __getstate__
        return py::make_tuple(self.direction(), self.is_push_or_pull(), self.is_jump(),
                              self.is_pusher_selection(), self.pusher_id(),
                              self.moved_box_id());
      },
      [](py::tuple t) { // __setstate__
        if (t.size() != 6) throw std::runtime_error("Invalid state!");
        // TODO: t[5].cast<piece_id_t>() - what if t[5] i s None?
        return make_unique<AtomicMove>(
          t[0].cast<Direction>(), t[1].cast<bool>(), t[2].cast<bool>(),
          t[3].cast<bool>(), t[4].cast<piece_id_t>(), t[5].cast<piece_id_t>());
      }))

    .def_property("moved_box_id",
                  [](const AtomicMove &self) -> py::object {
                    if (self.moved_box_id() == NULL_ID) return py::none();
                    return py::cast(self.moved_box_id());
                  },
                  [](AtomicMove &self, const py::object &val) {
                    self.set_moved_box_id(receive_box_id(val));
                  })

    .def_property("pusher_id",
                  [](const AtomicMove &self) -> py::object {
                    if (self.pusher_id() == NULL_ID) return py::none();
                    return py::cast(self.pusher_id());
                  },
                  [](AtomicMove &self, const py::object &val) {
                    self.set_pusher_id(receive_pusher_id(val));
                  })

    .def_property("is_move", &AtomicMove::is_move, &AtomicMove::set_is_move)
    .def_property("is_push_or_pull", &AtomicMove::is_push_or_pull,
                  &AtomicMove::set_is_push_or_pull)
    .def_property("is_pusher_selection", &AtomicMove::is_pusher_selection,
                  &AtomicMove::set_is_pusher_selection)
    .def_property("is_jump", &AtomicMove::is_jump, &AtomicMove::set_is_jump)
    .def_property("direction", &AtomicMove::direction, &AtomicMove::set_direction,
                  py::return_value_policy::reference)

    .def_property_readonly_static("l", [](py::object) { return AtomicMove::l; })
    .def_property_readonly_static("u", [](py::object) { return AtomicMove::u; })
    .def_property_readonly_static("r", [](py::object) { return AtomicMove::r; })
    .def_property_readonly_static("d", [](py::object) { return AtomicMove::d; })
    .def_property_readonly_static("L", [](py::object) { return AtomicMove::L; })
    .def_property_readonly_static("U", [](py::object) { return AtomicMove::U; })
    .def_property_readonly_static("R", [](py::object) { return AtomicMove::R; })
    .def_property_readonly_static("D", [](py::object) { return AtomicMove::D; })
    .def_property_readonly_static("w", [](py::object) { return AtomicMove::w; })
    .def_property_readonly_static("W", [](py::object) { return AtomicMove::W; })
    .def_property_readonly_static("e", [](py::object) { return AtomicMove::e; })
    .def_property_readonly_static("E", [](py::object) { return AtomicMove::E; })
    .def_property_readonly_static("n", [](py::object) { return AtomicMove::n; })
    .def_property_readonly_static("N", [](py::object) { return AtomicMove::N; })
    .def_property_readonly_static("s", [](py::object) { return AtomicMove::s; })
    .def_property_readonly_static("S", [](py::object) { return AtomicMove::S; })

    .def_property_readonly_static("CHARACTERS", [](py::object) {
      static const std::set<char> retv({
        AtomicMove::l,
        AtomicMove::u,
        AtomicMove::r,
        AtomicMove::d,
        AtomicMove::L,
        AtomicMove::U,
        AtomicMove::R,
        AtomicMove::D,
        AtomicMove::w,
        AtomicMove::W,
        AtomicMove::e,
        AtomicMove::E,
        AtomicMove::n,
        AtomicMove::N,
        AtomicMove::s,
        AtomicMove::S,
      });

      return retv;
    });
}
