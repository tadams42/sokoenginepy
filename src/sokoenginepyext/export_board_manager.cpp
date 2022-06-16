#include "sokoenginepyext.hpp"

using namespace std;
using sokoengine::game::BoardGraph;
using sokoengine::game::BoardManager;
using sokoengine::game::BoardState;
using sokoengine::game::HashedBoardManager;
using sokoengine::game::zobrist_key_t;

void export_board_manager(py::module &m) {
  py::class_<BoardState>(m, "BoardState")
    .def(py::init([](const py::iterable &pushers_positions,
                     const py::iterable &boxes_positions, zobrist_key_t zobrist_hash) {
           return make_unique<BoardState>(
             py::receive_positions_throw(pushers_positions),
             py::receive_positions_throw(boxes_positions), zobrist_hash);
         }),
         py::arg("pushers_positions") = py::none(),
         py::arg("boxes_positions") = py::none(),
         py::arg("zobrist_hash") = BoardState::NO_HASH)

    // protocols
    .def("__eq__", &BoardState::operator==)
    .def("__ne__", &BoardState::operator!=)
    .def("__str__", &BoardState::str)
    .def("__repr__", &BoardState::repr)

    .def_property(
      "pushers_positions", [](BoardState &self) { return self.pushers_positions(); },
      [](BoardState &self, const py::iterable &rv) {
        self.pushers_positions() = py::receive_positions_throw(rv);
      })

    .def_property(
      "boxes_positions", [](BoardState &self) { return self.boxes_positions(); },
      [](BoardState &self, const py::iterable &rv) {
        self.boxes_positions() = py::receive_positions_throw(rv);
      })

    .def_property(
      "zobrist_hash", [](BoardState &self) { return self.zobrist_hash(); },
      [](BoardState &self, zobrist_key_t rv) { self.zobrist_hash() = rv; });

  py::class_<BoardManager>(m, "BoardManager")
    .def(py::init<BoardGraph &, const string &, const string &>(), py::arg("board"),
         py::arg("boxorder") = "", py::arg("goalorder") = "")

    // protocols
    .def("__str__", &BoardManager::str)

    .def_property_readonly("board", &BoardManager::board,
                           py::return_value_policy::reference)

    .def_property_readonly("pushers_count", &BoardManager::pushers_count)
    .def_property_readonly("pushers_ids", &BoardManager::pushers_ids)
    .def_property_readonly("pushers_positions", &BoardManager::pushers_positions)
    .def("pusher_position", &BoardManager::pusher_position, py::arg("pusher_id"))
    .def("pusher_id_on", &BoardManager::pusher_id_on, py::arg("position"))
    .def("has_pusher", &BoardManager::has_pusher, py::arg("pusher_id"))
    .def("has_pusher_on", &BoardManager::has_pusher_on, py::arg("position"))
    .def("move_pusher_from", &BoardManager::move_pusher_from, py::arg("old_position"),
         py::arg("to_new_position"))
    .def("move_pusher", &BoardManager::move_pusher, py::arg("pushers_id"),
         py::arg("to_new_position"))

    .def_property_readonly("boxes_count", &BoardManager::boxes_count)
    .def_property_readonly("boxes_ids", &BoardManager::boxes_ids)
    .def_property_readonly("boxes_positions", &BoardManager::boxes_positions)
    .def("box_position", &BoardManager::box_position, py::arg("box_id"))
    .def("box_id_on", &BoardManager::box_id_on, py::arg("position"))
    .def("has_box", &BoardManager::has_box, py::arg("box_id"))
    .def("has_box_on", &BoardManager::has_box_on, py::arg("position"))
    .def("move_box_from", &BoardManager::move_box_from, py::arg("old_position"),
         py::arg("to_new_position"))
    .def("move_box", &BoardManager::move_box, py::arg("boxes_id"),
         py::arg("to_new_position"))

    .def_property_readonly("goals_count", &BoardManager::goals_count)
    .def_property_readonly("goals_ids", &BoardManager::goals_ids)
    .def_property_readonly("goals_positions", &BoardManager::goals_positions)
    .def("goal_position", &BoardManager::goal_position, py::arg("goal_id"))
    .def("goal_id_on", &BoardManager::goal_id_on, py::arg("position"))
    .def("has_goal", &BoardManager::has_goal, py::arg("goal_id"))
    .def("has_goal_on", &BoardManager::has_goal_on, py::arg("position"))

    .def_property_readonly("walls_positions", &BoardManager::walls_positions)

    .def_property_readonly("state", &BoardManager::state)

    .def("box_plus_id", &BoardManager::box_plus_id, py::arg("box_id"))
    .def("goal_plus_id", &BoardManager::goal_plus_id, py::arg("goal_id"))

    .def_property("boxorder", &BoardManager::boxorder,
                  [](BoardManager &self, const py::object &value) {
                    if (value.is_none())
                      self.set_boxorder("");
                    else {
                      string converted = value.cast<string>();
                      self.set_boxorder(converted);
                    }
                  })

    .def_property("goalorder", &BoardManager::goalorder,
                  [](BoardManager &self, const py::object &value) {
                    if (value.is_none())
                      self.set_goalorder("");
                    else {
                      string converted = value.cast<string>();
                      self.set_goalorder(converted);
                    }
                  })

    .def_property_readonly("is_sokoban_plus_enabled",
                           &BoardManager::is_sokoban_plus_enabled)

    .def_property_readonly("is_sokoban_plus_valid",
                           &BoardManager::is_sokoban_plus_valid)

    .def("enable_sokoban_plus", &BoardManager::enable_sokoban_plus)
    .def("disable_sokoban_plus", &BoardManager::disable_sokoban_plus)

    .def("solutions", &BoardManager::solutions)

    .def_property_readonly("is_solved", &BoardManager::is_solved)

    .def("switch_boxes_and_goals", &BoardManager::switch_boxes_and_goals)
    .def_property_readonly("is_playable", &BoardManager::is_playable);

  py::class_<HashedBoardManager, BoardManager>(m, "HashedBoardManager")
    .def(py::init<BoardGraph &, const string &, const string &>(), py::arg("board"),
         py::arg("boxorder") = "", py::arg("goalorder") = "")

    .def("__str__", &HashedBoardManager::str)

    .def_property_readonly("state_hash", &HashedBoardManager::state_hash)

    .def("external_state_hash", &HashedBoardManager::external_state_hash,
         py::arg("board_state"))

    .def_property_readonly("is_solved", &HashedBoardManager::is_solved)
    .def_property_readonly("initial_state_hash",
                           &HashedBoardManager::initial_state_hash)

    .def_property_readonly("solutions_hashes", &HashedBoardManager::solutions_hashes);
}
