#include "sokoenginepyext.hpp"

using namespace std;
using namespace sokoengine::io;

void export_io_puzzle(py::module &m) {
  auto pyPuzzle = py::class_<Puzzle>(m, "Puzzle");

  pyPuzzle.def(py::init<size_t, string, string, string, string, string, string, string,
                        string, PuzzleTypes>(),
               py::arg("id") = 0, py::arg("board") = "", py::arg("title") = "",
               py::arg("author") = "", py::arg("boxorder") = "",
               py::arg("goalorder") = "", py::arg("notes") = "",
               py::arg("created_at") = "", py::arg("updated_at") = "",
               py::arg("puzzle_type") = PuzzleTypes::SOKOBAN);

  pyPuzzle.def_readonly_static("WALL", &Puzzle::WALL);
  pyPuzzle.def_readonly_static("PUSHER", &Puzzle::PUSHER);
  pyPuzzle.def_readonly_static("PUSHER_ON_GOAL", &Puzzle::PUSHER_ON_GOAL);
  pyPuzzle.def_readonly_static("BOX", &Puzzle::BOX);
  pyPuzzle.def_readonly_static("BOX_ON_GOAL", &Puzzle::BOX_ON_GOAL);
  pyPuzzle.def_readonly_static("GOAL", &Puzzle::GOAL);
  pyPuzzle.def_readonly_static("FLOOR", &Puzzle::FLOOR);
  pyPuzzle.def_readonly_static("VISIBLE_FLOOR", &Puzzle::VISIBLE_FLOOR);
  pyPuzzle.def_readonly_static("ALT_PUSHER1", &Puzzle::ALT_PUSHER1);
  pyPuzzle.def_readonly_static("ALT_PUSHER2", &Puzzle::ALT_PUSHER2);
  pyPuzzle.def_readonly_static("ALT_PUSHER_ON_GOAL1", &Puzzle::ALT_PUSHER_ON_GOAL1);
  pyPuzzle.def_readonly_static("ALT_PUSHER_ON_GOAL2", &Puzzle::ALT_PUSHER_ON_GOAL2);
  pyPuzzle.def_readonly_static("ALT_BOX1", &Puzzle::ALT_BOX1);
  pyPuzzle.def_readonly_static("ALT_BOX_ON_GOAL1", &Puzzle::ALT_BOX_ON_GOAL1);
  pyPuzzle.def_readonly_static("ALT_GOAL1", &Puzzle::ALT_GOAL1);
  pyPuzzle.def_readonly_static("ALT_VISIBLE_FLOOR1", &Puzzle::ALT_VISIBLE_FLOOR1);

  pyPuzzle.def_static("is_pusher", &Puzzle::is_pusher);
  pyPuzzle.def_static("is_box", &Puzzle::is_box);
  pyPuzzle.def_static("is_goal", &Puzzle::is_goal);
  pyPuzzle.def_static("is_empty_floor", &Puzzle::is_empty_floor);
  pyPuzzle.def_static("is_wall", &Puzzle::is_wall);
  pyPuzzle.def_static("is_board", &Puzzle::is_board);
  pyPuzzle.def_static("is_sokoban_plus", &Puzzle::is_sokoban_plus);

  pyPuzzle.def("clear", &Puzzle::clear);

  pyPuzzle.def_property(
    "id", [](const Puzzle &self) { return self.id(); },
    [](Puzzle &self, size_t rv) { self.id() = rv; });

  pyPuzzle.def_property(
    "puzzle_type", [](const Puzzle &self) { return self.puzzle_type(); },
    [](Puzzle &self, PuzzleTypes rv) { self.puzzle_type() = rv; });

  pyPuzzle.def_property(
    "board", [](const Puzzle &self) { return self.board(); },
    [](Puzzle &self, const string &rv) { self.board() = rv; });

  pyPuzzle.def_property(
    "title", [](const Puzzle &self) { return self.title(); },
    [](Puzzle &self, const string &rv) { self.title() = rv; });

  pyPuzzle.def_property(
    "author", [](const Puzzle &self) { return self.author(); },
    [](Puzzle &self, const string &rv) { self.author() = rv; });

  pyPuzzle.def_property(
    "boxorder", [](const Puzzle &self) { return self.boxorder(); },
    [](Puzzle &self, const string &rv) { self.boxorder() = rv; });

  pyPuzzle.def_property(
    "goalorder", [](const Puzzle &self) { return self.goalorder(); },
    [](Puzzle &self, const string &rv) { self.goalorder() = rv; });

  pyPuzzle.def_property(
    "notes", [](const Puzzle &self) { return self.notes(); },
    [](Puzzle &self, const string &rv) { self.notes() = rv; });

  pyPuzzle.def_property(
    "created_at", [](const Puzzle &self) { return self.created_at(); },
    [](Puzzle &self, const string &rv) { self.created_at() = rv; });

  pyPuzzle.def_property(
    "updated_at", [](const Puzzle &self) { return self.updated_at(); },
    [](Puzzle &self, const string &rv) { self.updated_at() = rv; });

  pyPuzzle.def_property(
    "snapshots", [](const Puzzle &self) { return self.snapshots(); },
    [](Puzzle &self, const Snapshots &rv) { self.snapshots() = rv; });

  pyPuzzle.def_property_readonly("pushers_count", &Puzzle::pushers_count);
  pyPuzzle.def_property_readonly("boxes_count", &Puzzle::boxes_count);
  pyPuzzle.def_property_readonly("goals_count", &Puzzle::goals_count);

  pyPuzzle.def("reformatted", &Puzzle::reformatted,
               py::arg("use_visible_floor") = false,
               py::arg("break_long_lines_at") = 80, py::arg("rle_encode") = false);
}
