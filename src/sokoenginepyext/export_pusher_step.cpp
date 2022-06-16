#include "sokoenginepyext.hpp"

using namespace std;
using sokoengine::game::Config;
using sokoengine::game::Direction;
using sokoengine::game::DIRECTIONS_COUNT;
using sokoengine::game::OPPOSITE_DIRECTIONS;
using sokoengine::game::piece_id_t;
using sokoengine::game::PusherStep;

piece_id_t receive_pusher_id(const py::object &pusher_id) {
  // Pusher ID setter in Python accepts any object
  //  - anything not integer or < DEFAULT_ID is treated as DEFAULT_ID
  piece_id_t retv = Config::DEFAULT_PIECE_ID;
  py::extract<py::py_int_t> maybe_number(pusher_id);
  if (maybe_number.check()) {
    py::py_int_t tmp = maybe_number();
    if (tmp > Config::DEFAULT_PIECE_ID && tmp < numeric_limits<piece_id_t>::max()) {
      retv = (piece_id_t)tmp;
    }
  }
  return retv;
}

piece_id_t receive_box_id(const py::object &box_id) {
  // Box ID setter in Python accepts any object
  //  - anything not integer or < DEFAULT_ID is treated as NULL_ID
  piece_id_t retv = Config::NULL_ID;

  py::extract<py::py_int_t> maybe_number(box_id);
  if (maybe_number.check()) {
    py::py_int_t tmp = maybe_number();
    if (tmp > Config::DEFAULT_PIECE_ID && tmp < numeric_limits<piece_id_t>::max()) {
      retv = (piece_id_t)tmp;
    }
  }

  return retv;
}

constexpr const char *NAMES[DIRECTIONS_COUNT] = {
  "UP",   "NORTH_EAST", "RIGHT", "SOUTH_EAST",
  "DOWN", "SOUTH_WEST", "LEFT",  "NORTH_WEST"};

constexpr const char *OPPOSITE_NAMES[DIRECTIONS_COUNT] = {
  "DOWN", "SOUTH_WEST", "LEFT",  "NORTH_WEST",
  "UP",   "NORTH_EAST", "RIGHT", "SOUTH_EAST"};

void export_pusher_step(py::module &m) {
  auto direction_enm = py::enum_<Direction>(m, "Direction")
                         .value("UP", Direction::UP)
                         .value("DOWN", Direction::DOWN)
                         .value("LEFT", Direction::LEFT)
                         .value("RIGHT", Direction::RIGHT)
                         .value("SOUTH_EAST", Direction::SOUTH_EAST)
                         .value("SOUTH_WEST", Direction::SOUTH_WEST)
                         .value("NORTH_EAST", Direction::NORTH_EAST)
                         .value("NORTH_WEST", Direction::NORTH_WEST)
                         .def_static("__len__", []() { return DIRECTIONS_COUNT; });

  direction_enm.def_property_readonly(
    "opposite", [direction_enm](const Direction &self) {
      return direction_enm.attr(OPPOSITE_NAMES[static_cast<uint8_t>(self)]);
    });

  direction_enm.def_property_readonly("opposite_copy", [](const Direction &self) {
    return OPPOSITE_DIRECTIONS[static_cast<uint8_t>(self)];
  });
  // python -m timeit -r10 -s "import sokoenginepyext"
  // "sokoenginepyext.Direction.DOWN.opposite_copy" python -m timeit -r10 -s "import
  // sokoenginepyext" "sokoenginepyext.Direction.DOWN.opposite"

  // direction_enm.def(
  //   py::pickle(
  //     [](const Direction &self) { // __getstate__
  //       return py::make_tuple(direction_pack(self));
  //     },
  //     [](py::tuple t) { // __setstate__
  //       if (t.size() != 1) throw std::runtime_error("Invalid state!");
  //       return direction_unpack(t[0].cast<int8_t>());
  //     }
  //   ),
  //   py::return_value_policy::reference
  // );

  py::class_<PusherStep>(m, "PusherStep")
    .def(py::init([](const Direction &direction, bool box_moved, bool is_jump,
                     bool is_pusher_selection, const py::object &pusher_id,
                     const py::object &moved_box_id) {
           return make_unique<PusherStep>(
             direction, box_moved, is_jump, is_pusher_selection,
             receive_pusher_id(pusher_id), receive_box_id(moved_box_id));
         }),
         py::arg("direction") = Direction::LEFT, py::arg("box_moved") = false,
         py::arg("is_jump") = false, py::arg("is_pusher_selection") = false,
         py::arg("pusher_id") = Config::DEFAULT_PIECE_ID,
         py::arg("moved_box_id") = py::none())

    // protocols
    .def("__eq__", &PusherStep::operator==)
    .def("__ne__", &PusherStep::operator!=)
    .def("__str__", &PusherStep::str)
    .def("__repr__", &PusherStep::repr)

    .def(py::pickle(
      [](const PusherStep &self) { // __getstate__
        return py::make_tuple(self.direction(), self.is_push_or_pull(), self.is_jump(),
                              self.is_pusher_selection(), self.pusher_id(),
                              self.moved_box_id());
      },
      [](py::tuple t) { // __setstate__
        if (t.size() != 6) throw std::runtime_error("Invalid state!");
        // TODO: t[5].cast<piece_id_t>() - what if t[5] i s None?
        return make_unique<PusherStep>(
          t[0].cast<Direction>(), t[1].cast<bool>(), t[2].cast<bool>(),
          t[3].cast<bool>(), t[4].cast<piece_id_t>(), t[5].cast<piece_id_t>());
      }))

    .def_property(
      "direction",
      [direction_enm](const PusherStep &self) {
        return direction_enm.attr(NAMES[static_cast<uint8_t>(self.direction())]);
      },
      &PusherStep::set_direction)

    .def_property("direction_copy", &PusherStep::direction, &PusherStep::set_direction)
    // python -m timeit -r10 -s "import sokoenginepyext; a =
    // sokoenginepyext.PusherStep()" "a.direction"
    // python -m timeit -r10 -s "import sokoenginepyext; a =
    // sokoenginepyext.PusherStep()" "a.direction_copy"
    // python -m timeit -r10 -s "import sokoenginepyext; a =
    // sokoenginepyext.PusherStep()" "a.direction.opposite"
    // python -m timeit -r10 -s "import sokoenginepyext; a =
    // sokoenginepyext.PusherStep()" "a.direction_copy.opposite_copy"

    .def_property(
      "moved_box_id",
      [](const PusherStep &self) -> py::object {
        if (self.moved_box_id() == Config::NULL_ID) return py::none();
        return py::cast(self.moved_box_id());
      },
      [](PusherStep &self, const py::object &val) {
        self.set_moved_box_id(receive_box_id(val));
      })

    .def_property(
      "pusher_id",
      [](const PusherStep &self) -> py::object {
        if (self.pusher_id() == Config::NULL_ID) return py::none();
        return py::cast(self.pusher_id());
      },
      [](PusherStep &self, const py::object &val) {
        self.set_pusher_id(receive_pusher_id(val));
      })

    .def_property("is_move", &PusherStep::is_move, &PusherStep::set_is_move)
    .def_property("is_push_or_pull", &PusherStep::is_push_or_pull,
                  &PusherStep::set_is_push_or_pull)
    .def_property("is_pusher_selection", &PusherStep::is_pusher_selection,
                  &PusherStep::set_is_pusher_selection)
    .def_property("is_jump", &PusherStep::is_jump, &PusherStep::set_is_jump);
}
