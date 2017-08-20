#include <boost/python.hpp>
#include <libsokoengine.hpp>

using namespace boost::python;
using namespace sokoengine;

struct AtomicMovePickle : boost::python::pickle_suite {
  static boost::python::tuple getinitargs(AtomicMove const& am) {
    return boost::python::make_tuple(am.direction(), am.is_push_or_pull());
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

void export_atomic_move() {
  scope in_AtomicMove = class_<AtomicMove>(
      // class Python name
      "AtomicMove",
      // __init__
      init<optional<Direction, bool> >(args("direction", "box_moved"))
    )

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
