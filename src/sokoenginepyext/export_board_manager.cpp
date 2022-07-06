#include "sokoenginepyext.hpp"

using sokoengine::position_t;
using sokoengine::game::BoardGraph;
using sokoengine::game::BoardManager;
using sokoengine::game::BoardState;
using sokoengine::game::HashedBoardManager;
using sokoengine::game::piece_id_t;
using sokoengine::game::Positions;
using sokoengine::game::Selectors;
using sokoengine::game::zobrist_key_t;
using std::string;

void export_board_manager(py::module &m) {
  py::class_<BoardState>(m, "BoardState")
    .def(
      py::init<const Positions &, const Positions &, zobrist_key_t>(),
      py::arg("pushers_positions") = Positions(),
      py::arg("boxes_positions")   = Positions(),
      py::arg("zobrist_hash")      = BoardState::NO_HASH
    )

    // protocols
    .def("__eq__", &BoardState::operator==)
    .def("__ne__", &BoardState::operator!=)
    .def("__str__", &BoardState::str)
    .def("__repr__", &BoardState::repr)

    .def_property(
      "pushers_positions",
      [](const BoardState &self) {
        return self.pushers_positions();
      },
      [](BoardState &self, const Positions &rv) {
        self.pushers_positions() = rv;
      }
    )

    .def_property(
      "boxes_positions",
      [](const BoardState &self) {
        return self.boxes_positions();
      },
      [](BoardState &self, const Positions &rv) {
        self.boxes_positions() = rv;
      }
    )

    .def_property(
      "zobrist_hash",
      [](BoardState &self) {
        return self.zobrist_hash();
      },
      [](BoardState &self, zobrist_key_t rv) {
        self.zobrist_hash() = rv;
      }
    );

  py::class_<BoardManager>(m, "BoardManager")
    .def(
      py::init<BoardGraph &, const string &, const string &>(),
      py::arg("board"),
      py::arg("boxorder")  = "",
      py::arg("goalorder") = ""
    )

    // protocols
    .def("__str__", &BoardManager::str)

    // --------------------------------------------------------------------------
    // Pushers
    // --------------------------------------------------------------------------
    .def_property_readonly("pushers_count", &BoardManager::pushers_count)
    .def_property_readonly("pushers_ids", &BoardManager::pushers_ids)
    .def_property_readonly("pushers_positions", &BoardManager::pushers_positions)
    .def(
      "pusher_position",
      [](BoardManager &self, py_int_t pusher_id) {
        return self.pusher_position(piece_or_throw(Selectors::PUSHERS, pusher_id));
      },
      py::arg("pusher_id")
    )
    .def(
      "pusher_id_on",
      [](BoardManager &self, py_int_t position) {
        return self.pusher_id_on(position_or_throw(position));
      },
      py::arg("position")
    )
    .def(
      "has_pusher",
      [](BoardManager &self, py_int_t pusher_id) {
        if (pusher_id < 0 || pusher_id >= std::numeric_limits<piece_id_t>::max())
          return false;
        return self.has_pusher(static_cast<piece_id_t>(pusher_id));
      },
      py::arg("pusher_id")
    )
    .def(
      "has_pusher_on",
      [](BoardManager &self, py_int_t position) {
        if (position < 0 || position >= std::numeric_limits<position_t>::max())
          return false;
        return self.has_pusher_on(static_cast<position_t>(position));
      },
      py::arg("position")
    )
    .def(
      "move_pusher_from",
      [](BoardManager &self, py_int_t old_position, py_int_t to_new_position) {
        return self.move_pusher_from(
          position_or_throw(old_position), position_or_throw(to_new_position)
        );
      },
      py::arg("old_position"),
      py::arg("to_new_position")
    )
    .def(
      "move_pusher",
      [](BoardManager &self, py_int_t pusher_id, py_int_t to_new_position) {
        return self.move_pusher(
          piece_or_throw(Selectors::PUSHERS, pusher_id),
          position_or_throw(to_new_position)
        );
      },
      py::arg("pusher_id"),
      py::arg("to_new_position")
    )

    // --------------------------------------------------------------------------
    // Boxes
    // --------------------------------------------------------------------------
    .def_property_readonly("boxes_count", &BoardManager::boxes_count)
    .def_property_readonly("boxes_ids", &BoardManager::boxes_ids)
    .def_property_readonly("boxes_positions", &BoardManager::boxes_positions)
    .def(
      "box_position",
      [](BoardManager &self, py_int_t box_id) {
        return self.box_position(piece_or_throw(Selectors::BOXES, box_id));
      },
      py::arg("box_id")
    )
    .def(
      "box_id_on",
      [](BoardManager &self, py_int_t position) {
        return self.box_id_on(position_or_throw(position));
      },
      py::arg("position")
    )
    .def(
      "has_box",
      [](BoardManager &self, py_int_t box_id) {
        if (box_id < 0 || box_id >= std::numeric_limits<piece_id_t>::max())
          return false;
        return self.has_box(static_cast<piece_id_t>(box_id));
      },
      py::arg("box_id")
    )
    .def(
      "has_box_on",
      [](BoardManager &self, py_int_t position) {
        if (position < 0 || position >= std::numeric_limits<position_t>::max())
          return false;
        return self.has_box_on(static_cast<position_t>(position));
      },
      py::arg("position")
    )
    .def(
      "move_box_from",
      [](BoardManager &self, py_int_t old_position, py_int_t to_new_position) {
        return self.move_box_from(
          position_or_throw(old_position), position_or_throw(to_new_position)
        );
      },
      py::arg("old_position"),
      py::arg("to_new_position")
    )
    .def(
      "move_box",
      [](BoardManager &self, py_int_t box_id, py_int_t to_new_position) {
        return self.move_box(
          piece_or_throw(Selectors::BOXES, box_id), position_or_throw(to_new_position)
        );
      },
      py::arg("box_id"),
      py::arg("to_new_position")
    )

    // --------------------------------------------------------------------------
    // Goals
    // --------------------------------------------------------------------------
    .def_property_readonly("goals_count", &BoardManager::goals_count)
    .def_property_readonly("goals_ids", &BoardManager::goals_ids)
    .def_property_readonly("goals_positions", &BoardManager::goals_positions)
    .def(
      "goal_position",
      [](BoardManager &self, py_int_t goal_id) {
        return self.goal_position(piece_or_throw(Selectors::GOALS, goal_id));
      },
      py::arg("goal_id")
    )
    .def(
      "goal_id_on",
      [](BoardManager &self, py_int_t position) {
        return self.goal_id_on(position_or_throw(position));
      },
      py::arg("position")
    )
    .def(
      "has_goal",
      [](BoardManager &self, py_int_t goal_id) {
        if (goal_id < 0 || goal_id >= std::numeric_limits<piece_id_t>::max())
          return false;
        return self.has_goal(static_cast<piece_id_t>(goal_id));
      },
      py::arg("goal_id")
    )
    .def(
      "has_goal_on",
      [](BoardManager &self, py_int_t position) {
        if (position < 0 || position >= std::numeric_limits<position_t>::max())
          return false;
        return self.has_goal_on(static_cast<position_t>(position));
      },
      py::arg("position")
    )

    // --------------------------------------------------------------------------
    // Sokoban+
    // --------------------------------------------------------------------------
    .def(
      "box_plus_id",
      [](BoardManager &self, py_int_t box_id) {
        return self.box_plus_id(piece_or_throw(Selectors::BOXES, box_id));
      },
      py::arg("box_id")
    )
    .def(
      "goal_plus_id",
      [](BoardManager &self, py_int_t goal_id) {
        return self.goal_plus_id(piece_or_throw(Selectors::GOALS, goal_id));
      },
      py::arg("goal_id")
    )

    .def_property("boxorder", &BoardManager::boxorder, &BoardManager::set_boxorder)
    .def_property("goalorder", &BoardManager::goalorder, &BoardManager::set_goalorder)

    .def_property_readonly(
      "is_sokoban_plus_enabled", &BoardManager::is_sokoban_plus_enabled
    )
    .def_property_readonly(
      "is_sokoban_plus_valid", &BoardManager::is_sokoban_plus_valid
    )

    .def("enable_sokoban_plus", &BoardManager::enable_sokoban_plus)
    .def("disable_sokoban_plus", &BoardManager::disable_sokoban_plus)

    // --------------------------------------------------------------------------
    // Board state
    // --------------------------------------------------------------------------

    .def_property_readonly(
      "board", &BoardManager::board, py::return_value_policy::reference
    )
    .def_property_readonly("walls_positions", &BoardManager::walls_positions)
    .def_property_readonly("state", &BoardManager::state)

    .def("solutions", &BoardManager::solutions)

    .def_property_readonly("is_solved", &BoardManager::is_solved)

    .def("switch_boxes_and_goals", &BoardManager::switch_boxes_and_goals)
    .def_property_readonly("is_playable", &BoardManager::is_playable);

  py::class_<HashedBoardManager, BoardManager>(m, "HashedBoardManager")
    .def(
      py::init<BoardGraph &, const string &, const string &>(),
      py::arg("board"),
      py::arg("boxorder")  = "",
      py::arg("goalorder") = ""
    )

    .def("__str__", &HashedBoardManager::str)

    .def_property_readonly("state_hash", &HashedBoardManager::state_hash)

    .def(
      "external_state_hash",
      &HashedBoardManager::external_state_hash,
      py::arg("board_state")
    )

    .def_property_readonly("is_solved", &HashedBoardManager::is_solved)
    .def_property_readonly(
      "initial_state_hash", &HashedBoardManager::initial_state_hash
    )

    .def_property_readonly("solutions_hashes", &HashedBoardManager::solutions_hashes);
}
