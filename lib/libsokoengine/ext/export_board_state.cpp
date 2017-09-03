#include <pybind11/pybind11.h>
#include <sokoengine.hpp>

using namespace std;
namespace py = pybind11;
using namespace sokoengine;

void export_board_state(py::module& m) {
  py::class_<BoardState>(m, "BoardState")
    .def(py::init<VariantBoard&>(), py::arg("variant_board"))

    // protocols
    .def("__eq__", &BoardState::operator==)
    .def("__ne__", &BoardState::operator!=)
    .def("__str__", &BoardState::str)
    .def("__repr__", &BoardState::repr)

    .def_property_readonly(
      "board", &BoardState::board, py::return_value_policy::reference
    )

    .def_property_readonly("pushers_count", &BoardState::pushers_count)

    .def_property_readonly(
      "pushers_ids", [](const BoardState& self) {
        auto native_retv = self.pushers_ids();
        py::list retv;
        for (auto id : native_retv) retv.append(id);
        return retv;
      }
    )

    .def_property_readonly(
      "pushers_positions", [](const BoardState& self) {
        auto native_retv = self.pushers_positions();
        py::dict retv;
        for (auto pusher : native_retv) retv[py::int_(pusher.first)] = pusher.second;
        return retv;
      }
    )

    .def("pusher_position", &BoardState::pusher_position, py::arg("pusher_id"))
    .def("pusher_id_on", &BoardState::pusher_id_on, py::arg("position"))
    .def("has_pusher", &BoardState::has_pusher, py::arg("pusher_id"))
    .def("has_pusher_on", &BoardState::has_pusher_on, py::arg("position"))

    .def(
      "move_pusher_from", &BoardState::move_pusher_from,
      py::arg("old_position"), py::arg("to_new_position")
    )

    .def(
      "move_pusher", &BoardState::move_pusher,
      py::arg("pushers_id"), py::arg("to_new_position")
    )

    .def_property_readonly("boxes_count", &BoardState::boxes_count)

    .def_property_readonly(
      "boxes_ids", [](const BoardState& self) {
        auto native_retv = self.boxes_ids();
        py::list retv;
        for (auto id : native_retv) retv.append(id);
        return retv;
      }
    )

    .def_property_readonly(
      "boxes_positions", [](const BoardState& self) {
        auto native_retv = self.boxes_positions();
        py::dict retv;
        for (auto box : native_retv) retv[py::int_(box.first)] = box.second;
        return retv;
      }
    )

    .def("box_position", &BoardState::box_position, py::arg("box_id"))
    .def("box_id_on", &BoardState::box_id_on, py::arg("position"))
    .def("has_box", &BoardState::has_box, py::arg("box_id"))

    .def(
      "has_box_on", [](const BoardState& self, const py::object& position) {
        if (position.is_none()) return false;
        else return self.has_box_on(position.cast<position_t>());
      },
      py::arg("position")
    )

    .def(
      "move_box_from", &BoardState::move_box_from,
      py::arg("old_position"), py::arg("to_new_position")
    )

    .def(
      "move_box", &BoardState::move_box,
      py::arg("boxes_id"), py::arg("to_new_position")
    )

    .def_property_readonly("goals_count", &BoardState::goals_count)

    .def_property_readonly(
      "goals_ids", [](const BoardState& self) {
        auto native_retv = self.goals_ids();
        py::list retv;
        for (auto id : native_retv) retv.append(id);
        return retv;
      }
    )

    .def_property_readonly(
      "goals_positions", [](const BoardState& self) {
        auto native_retv = self.goals_positions();
        py::dict retv;
        for (auto goal : native_retv) retv[py::int_(goal.first)] = goal.second;
        return retv;
      }
    )

    .def("goal_position", &BoardState::goal_position, py::arg("goal_id"))
    .def("goal_id_on", &BoardState::goal_id_on, py::arg("position"))
    .def("has_goal", &BoardState::has_goal, py::arg("goal_id"))
    .def("has_goal_on", &BoardState::has_goal_on, py::arg("position"))
    .def("box_plus_id", &BoardState::box_plus_id, py::arg("box_id"))
    .def("goal_plus_id", &BoardState::goal_plus_id, py::arg("goal_id"))

    .def_property(
      "boxorder", &BoardState::boxorder,
      [](BoardState& self, const py::object& value) {
        if (value.is_none())
          self.set_boxorder("");
        else {
          string converted = value.cast<string>();
          self.set_boxorder(converted);
        }
      }
    )

    .def_property(
      "goalorder", &BoardState::goalorder,
      [](BoardState& self, const py::object& value) {
        if (value.is_none())
          self.set_goalorder("");
        else {
          string converted = value.cast<string>();
          self.set_goalorder(converted);
        }
      }
    )

    .def_property_readonly(
      "is_sokoban_plus_enabled", &BoardState::is_sokoban_plus_enabled
    )

    .def_property_readonly(
      "is_sokoban_plus_valid", &BoardState::is_sokoban_plus_valid
    )

    .def("enable_sokoban_plus", &BoardState::enable_sokoban_plus)
    .def("disable_sokoban_plus", &BoardState::disable_sokoban_plus)

    .def(
      "solutions", [](const BoardState& self) {
        auto native_retv = self.solutions();

        py::list retv;
        for (auto i = native_retv.begin(); i != native_retv.end(); ++i) {
          py::dict d;
          for(auto j = (*i).begin(); j != (*i).end(); j++) {
            d[py::int_(j->first)] = j->second;
          }
          retv.append(d);
        }

        return retv;
      }
    )

    .def("switch_boxes_and_goals", &BoardState::switch_boxes_and_goals)
    .def_property_readonly("is_playable", &BoardState::is_playable)
  ;

  py::class_<HashedBoardState, BoardState>(m, "HashedBoardState")
    .def(py::init<VariantBoard&>(), py::arg("variant_board"))

    .def("__eq__", &HashedBoardState::operator==)
    .def("__ne__", &HashedBoardState::operator!=)
    .def("__str__", &HashedBoardState::str)
    .def("__repr__", &HashedBoardState::repr)

    .def_property_readonly(
      "boxes_layout_hash", &HashedBoardState::boxes_layout_hash
    )

    .def_property_readonly(
      "boxes_and_pushers_layout_hash",
      &HashedBoardState::boxes_and_pushers_layout_hash
    )

    .def(
      "external_position_hash",
      &HashedBoardState::external_position_hash,
      py::arg("boxes_positions")
    )

    .def("is_solved", &HashedBoardState::is_solved)

    .def_property_readonly(
      "solution_hashes", [](const HashedBoardState& self) {
        auto native_retv = self.solution_hashes();
        py::list retv;
        for (auto val : native_retv) retv.append(val);
        return retv;
      }
    )
  ;
}
