#include <memory>
#include <boost/python.hpp>
#include <boost/python/raw_function.hpp>
#include <sokoengine.hpp>

using namespace std;
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

shared_ptr<AtomicMove> AtomicMove_init(
  const Direction& direction,
  bool box_moved,
  bool is_jump,
  bool is_pusher_selection,
  piece_id_t pusher_id,
  const object& moved_box_id
) {
  int moved_box_id_converted = NULL_ID;
  if (!moved_box_id.is_none())
    moved_box_id_converted = extract<int>(moved_box_id);
  return make_shared<AtomicMove>(
    direction,
    box_moved,
    is_jump,
    is_pusher_selection,
    pusher_id,
    moved_box_id_converted
  );
}

void export_atomic_move() {
  class_<AtomicMove>("AtomicMove")
    .def("__init__", make_constructor(
      AtomicMove_init,
      default_call_policies(),
      (
        boost::python::arg("direction")=Direction::LEFT,
        boost::python::arg("box_moved")=false,
        boost::python::arg("is_jump")=false,
        boost::python::arg("is_pusher_selection")=false,
        // Without this static_cast extension segfaults on import
        boost::python::arg("pusher_id")=static_cast<int>(DEFAULT_PIECE_ID),
        boost::python::arg("moved_box_id")=object()
      )
    ))

    // pickle support
    .def_pickle(AtomicMovePickle())

    // @classmethod
    .def(
      "is_atomic_move", &AtomicMove::is_atomic_move,
      (boost::python::arg("character"))
    ).staticmethod("is_atomic_move")

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
