#include "sokoenginepyext.hpp"

using namespace std;
using sokoengine::io::Collection;
using sokoengine::io::Puzzles;
using sokoengine::io::Strings;
using sokoengine::game::Tessellation;

void export_io_collection(py::module &m) {
  auto pyCollection = py::class_<Collection>(m, "Collection");

  pyCollection.def(py::init<string, string, string, string, Strings>(),
                   py::arg("title") = "", py::arg("author") = "",
                   py::arg("created_at") = "", py::arg("updated_at") = "",
                   py::arg("notes") = Strings());

  pyCollection.def_property(
    "title", [](const Collection &self) { return self.title(); },
    [](Collection &self, const string &rv) { self.title() = rv; });

  pyCollection.def_property(
    "author", [](const Collection &self) { return self.author(); },
    [](Collection &self, const string &rv) { self.author() = rv; });

  pyCollection.def_property(
    "notes", [](const Collection &self) { return self.notes(); },
    [](Collection &self, const Strings &rv) { self.notes() = rv; });

  pyCollection.def_property(
    "created_at", [](const Collection &self) { return self.created_at(); },
    [](Collection &self, const string &rv) { self.created_at() = rv; });

  pyCollection.def_property(
    "updated_at", [](const Collection &self) { return self.updated_at(); },
    [](Collection &self, const string &rv) { self.updated_at() = rv; });

  pyCollection.def_property(
    "puzzles", [](const Collection &self) { return self.puzzles(); },
    [](Collection &self, const Puzzles &rv) { self.puzzles() = rv; });

  pyCollection
    .def("load", py::overload_cast<const filesystem::path &>(&Collection::load))
    .def("load",
         py::overload_cast<const filesystem::path &, Tessellation>(&Collection::load))
    .def("load", py::overload_cast<const string &>(&Collection::load))
    .def("load", py::overload_cast<const string &, Tessellation>(&Collection::load));

  pyCollection
    .def("save",
         py::overload_cast<const filesystem::path &>(&Collection::save, py::const_))
    .def("save", py::overload_cast<const string &>(&Collection::save, py::const_));
}
