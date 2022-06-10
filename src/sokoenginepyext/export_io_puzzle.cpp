#include "sokoenginepyext.hpp"

using namespace std;
using namespace sokoengine;
using namespace sokoengine::io;
using namespace sokoengine::game;
using sokoengine::Strings;

void export_io_puzzle(py::module &m) {
  auto pyPuzzle = py::class_<Puzzle>(m, "Puzzle");

  pyPuzzle.def_static(
    "instance_from",
    [](const py::object &tessellation_or_description, board_size_t width,
       board_size_t height, const py::object &board) -> py::object {
      py::extract<string> string_obj(tessellation_or_description);
      py::extract<const Tessellation &> tessellation_obj(tessellation_or_description);

      string description;
      if (string_obj.check()) {
        description = string_obj();
      } else if (tessellation_obj.check()) {
        const Tessellation &tessellation = tessellation_obj();
        description = tessellation.str();
      } else
        throw std::invalid_argument(
          string() + "tessellation_or_description can't be converted to " +
          "known tessellation type");

      unique_ptr<Puzzle> puzzle;

      if (board.is_none()) {
        puzzle = Puzzle::instance_from(description, width, height);
      } else {
        string board_converted = py::extract<string>(board)();
        puzzle = Puzzle::instance_from(description, board_converted);
      }

      if (description == "sokoban") {
        auto down_casted = py::cast<unique_ptr<SokobanPuzzle>>(
          unique_ptr<SokobanPuzzle>(static_cast<SokobanPuzzle *>(puzzle.get())));
        puzzle.release();
        return down_casted;
      } else if (description == "trioban") {
        auto down_casted = py::cast<unique_ptr<TriobanPuzzle>>(
          unique_ptr<TriobanPuzzle>(static_cast<TriobanPuzzle *>(puzzle.release())));
        puzzle.release();
        return down_casted;
      } else if (description == "octoban") {
        auto down_casted = py::cast<unique_ptr<OctobanPuzzle>>(
          unique_ptr<OctobanPuzzle>(static_cast<OctobanPuzzle *>(puzzle.release())));
        puzzle.release();
        return down_casted;
      } else if (description == "hexoban") {
        auto down_casted = py::cast<unique_ptr<HexobanPuzzle>>(
          unique_ptr<HexobanPuzzle>(static_cast<HexobanPuzzle *>(puzzle.release())));
        puzzle.release();
        return down_casted;
      }
      throw std::invalid_argument("Don't know about tessellation: " + description);
    },
    py::arg("tessellation_or_description") = py::cast<string>("sokoban"),
    py::arg("width") = 0, py::arg("height") = 0, py::arg("board") = py::none());

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
  pyPuzzle.def_static("is_border_element", &Puzzle::is_border_element);
  pyPuzzle.def_static("is_puzzle_element", &Puzzle::is_puzzle_element);
  pyPuzzle.def_static("is_board", &Puzzle::is_board);
  pyPuzzle.def_static("is_sokoban_plus", &Puzzle::is_sokoban_plus);

  pyPuzzle.def_property(
    "id", [](const Puzzle &self) { return self.id(); },
    [](Puzzle &self, size_t rv) { self.id() = rv; });

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
    [](Puzzle &self, const Strings &rv) { self.notes() = rv; });

  pyPuzzle.def_property(
    "created_at", [](const Puzzle &self) { return self.created_at(); },
    [](Puzzle &self, const string &rv) { self.created_at() = rv; });

  pyPuzzle.def_property(
    "updated_at", [](const Puzzle &self) { return self.updated_at(); },
    [](Puzzle &self, const string &rv) { self.updated_at() = rv; });

  pyPuzzle.def_property(
    "snapshots", [](const Puzzle &self) { return self.snapshots(); },
    [](Puzzle &self, const Snapshots &rv) { self.snapshots() = rv; });

  pyPuzzle.def_property(
    "board", [](const Puzzle &self) { return self.board(); },
    [](Puzzle &self, const string &rv) { self.set_board(rv); });

  pyPuzzle.def_property_readonly("tessellation", &Puzzle::tessellation,
                                 py::return_value_policy::reference);

  pyPuzzle.def(
    "__getitem__",
    [](const Puzzle &self, position_t position) -> char { return self.at(position); },
    py::arg("position"));

  pyPuzzle.def(
    "__setitem__",
    [](Puzzle &self, position_t position, char c) { self.set_at(position, c); },
    py::arg("position"), py::arg("char"));

  pyPuzzle.def("__str__", &Puzzle::str);
  pyPuzzle.def("__repr__", &Puzzle::repr);
  pyPuzzle.def("to_board_str", &Puzzle::to_board_str,
               py::arg("use_visible_floor") = false, py::arg("rle_encode") = false);
  pyPuzzle.def_property_readonly("internal_board", &Puzzle::internal_board);

  pyPuzzle.def_property_readonly("width", &Puzzle::width);
  pyPuzzle.def_property_readonly("height", &Puzzle::height);
  pyPuzzle.def_property_readonly("size", &Puzzle::size);
  pyPuzzle.def_property_readonly("pushers_count", &Puzzle::pushers_count);
  pyPuzzle.def_property_readonly("boxes_count", &Puzzle::boxes_count);
  pyPuzzle.def_property_readonly("goals_count", &Puzzle::goals_count);

  pyPuzzle.def("add_row_top", &Puzzle::add_row_top);
  pyPuzzle.def("add_row_bottom", &Puzzle::add_row_bottom);
  pyPuzzle.def("add_column_left", &Puzzle::add_column_left);
  pyPuzzle.def("add_column_right", &Puzzle::add_column_right);
  pyPuzzle.def("remove_row_top", &Puzzle::remove_row_top);
  pyPuzzle.def("remove_row_bottom", &Puzzle::remove_row_bottom);
  pyPuzzle.def("remove_column_left", &Puzzle::remove_column_left);
  pyPuzzle.def("remove_column_right", &Puzzle::remove_column_right);
  pyPuzzle.def("trim_left", &Puzzle::trim_left);
  pyPuzzle.def("trim_right", &Puzzle::trim_right);
  pyPuzzle.def("trim_top", &Puzzle::trim_top);
  pyPuzzle.def("trim_bottom", &Puzzle::trim_bottom);
  pyPuzzle.def("reverse_rows", &Puzzle::reverse_rows);
  pyPuzzle.def("reverse_columns", &Puzzle::reverse_columns);
  pyPuzzle.def("resize", &Puzzle::resize, py::arg("new_width"), py::arg("new_height"));
  pyPuzzle.def("resize_and_center", &Puzzle::resize_and_center, py::arg("new_width"),
               py::arg("new_height"));
  pyPuzzle.def("trim", &Puzzle::trim);

  auto pySokobanPuzzle =
    py::class_<SokobanPuzzle, Puzzle>(m, "SokobanPuzzle", py::is_final());
  auto pyTriobanPuzzle =
    py::class_<TriobanPuzzle, Puzzle>(m, "TriobanPuzzle", py::is_final());
  auto pyOctobanPuzzle =
    py::class_<OctobanPuzzle, Puzzle>(m, "OctobanPuzzle", py::is_final());
  auto pyHexobanPuzzle =
    py::class_<HexobanPuzzle, Puzzle>(m, "HexobanPuzzle", py::is_final());

  pySokobanPuzzle.def(
    py::init([](board_size_t width, board_size_t height, const py::object &board) {
      if (board.is_none()) return make_unique<SokobanPuzzle>(width, height);
      string board_converted = board.cast<string>();
      return make_unique<SokobanPuzzle>(board_converted);
    }),
    py::arg("width") = 0, py::arg("height") = 0, py::arg("board") = py::none());

  pyHexobanPuzzle.def(
    py::init([](board_size_t width, board_size_t height, const py::object &board) {
      if (board.is_none()) return make_unique<HexobanPuzzle>(width, height);
      string board_converted = board.cast<string>();
      return make_unique<HexobanPuzzle>(board_converted);
    }),
    py::arg("width") = 0, py::arg("height") = 0, py::arg("board") = py::none());

  pyTriobanPuzzle.def(
    py::init([](board_size_t width, board_size_t height, const py::object &board) {
      if (board.is_none()) return make_unique<TriobanPuzzle>(width, height);
      string board_converted = board.cast<string>();
      return make_unique<TriobanPuzzle>(board_converted);
    }),
    py::arg("width") = 0, py::arg("height") = 0, py::arg("board") = py::none());

  pyOctobanPuzzle.def(
    py::init([](board_size_t width, board_size_t height, const py::object &board) {
      if (board.is_none()) return make_unique<OctobanPuzzle>(width, height);
      string board_converted = board.cast<string>();
      return make_unique<OctobanPuzzle>(board_converted);
    }),
    py::arg("width") = 0, py::arg("height") = 0, py::arg("board") = py::none());
}
