#include "sokoenginepyext.hpp"

using namespace std;
using namespace sokoengine;

void export_board_manager(py::module& m) {
  py::class_<BoardState>(m, "BoardState")
    .def(
      py::init(
        [](
          const py::list& pushers_positions, const py::list& boxes_positions,
          const py::object& zobrist_hash
        ) {
          Positions pushers_positions_native;
          for (auto val : pushers_positions)
            pushers_positions_native.push_back(val.cast<position_t>());

          Positions boxes_positions_native;
          for (auto val : boxes_positions)
            boxes_positions_native.push_back(val.cast<position_t>());

          zobrist_key_t zobrist_hash_native;
          if (zobrist_hash.is_none()) zobrist_hash_native = 0;
          else zobrist_hash_native = zobrist_hash.cast<zobrist_key_t>();

          return make_unique<BoardState>(
            pushers_positions_native, boxes_positions_native,
            zobrist_hash_native
          );
        }
      ),
      py::arg("pushers_positions")=py::none(),
      py::arg("boxes_positions")=py::none(),
      py::arg("zobrist_hash")=py::none()
    )

    // protocols
    .def("__eq__", &BoardState::operator==)
    .def("__ne__", &BoardState::operator!=)
    .def("__str__", &BoardState::str)
    .def("__repr__", &BoardState::repr)

    .def_property(
      "pushers_positions",
      [](BoardState& self) {
        auto native_retv = self.pushers_positions();
        py::list retv;
        for (auto val : native_retv) retv.append(val);
        return retv;
      },
      [](BoardState& self, const py::list& rv) {
        self.pushers_positions() = Positions();
        if (!rv.is_none()) {
          for (auto val : rv)
            self.pushers_positions().push_back(val.cast<position_t>());
        }
      }
    )

    .def_property(
      "boxes_positions",
      [](BoardState& self) {
        auto native_retv = self.boxes_positions();
        py::list retv;
        for (auto val : native_retv) retv.append(val);
        return retv;
      },
      [](BoardState& self, const py::list& rv) {
        self.boxes_positions() = Positions();
        if (!rv.is_none()) {
          for (auto val : rv)
            self.boxes_positions().push_back(val.cast<position_t>());
        }
      }
    )

    .def_property(
      "zobrist_hash",
      [](BoardState& self) {
        return self.zobrist_hash();
      },
      [](BoardState& self, const py::object& rv) {
        if (rv.is_none()) self.zobrist_hash() = 0;
        else self.zobrist_hash() = rv.cast<zobrist_key_t>();
      }
    )
  ;

  py::class_<BoardManager>(m, "BoardManager")
    .def(py::init<VariantBoard&>(), py::arg("variant_board"))

    // protocols
    .def("__eq__", &BoardManager::operator==)
    .def("__ne__", &BoardManager::operator!=)
    .def("__str__", &BoardManager::str)
    .def("__repr__", &BoardManager::repr)

    .def_property_readonly(
      "board", &BoardManager::board, py::return_value_policy::reference
    )

    .def_property_readonly("pushers_count", &BoardManager::pushers_count)

    .def_property_readonly(
      "pushers_ids", [](const BoardManager& self) {
        auto native_retv = self.pushers_ids();
        py::list retv;
        for (auto id : native_retv) retv.append(id);
        return retv;
      }
    )

    .def_property_readonly(
      "pushers_positions", [](const BoardManager& self) {
        auto native_retv = self.pushers_positions();
        py::dict retv;
        for (auto pusher : native_retv) retv[py::int_(pusher.first)] = pusher.second;
        return retv;
      }
    )

    .def("pusher_position", &BoardManager::pusher_position, py::arg("pusher_id"))
    .def("pusher_id_on", &BoardManager::pusher_id_on, py::arg("position"))
    .def("has_pusher", &BoardManager::has_pusher, py::arg("pusher_id"))
    .def("has_pusher_on", &BoardManager::has_pusher_on, py::arg("position"))

    .def(
      "move_pusher_from", &BoardManager::move_pusher_from,
      py::arg("old_position"), py::arg("to_new_position")
    )

    .def(
      "move_pusher", &BoardManager::move_pusher,
      py::arg("pushers_id"), py::arg("to_new_position")
    )

    .def_property_readonly("boxes_count", &BoardManager::boxes_count)

    .def_property_readonly(
      "boxes_ids", [](const BoardManager& self) {
        auto native_retv = self.boxes_ids();
        py::list retv;
        for (auto id : native_retv) retv.append(id);
        return retv;
      }
    )

    .def_property_readonly(
      "boxes_positions", [](const BoardManager& self) {
        auto native_retv = self.boxes_positions();
        py::dict retv;
        for (auto box : native_retv) retv[py::int_(box.first)] = box.second;
        return retv;
      }
    )

    .def("box_position", &BoardManager::box_position, py::arg("box_id"))
    .def("box_id_on", &BoardManager::box_id_on, py::arg("position"))
    .def("has_box", &BoardManager::has_box, py::arg("box_id"))

    .def(
      "has_box_on", [](const BoardManager& self, const py::object& position) {
        if (position.is_none()) return false;
        return self.has_box_on(position.cast<position_t>());
      },
      py::arg("position")
    )

    .def(
      "move_box_from", &BoardManager::move_box_from,
      py::arg("old_position"), py::arg("to_new_position")
    )

    .def(
      "move_box", &BoardManager::move_box,
      py::arg("boxes_id"), py::arg("to_new_position")
    )

    .def_property_readonly("goals_count", &BoardManager::goals_count)

    .def_property_readonly(
      "goals_ids", [](const BoardManager& self) {
        auto native_retv = self.goals_ids();
        py::list retv;
        for (auto id : native_retv) retv.append(id);
        return retv;
      }
    )

    .def_property_readonly(
      "goals_positions", [](const BoardManager& self) {
        auto native_retv = self.goals_positions();
        py::dict retv;
        for (auto goal : native_retv) retv[py::int_(goal.first)] = goal.second;
        return retv;
      }
    )

    .def("goal_position", &BoardManager::goal_position, py::arg("goal_id"))
    .def("goal_id_on", &BoardManager::goal_id_on, py::arg("position"))
    .def("has_goal", &BoardManager::has_goal, py::arg("goal_id"))
    .def("has_goal_on", &BoardManager::has_goal_on, py::arg("position"))
    .def_property_readonly("state", &BoardManager::state)

    .def("box_plus_id", &BoardManager::box_plus_id, py::arg("box_id"))
    .def("goal_plus_id", &BoardManager::goal_plus_id, py::arg("goal_id"))

    .def_property(
      "boxorder", &BoardManager::boxorder,
      [](BoardManager& self, const py::object& value) {
        if (value.is_none())
          self.set_boxorder("");
        else {
          string converted = value.cast<string>();
          self.set_boxorder(converted);
        }
      }
    )

    .def_property(
      "goalorder", &BoardManager::goalorder,
      [](BoardManager& self, const py::object& value) {
        if (value.is_none())
          self.set_goalorder("");
        else {
          string converted = value.cast<string>();
          self.set_goalorder(converted);
        }
      }
    )

    .def_property_readonly(
      "is_sokoban_plus_enabled", &BoardManager::is_sokoban_plus_enabled
    )

    .def_property_readonly(
      "is_sokoban_plus_valid", &BoardManager::is_sokoban_plus_valid
    )

    .def("enable_sokoban_plus", &BoardManager::enable_sokoban_plus)
    .def("disable_sokoban_plus", &BoardManager::disable_sokoban_plus)

    .def(
      "solutions", [](const BoardManager& self) {
        auto native_retv = self.solutions();

        py::list retv;
        for (auto i = native_retv.begin(); i != native_retv.end(); ++i) {
          py::dict d;
          for (auto j = (*i).begin(); j != (*i).end(); j++) {
            d[py::int_(j->first)] = j->second;
          }
          retv.append(d);
        }

        return retv;
      }
    )

    .def("switch_boxes_and_goals", &BoardManager::switch_boxes_and_goals)
    .def_property_readonly("is_playable", &BoardManager::is_playable)
  ;

  py::class_<HashedBoardManager, BoardManager>(m, "HashedBoardManager")
    .def(py::init<VariantBoard&>(), py::arg("variant_board"))

    .def("__eq__", &HashedBoardManager::operator==)
    .def("__ne__", &HashedBoardManager::operator!=)
    .def("__str__", &HashedBoardManager::str)
    .def("__repr__", &HashedBoardManager::repr)

    .def_property_readonly(
      "boxes_layout_hash", &HashedBoardManager::boxes_layout_hash
    )

    .def_property_readonly(
      "boxes_and_pushers_layout_hash",
      &HashedBoardManager::boxes_and_pushers_layout_hash
    )

    .def(
      "external_position_hash",
      &HashedBoardManager::external_position_hash,
      py::arg("boxes_positions")
    )

    .def("is_solved", &HashedBoardManager::is_solved)

    .def_property_readonly(
      "solution_hashes", [](const HashedBoardManager& self) {
        auto native_retv = self.solution_hashes();
        py::list retv;
        for (auto val : native_retv) retv.append(val);
        return retv;
      }
    )
  ;
}
