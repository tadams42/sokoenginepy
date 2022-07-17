#include "sokoenginepyext.hpp"

using sokoengine::board_size_t;
using sokoengine::CellOrientation;
using sokoengine::position_t;
using sokoengine::Tessellation;
using sokoengine::Puzzle;
using sokoengine::Snapshots;
using std::make_unique;
using std::string;

void export_io_puzzle(py::module &m) {
  py::enum_<CellOrientation>(m, "CellOrientation")
    .value("DEFAULT", CellOrientation::DEFAULT)
    .value("TRIANGLE_DOWN", CellOrientation::TRIANGLE_DOWN)
    .value("OCTAGON", CellOrientation::OCTAGON);

  auto pyPuzzle = py::class_<Puzzle>(m, "Puzzle", py::is_final());

  pyPuzzle.def(
    py::init([](
               Tessellation      tessellation,
               py_int_t          width,
               py_int_t          height,
               const py::object &board
             ) {
      if (board.is_none())
        return make_unique<Puzzle>(
          tessellation, size_or_throw(width), size_or_throw(height)
        );
      string board_converted = board.cast<string>();
      return make_unique<Puzzle>(tessellation, board_converted);
    }),
    py::arg("tessellation"),
    py::arg("width")  = 0,
    py::arg("height") = 0,
    py::arg("board")  = py::none()
  );

  pyPuzzle.def_readonly_static("WALL", &Puzzle::WALL);
  pyPuzzle.def_readonly_static("PUSHER", &Puzzle::PUSHER);
  pyPuzzle.def_readonly_static("PUSHER_ON_GOAL", &Puzzle::PUSHER_ON_GOAL);
  pyPuzzle.def_readonly_static("BOX", &Puzzle::BOX);
  pyPuzzle.def_readonly_static("BOX_ON_GOAL", &Puzzle::BOX_ON_GOAL);
  pyPuzzle.def_readonly_static("GOAL", &Puzzle::GOAL);
  pyPuzzle.def_readonly_static("FLOOR", &Puzzle::FLOOR);
  pyPuzzle.def_readonly_static("VISIBLE_FLOOR", &Puzzle::VISIBLE_FLOOR);

  pyPuzzle.def_property(
    "title",
    [](const Puzzle &self) {
      return self.title();
    },
    [](Puzzle &self, const string &rv) {
      self.title() = rv;
    }
  );

  pyPuzzle.def_property(
    "author",
    [](const Puzzle &self) {
      return self.author();
    },
    [](Puzzle &self, const string &rv) {
      self.author() = rv;
    }
  );

  pyPuzzle.def_property(
    "boxorder",
    [](const Puzzle &self) {
      return self.boxorder();
    },
    [](Puzzle &self, const string &rv) {
      self.boxorder() = rv;
    }
  );

  pyPuzzle.def_property(
    "goalorder",
    [](const Puzzle &self) {
      return self.goalorder();
    },
    [](Puzzle &self, const string &rv) {
      self.goalorder() = rv;
    }
  );

  pyPuzzle.def_property(
    "notes",
    [](const Puzzle &self) {
      return self.notes();
    },
    [](Puzzle &self, const string &rv) {
      self.notes() = rv;
    }
  );

  pyPuzzle.def_property(
    "board",
    [](const Puzzle &self) {
      return self.board();
    },
    [](Puzzle &self, const string &rv) {
      self.set_board(rv);
    }
  );

  pyPuzzle.def_property(
    "snapshots",
    [](const Puzzle &self) {
      return self.snapshots();
    },
    [](Puzzle &self, const Snapshots &rv) {
      self.snapshots() = rv;
    }
  );

  pyPuzzle.def_property_readonly("tessellation", &Puzzle::tessellation);
  pyPuzzle.def_property_readonly("has_sokoban_plus", &Puzzle::has_sokoban_plus);

  pyPuzzle.def(
    "cell_orientation",
    [](const Puzzle &self, py_int_t position) {
      return self.cell_orientation(position_or_throw(position));
    },
    py::arg("position")
  );

  pyPuzzle.def(
    "__getitem__",
    [](const Puzzle &self, py_int_t position) -> char {
      return self.at(position_or_throw(position));
    },
    py::arg("position")
  );

  pyPuzzle.def(
    "__setitem__",
    [](Puzzle &self, py_int_t position, char c) {
      self.set_at(position_or_throw(position), c);
    },
    py::arg("position"),
    py::arg("char")
  );

  pyPuzzle.def("__str__", &Puzzle::str);
  pyPuzzle.def("__repr__", &Puzzle::repr);
  pyPuzzle.def(
    "to_board_str",
    &Puzzle::to_board_str,
    py::arg("use_visible_floor") = false,
    py::arg("rle_encode")        = false
  );
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

  pyPuzzle.def(
    "resize",
    [](Puzzle &self, py_int_t new_width, py_int_t new_height) {
      return self.resize(size_or_throw(new_width), size_or_throw(new_height));
    },
    py::arg("new_width"),
    py::arg("new_height")
  );

  pyPuzzle.def(
    "resize_and_center",
    [](Puzzle &self, py_int_t new_width, py_int_t new_height) {
      return self.resize_and_center(
        size_or_throw(new_width), size_or_throw(new_height)
      );
    },
    py::arg("new_width"),
    py::arg("new_height")
  );

  pyPuzzle.def("trim", &Puzzle::trim);
}
