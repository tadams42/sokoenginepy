#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <sokoengine.hpp>

using namespace boost::python;
using namespace sokoengine;

boost::python::list last_move_wrapper(Mover& mover) {
  return boost::python::list(mover.last_move());
}

void set_last_move_wrapper(Mover& mover, const object& obj) {
  Mover::Moves moves;

  if (! obj.is_none()) {
    auto length = len(obj);
    for (size_t i = 0; i < length; ++i) {
      moves.push_back(boost::python::extract<AtomicMove>(obj[i]));
    }
  }

  mover.set_last_move(moves);
}

void export_mover() {
  class_<Mover::Moves>("Moves").def(vector_indexing_suite<Mover::Moves>());

  enum_<SolvingMode>("SolvingMode")
    .value("FORWARD", SolvingMode::FORWARD)
    .value("REVERSE", SolvingMode::REVERSE)
    // We don't want constants be available in module scope
    // .export_values()
  ;

  class_<Mover>("Mover", init<VariantBoard&, optional<SolvingMode> >((
    boost::python::arg("board"),
    boost::python::arg("solving_mode")=SolvingMode::FORWARD
  )))

    .add_property(
      "board", make_function(&Mover::board, return_internal_reference<>())
    )
    .add_property("solving_mode", &Mover::solving_mode)
    .add_property(
      "state", make_function(&Mover::state, return_internal_reference<>())
    )
    .add_property("selected_pusher", &Mover::selected_pusher)
    .add_property("pulls_boxes", &Mover::pulls_boxes, &Mover::set_pulls_boxes)
    .add_property("last_move", &last_move_wrapper, &set_last_move_wrapper)

    .def(
      "select_pusher", &Mover::select_pusher,
      (boost::python::arg("pusher_id"))
    )
    .def(
      "move", &Mover::move, (boost::python::arg("direction"))
    )
    .def(
      "jump", &Mover::jump, (boost::python::arg("new_position"))
    )
    .def(
      "undo_last_move", &Mover::undo_last_move
    )
  ;
}
