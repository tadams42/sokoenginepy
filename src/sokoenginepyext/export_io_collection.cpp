#include "sokoenginepyext.hpp"

using namespace std;
using namespace sokoengine::io;

void export_io_collection(py::module &m) {
  auto pyCollection = py::class_<Collection>(m, "Collection");

  pyCollection.def(py::init<string, string, string, string, string>(),
                   py::arg("title") = "", py::arg("author") = "", py::arg("notes") = "",
                   py::arg("created_at") = "", py::arg("updated_at") = "");

  pyCollection.def("clear", &Collection::clear);

  pyCollection.def_property(
    "title", [](const Collection &self) { return self.title(); },
    [](Collection &self, const string &rv) { self.title() = rv; });

  pyCollection.def_property(
    "author", [](const Collection &self) { return self.author(); },
    [](Collection &self, const string &rv) { self.author() = rv; });

  pyCollection.def_property(
    "notes", [](const Collection &self) { return self.notes(); },
    [](Collection &self, const string &rv) { self.notes() = rv; });

  pyCollection.def_property(
    "created_at", [](const Collection &self) { return self.created_at(); },
    [](Collection &self, const string &rv) { self.created_at() = rv; });

  pyCollection.def_property(
    "updated_at", [](const Collection &self) { return self.updated_at(); },
    [](Collection &self, const string &rv) { self.updated_at() = rv; });

  pyCollection.def_property(
    "puzzles", [](const Collection &self) { return self.puzzles(); },
    [](Collection &self, const Puzzles &rv) { self.puzzles() = rv; });

  // pyCollection.def(
  //   "load",
  //   [](Collection &self, const string &path,
  //      const PuzzleTypes *puzzle_type_hint = nullptr) {
  //     if (puzzle_type_hint == nullptr) {
  //       return self.load(path);
  //     } else {
  //       return self.load(path, *puzzle_type_hint);
  //     }
  //   },
  //   py::arg("path"), py::arg("puzzle_type_hint") = static_cast<PuzzleTypes
  //   *>(nullptr));
  // pyCollection.def("save", &Collection::save);

  pyCollection
    .def("load", py::overload_cast<const filesystem::path &>(&Collection::load))
    .def("load", py::overload_cast<const filesystem::path &, const PuzzleTypes &>(
                   &Collection::load))
    .def("load", py::overload_cast<const string &>(&Collection::load))
    .def("load",
         py::overload_cast<const string &, const PuzzleTypes &>(&Collection::load));

  pyCollection
    .def("save",
         py::overload_cast<const filesystem::path &>(&Collection::save, py::const_))
    .def("save", py::overload_cast<const string &>(&Collection::save, py::const_));

  pyCollection.def("reformat", &Collection::reformat,
                   py::arg("use_visible_floor") = false,
                   py::arg("break_long_lines_at") = 80, py::arg("rle_encode") = false);
}
