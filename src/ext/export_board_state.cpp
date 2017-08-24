#include <memory>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/map_indexing_suite.hpp>
#include <sokoengine.hpp>

using namespace std;
using namespace boost::python;
using namespace sokoengine;

boost::python::list pushers_ids_wrapper(BoardState& board_state) {
  return boost::python::list(board_state.pushers_ids());
}

boost::python::dict pushers_positions_wrapper(BoardState& board_state) {
  boost::python::dict retv;
  auto internal = board_state.pushers_positions();
  for (auto iter = internal.begin(); iter != internal.end(); ++iter) {
    retv[iter->first] = iter->second;
  }
  return retv;
}

boost::python::list boxes_ids_wrapper(BoardState& board_state) {
  return boost::python::list(board_state.boxes_ids());
}

boost::python::dict boxes_positions_wrapper(BoardState& board_state) {
  boost::python::dict retv;
  auto internal = board_state.boxes_positions();
  for (auto iter = internal.begin(); iter != internal.end(); ++iter) {
    retv[iter->first] = iter->second;
  }
  return retv;
}

boost::python::list goals_ids_wrapper(BoardState& board_state) {
  return boost::python::list(board_state.goals_ids());
}

boost::python::dict goals_positions_wrapper(BoardState& board_state) {
  boost::python::dict retv;
  auto internal = board_state.goals_positions();
  for (auto iter = internal.begin(); iter != internal.end(); ++iter) {
    retv[iter->first] = iter->second;
  }
  return retv;
}

boost::python::list solutions_wrapper(BoardState& board_state) {
  auto internal = board_state.solutions();

  boost::python::list retv;
  for (auto i = internal.begin(); i != internal.end(); ++i) {
    boost::python::dict d;
    for(auto j = (*i).begin(); j != (*i).end(); j++) {
      d[j->first] = j->second;
    }
    retv.append(d);
  }

  return retv;
}

boost::python::list solution_hashes_wrapper(HashedBoardState& board_state) {
  HashedBoardState::solution_hashes_t internal = board_state.solution_hashes();
  boost::python::list retv;
  for (const zobrist_key_t& hsh : internal) {
    retv.append(hsh);
  }
  return retv;
}

void set_boxorder_wrapper_BoardState(BoardState& board_state, const object& val) {
  if (val.is_none())
    board_state.set_boxorder("");
  else {
    string converted = extract<string>(val);
    board_state.set_boxorder(converted);
  }
}

void set_goalorder_wrapper_BoardState(BoardState& board_state, const object& val) {
  if (val.is_none())
    board_state.set_goalorder("");
  else {
    string converted = extract<string>(val);
    board_state.set_goalorder(converted);
  }
}

void set_boxorder_wrapper_HashedBoardState(HashedBoardState& board_state, const object& val) {
  if (val.is_none())
    board_state.set_boxorder("");
  else {
    string converted = extract<string>(val);
    board_state.set_boxorder(converted);
  }
}

void set_goalorder_wrapper_HashedBoardState(HashedBoardState& board_state, const object& val) {
  if (val.is_none())
    board_state.set_goalorder("");
  else {
    string converted = extract<string>(val);
    board_state.set_goalorder(converted);
  }
}

bool has_box_on_wrapper(BoardState& board_state, const object& position) {
  if (position.is_none()) return false;
  return board_state.has_box_on(extract<position_t>(position));
}

void export_board_state() {
  class_<BoardState>("BoardState", init<VariantBoard&>((
    boost::python::arg("variant_board")
  )))
    // protocols
    .def("__eq__", &BoardState::operator==)
    .def("__ne__", &BoardState::operator!=)
    .def("__str__", &BoardState::str)
    .def("__repr__", &BoardState::repr)

    .add_property(
      "board", make_function(
        &BoardState::board, return_internal_reference<>()
      )
    )

    .add_property("pushers_count", &BoardState::pushers_count)
    .add_property("pushers_ids", &pushers_ids_wrapper)
    .add_property("pushers_positions", &pushers_positions_wrapper)
    .def("pusher_position", &BoardState::pusher_position, (
      boost::python::arg("pusher_id")
    ))
    .def("pusher_id_on", &BoardState::pusher_id_on, (
      boost::python::arg("position")
    ))
    .def("has_pusher", &BoardState::has_pusher, (
      boost::python::arg("pusher_id")
    ))
    .def("has_pusher_on", &BoardState::has_pusher_on, (
      boost::python::arg("position")
    ))
    .def("move_pusher_from", &BoardState::move_pusher_from, (
      boost::python::arg("old_position"),
      boost::python::arg("to_new_position")
    ))
    .def("move_pusher", &BoardState::move_pusher, (
      boost::python::arg("pushers_id"),
      boost::python::arg("to_new_position")
    ))

    .add_property("boxes_count", &BoardState::boxes_count)
    .add_property("boxes_ids", &boxes_ids_wrapper)
    .add_property("boxes_positions", &boxes_positions_wrapper)
    .def("box_position", &BoardState::box_position, (
      boost::python::arg("box_id")
    ))
    .def("box_id_on", &BoardState::box_id_on, (
      boost::python::arg("position")
    ))
    .def("has_box", &BoardState::has_box, (
      boost::python::arg("box_id")
    ))
    .def("has_box_on", &has_box_on_wrapper, (
      boost::python::arg("position")
    ))
    .def("move_box_from", &BoardState::move_box_from, (
      boost::python::arg("old_position"),
      boost::python::arg("to_new_position")
    ))
    .def("move_box", &BoardState::move_box, (
      boost::python::arg("boxes_id"),
      boost::python::arg("to_new_position")
    ))

    .add_property("goals_count", &BoardState::goals_count)
    .add_property("goals_ids", &goals_ids_wrapper)
    .add_property("goals_positions", &goals_positions_wrapper)
    .def("goal_position", &BoardState::goal_position, (
      boost::python::arg("goal_id")
    ))
    .def("goal_id_on", &BoardState::goal_id_on, (
      boost::python::arg("position")
    ))
    .def("has_goal", &BoardState::has_goal, (
      boost::python::arg("goal_id")
    ))
    .def("has_goal_on", &BoardState::has_goal_on, (
      boost::python::arg("position")
    ))

    .def("box_plus_id", &BoardState::box_plus_id, (
      boost::python::arg("box_id")
    ))
    .def("goal_plus_id", &BoardState::goal_plus_id, (
      boost::python::arg("goal_id")
    ))

    .add_property("boxorder", &BoardState::boxorder, &set_boxorder_wrapper_BoardState)
    .add_property("goalorder", &BoardState::goalorder, &set_goalorder_wrapper_BoardState)
    .add_property("is_sokoban_plus_enabled", &BoardState::is_sokoban_plus_enabled)
    .add_property("is_sokoban_plus_valid", &BoardState::is_sokoban_plus_valid)
    .def("enable_sokoban_plus", &BoardState::enable_sokoban_plus)
    .def("disable_sokoban_plus", &BoardState::disable_sokoban_plus)

    .def("solutions", &solutions_wrapper)
    .def("switch_boxes_and_goals", &BoardState::switch_boxes_and_goals)
    .add_property("is_playable", &BoardState::is_playable)
  ;

  class_<BoardState::piece_positions_map_t>(
    "Positions").def(map_indexing_suite<BoardState::piece_positions_map_t>()
  );

  class_<HashedBoardState, bases<BoardState> >(
    "HashedBoardState", init<VariantBoard&>((boost::python::arg("variant_board")))
  )
    .def("__eq__", &HashedBoardState::operator==)
    .def("__ne__", &HashedBoardState::operator!=)
    .def("__str__", &HashedBoardState::str)
    .def("__repr__", &HashedBoardState::repr)

    .add_property("boxes_layout_hash", &HashedBoardState::boxes_layout_hash)
    .add_property("boxes_and_pushers_layout_hash", &HashedBoardState::boxes_and_pushers_layout_hash)
    .def(
      "external_position_hash",
      &HashedBoardState::external_position_hash,
      (boost::python::arg("boxes_positions"))
    )
    .add_property("boxorder", &HashedBoardState::boxorder, &set_boxorder_wrapper_HashedBoardState)
    .add_property("goalorder", &HashedBoardState::goalorder, &set_goalorder_wrapper_HashedBoardState)
    .def("enable_sokoban_plus", &HashedBoardState::enable_sokoban_plus)
    .def("disable_sokoban_plus", &HashedBoardState::disable_sokoban_plus)
    .def("is_solved", &HashedBoardState::is_solved)
    .add_property("solution_hashes", &solution_hashes_wrapper)
    .def("switch_boxes_and_goals", &HashedBoardState::switch_boxes_and_goals)
  ;
}
