#include <boost/python.hpp>
#include <boost/python/raw_function.hpp>
#include <libsokoengine.hpp>

using namespace boost::python;
using namespace sokoengine;

struct AtomicMovePickle : boost::python::pickle_suite {
  static boost::python::tuple getinitargs(AtomicMove const& am) {
    return boost::python::make_tuple(
      am.direction(), am.is_push_or_pull(), am.is_jump(),
      am.is_pusher_selection(), am.pusher_id(), am.moved_box_id()
    );
  }
};

object moved_box_id_getter_wraper(const AtomicMove &atomic_move) {
  piece_id_t retv = atomic_move.moved_box_id();
  if (retv == NULL_ID) return object();  // return None
  else return object(retv);
}

void moved_box_id_setter_wraper(AtomicMove &atomic_move, const object& val) {
  piece_id_t rv;
  if (!val.is_none()) rv = boost::python::extract<piece_id_t>(val);
  else rv = NULL_ID;
  atomic_move.set_moved_box_id(rv);
}

object pusher_id_getter_wraper(const AtomicMove &atomic_move) {
  piece_id_t retv = atomic_move.pusher_id();
  if (retv == NULL_ID) return object();  // return None
  else return object(retv);
}

void pusher_id_setter_wraper(AtomicMove &atomic_move, const object& val) {
  piece_id_t rv;
  if (!val.is_none()) rv = boost::python::extract<piece_id_t>(val);
  else rv = NULL_ID;
  atomic_move.set_pusher_id(rv);
}

object AtomicMove_init(tuple args, dict kwargs) {
  Direction direction = Direction::LEFT;
  bool box_moved = false, is_jump = false, is_pusher_selection = false;
  piece_id_t pusher_id = DEFAULT_PIECE_ID, moved_box_id = NULL_ID;

  auto moved_box_id_extractor = [&] (const object& obj) -> piece_id_t {
    if (!obj.is_none()) return extract<piece_id_t>(obj);
    else return NULL_ID;
  };

  switch (len(args)) {
    case 7:
      direction = extract<Direction>(args[1]);
      box_moved = extract<bool>(args[2]);
      is_jump = extract<bool>(args[3]);
      is_pusher_selection = extract<bool>(args[4]);
      pusher_id = extract<piece_id_t>(args[5]);
      moved_box_id = moved_box_id_extractor(args[6]);
      break;
    case 6:
      direction = extract<Direction>(args[1]);
      box_moved = extract<bool>(args[2]);
      is_jump = extract<bool>(args[3]);
      is_pusher_selection = extract<bool>(args[4]);
      pusher_id = extract<piece_id_t>(args[5]);
      break;
    case 5:
      direction = extract<Direction>(args[1]);
      box_moved = extract<bool>(args[2]);
      is_jump = extract<bool>(args[3]);
      is_pusher_selection = extract<bool>(args[4]);
      break;
    case 4:
      direction = extract<Direction>(args[1]);
      box_moved = extract<bool>(args[2]);
      is_jump = extract<bool>(args[3]);
      break;
    case 3:
      direction = extract<Direction>(args[1]);
      box_moved = extract<bool>(args[2]);
      break;
    case 2:
      direction = extract<Direction>(args[1]);
  }

  if (kwargs.contains("direction"))
    direction = extract<Direction>(kwargs["direction"]);
  if (kwargs.contains("box_moved"))
    box_moved = extract<bool>(kwargs["box_moved"]);
  if (kwargs.contains("is_jump"))
    is_jump = extract<bool>(kwargs["is_jump"]);
  if (kwargs.contains("is_pusher_selection"))
    is_pusher_selection = extract<bool>(kwargs["is_pusher_selection"]);
  if (kwargs.contains("pusher_id"))
    pusher_id = extract<piece_id_t>(kwargs["pusher_id"]);
  if (kwargs.contains("moved_box_id"))
    moved_box_id = moved_box_id_extractor(kwargs["moved_box_id"]);

  return args[0].attr("__init__")(
    direction, box_moved, is_jump, is_pusher_selection, pusher_id, moved_box_id
  );
}

void export_atomic_move() {
  scope in_AtomicMove = class_<AtomicMove>("AtomicMove", no_init)
    .def("__init__", raw_function(AtomicMove_init)) // raw constructor
    .def(
      init<Direction, bool, bool, bool, piece_id_t, piece_id_t>(
        args(
          "direction", "box_moved", "is_jump", "is_pusher_selection",
          "pusher_id", "moved_box_id"
        )
      )
    ) // C++ constructor, shadowed by raw ctor

    // pickle support
    .def_pickle(AtomicMovePickle())

    // @classmethod
    .def("is_atomic_move", &AtomicMove::is_atomic_move, args("character"))
    .staticmethod("is_atomic_move")

    // protocols
    .def("__eq__", &AtomicMove::operator==)
    .def("__ne__", &AtomicMove::operator!=)
    .def("__str__", &AtomicMove::str)
    .def("__repr__", &AtomicMove::repr)

    // instance methods and properties
    .add_property("moved_box_id", &moved_box_id_getter_wraper, &moved_box_id_setter_wraper)

    .add_property("pusher_id", &pusher_id_getter_wraper, &pusher_id_setter_wraper)
    .add_property("is_move", &AtomicMove::is_move, &AtomicMove::set_is_move)
    .add_property("is_push_or_pull", &AtomicMove::is_push_or_pull, &AtomicMove::set_is_push_or_pull)
    .add_property("is_pusher_selection", &AtomicMove::is_pusher_selection, &AtomicMove::set_is_pusher_selection)
    .add_property("is_jump", &AtomicMove::is_jump, &AtomicMove::set_is_jump)
    .add_property(
      "direction",
      make_function(&AtomicMove::direction, return_internal_reference<>()),
      &AtomicMove::set_direction
    )
  ;

}
