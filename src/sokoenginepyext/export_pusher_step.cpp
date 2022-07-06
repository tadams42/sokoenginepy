#include "sokoenginepyext.hpp"

using sokoengine::game::Config;
using sokoengine::game::Direction;
using sokoengine::game::DIRECTIONS_COUNT;
using sokoengine::game::OPPOSITE_DIRECTIONS;
using sokoengine::game::piece_id_t;
using sokoengine::game::PusherStep;
using sokoengine::game::Selectors;
using sokoengine::game::Tessellation;
using std::make_unique;

constexpr const char *NAMES[DIRECTIONS_COUNT] = {
  "UP",
  "NORTH_EAST",
  "RIGHT",
  "SOUTH_EAST",
  "DOWN",
  "SOUTH_WEST",
  "LEFT",
  "NORTH_WEST"};

constexpr const char *OPPOSITE_NAMES[DIRECTIONS_COUNT] = {
  "DOWN",
  "SOUTH_WEST",
  "LEFT",
  "NORTH_WEST",
  "UP",
  "NORTH_EAST",
  "RIGHT",
  "SOUTH_EAST"};

void export_pusher_step(py::module &m) {
  auto pyDirection = py::enum_<Direction>(m, "Direction")
                       .value("UP", Direction::UP)
                       .value("DOWN", Direction::DOWN)
                       .value("LEFT", Direction::LEFT)
                       .value("RIGHT", Direction::RIGHT)
                       .value("SOUTH_EAST", Direction::SOUTH_EAST)
                       .value("SOUTH_WEST", Direction::SOUTH_WEST)
                       .value("NORTH_EAST", Direction::NORTH_EAST)
                       .value("NORTH_WEST", Direction::NORTH_WEST)
                       .def_static("__len__", []() {
                         return DIRECTIONS_COUNT;
                       });

  pyDirection.def_property_readonly("opposite", [pyDirection](const Direction &self) {
    return pyDirection.attr(OPPOSITE_NAMES[static_cast<uint8_t>(self)]);
  });

  auto pyPusherStep = py::class_<PusherStep>(m, "PusherStep");

  pyPusherStep.def(
    py::init([](
               const Direction &direction,
               py_int_t         moved_box_id,
               bool             is_jump,
               bool             is_pusher_selection,
               py_int_t         pusher_id,
               bool             is_current_pos
             ) {
      return make_unique<PusherStep>(
        direction,
        no_id_if_invalid(moved_box_id),
        is_jump,
        is_pusher_selection,
        default_if_invalid(pusher_id),
        is_current_pos
      );
    }),
    py::arg("direction")           = Direction::LEFT,
    py::arg("moved_box_id")        = Config::NO_ID,
    py::arg("is_jump")             = false,
    py::arg("is_pusher_selection") = false,
    py::arg("pusher_id")           = Config::DEFAULT_ID,
    py::arg("is_current_pos")      = false
  );

  // protocols
  pyPusherStep.def("__eq__", &PusherStep::operator==);
  pyPusherStep.def("__ne__", &PusherStep::operator!=);
  pyPusherStep.def("__str__", &PusherStep::str);
  pyPusherStep.def("__repr__", &PusherStep::repr);

  pyPusherStep.def_property(
    "direction",
    [pyDirection](const PusherStep &self) {
      return pyDirection.attr(NAMES[static_cast<uint8_t>(self.direction())]);
    },
    &PusherStep::set_direction
  );

  pyPusherStep.def_property(
    "moved_box_id",
    &PusherStep::moved_box_id,
    [](PusherStep &self, py_int_t rv) {
      self.set_moved_box_id(no_id_if_invalid(rv));
    }
  );
  pyPusherStep.def_property(
    "pusher_id",
    &PusherStep::pusher_id,
    [](PusherStep &self, py_int_t rv) {
      self.set_pusher_id(default_if_invalid(rv));
    }
  );

  pyPusherStep.def_property_readonly("is_move", &PusherStep::is_move);
  pyPusherStep.def_property_readonly("is_push_or_pull", &PusherStep::is_push_or_pull);
  pyPusherStep.def_property(
    "is_pusher_selection",
    &PusherStep::is_pusher_selection,
    &PusherStep::set_is_pusher_selection
  );
  pyPusherStep.def_property("is_jump", &PusherStep::is_jump, &PusherStep::set_is_jump);
  pyPusherStep.def_property(
    "is_current_pos", &PusherStep::is_current_pos, &PusherStep::set_is_current_pos
  );

  // clang-format off
  pyPusherStep.def(py::pickle(
    [](const PusherStep &self) { // __getstate__
      return py::make_tuple(
        sokoengine::game::direction_pack(self.direction()),
        self.moved_box_id(),
        self.is_jump(),
        self.is_pusher_selection(),
        self.pusher_id(),
        self.is_current_pos()
      );
    },
    [](py::tuple t) { // __setstate__
      if (t.size() != 6)
        throw std::runtime_error("Invalid pickle state for PusherStep!");
      return make_unique<PusherStep>(
        sokoengine::game::direction_unpack(t[0].cast<uint8_t>()),
        t[1].cast<piece_id_t>(),
        t[2].cast<bool>(),
        t[3].cast<bool>(),
        t[4].cast<piece_id_t>(),
        t[5].cast<bool>()
      );
    }));
  // clang-format on

  // clang-format off
  /*
  pyDirection.def_property_readonly("opposite_copy", [](const Direction &self) {
    return OPPOSITE_DIRECTIONS[static_cast<uint8_t>(self)];
  });

  // python -m timeit -r10 -s "import sokoenginepyext" "sokoenginepyext.Direction.DOWN.opposite_copy"
  // python -m timeit -r10 -s "import sokoenginepyext" "sokoenginepyext.Direction.DOWN.opposite"

  pyPusherStep.def_property("direction_copy", &PusherStep::direction, &PusherStep::set_direction);

  // python -m timeit -r10 -s "import sokoenginepyext; a = sokoenginepyext.PusherStep()" "a.direction"
  // python -m timeit -r10 -s "import sokoenginepyext; a = sokoenginepyext.PusherStep()" "a.direction_copy"
  // python -m timeit -r10 -s "import sokoenginepyext; a = sokoenginepyext.PusherStep()" "a.direction.opposite"
  // python -m timeit -r10 -s "import sokoenginepyext; a = sokoenginepyext.PusherStep()" "a.direction_copy.opposite_copy"
  */
  // clang-format on
}
