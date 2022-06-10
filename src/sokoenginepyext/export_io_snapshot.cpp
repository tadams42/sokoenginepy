#include "sokoenginepyext.hpp"

using namespace std;
using namespace sokoengine;
using namespace sokoengine::io;
using sokoengine::Strings;

void export_io_snapshot(py::module &m) {
  auto pySnapshot = py::class_<Snapshot>(m, "Snapshot");

  pySnapshot.def(
    py::init<size_t, string, string, string, string, string, string, Strings>(),
    py::arg("id") = 0, py::arg("moves") = "", py::arg("title") = "",
    py::arg("duration") = "", py::arg("solver") = "", py::arg("created_at") = "",
    py::arg("updated_at") = "", py::arg("notes") = Strings());

  pySnapshot.def_readonly_static("l", &Snapshot::l);
  pySnapshot.def_readonly_static("u", &Snapshot::u);
  pySnapshot.def_readonly_static("r", &Snapshot::r);
  pySnapshot.def_readonly_static("d", &Snapshot::d);
  pySnapshot.def_readonly_static("L", &Snapshot::L);
  pySnapshot.def_readonly_static("U", &Snapshot::U);
  pySnapshot.def_readonly_static("R", &Snapshot::R);
  pySnapshot.def_readonly_static("D", &Snapshot::D);
  pySnapshot.def_readonly_static("w", &Snapshot::w);
  pySnapshot.def_readonly_static("W", &Snapshot::W);
  pySnapshot.def_readonly_static("e", &Snapshot::e);
  pySnapshot.def_readonly_static("E", &Snapshot::E);
  pySnapshot.def_readonly_static("n", &Snapshot::n);
  pySnapshot.def_readonly_static("N", &Snapshot::N);
  pySnapshot.def_readonly_static("s", &Snapshot::s);
  pySnapshot.def_readonly_static("S", &Snapshot::S);

  pySnapshot.def_readonly_static("JUMP_BEGIN", &Snapshot::JUMP_BEGIN);
  pySnapshot.def_readonly_static("JUMP_END", &Snapshot::JUMP_END);
  pySnapshot.def_readonly_static("PUSHER_CHANGE_BEGIN", &Snapshot::PUSHER_CHANGE_BEGIN);
  pySnapshot.def_readonly_static("PUSHER_CHANGE_END", &Snapshot::PUSHER_CHANGE_END);
  pySnapshot.def_readonly_static("CURRENT_POSITION_CH", &Snapshot::CURRENT_POSITION_CH);

  pySnapshot.def_static("is_pusher_step", &Snapshot::is_pusher_step);
  pySnapshot.def_static("is_snapshot", &Snapshot::is_snapshot);
  pySnapshot.def_static("cleaned_moves", &Snapshot::cleaned_moves);

  pySnapshot.def_property(
    "id", [](const Snapshot &self) { return self.id(); },
    [](Snapshot &self, size_t rv) { self.id() = rv; });

  pySnapshot.def_property(
    "moves", [](const Snapshot &self) { return self.moves(); },
    [](Snapshot &self, const string &rv) { self.moves() = rv; });

  pySnapshot.def_property(
    "title", [](const Snapshot &self) { return self.title(); },
    [](Snapshot &self, const string &rv) { self.title() = rv; });

  pySnapshot.def_property(
    "duration", [](const Snapshot &self) { return self.duration(); },
    [](Snapshot &self, const string &rv) { self.duration() = rv; });

  pySnapshot.def_property(
    "solver", [](const Snapshot &self) { return self.solver(); },
    [](Snapshot &self, const string &rv) { self.solver() = rv; });

  pySnapshot.def_property(
    "notes", [](const Snapshot &self) { return self.notes(); },
    [](Snapshot &self, const Strings &rv) { self.notes() = rv; });

  pySnapshot.def_property(
    "created_at", [](const Snapshot &self) { return self.created_at(); },
    [](Snapshot &self, const string &rv) { self.created_at() = rv; });

  pySnapshot.def_property(
    "updated_at", [](const Snapshot &self) { return self.updated_at(); },
    [](Snapshot &self, const string &rv) { self.updated_at() = rv; });

  pySnapshot.def_property_readonly("pushes_count", &Snapshot::pushes_count);
  pySnapshot.def_property_readonly("moves_count", &Snapshot::moves_count);
  pySnapshot.def_property_readonly("is_reverse", &Snapshot::is_reverse);
}
