#include "sokoenginepyext.hpp"

using namespace std;
using sokoengine::game::PusherSteps;
using sokoengine::io::HexobanSnapshot;
using sokoengine::io::OctobanSnapshot;
using sokoengine::io::Snapshot;
using sokoengine::io::SokobanSnapshot;
using sokoengine::io::Strings;
using sokoengine::io::TriobanSnapshot;

void export_io_snapshot(py::module &m) {
  auto pySnapshot = py::class_<Snapshot>(m, "Snapshot", py::is_final());

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

  pySnapshot.def_static("is_move_step", &Snapshot::is_pusher_step);
  pySnapshot.def_static("is_push_step", &Snapshot::is_pusher_step);
  pySnapshot.def_static("is_pusher_step", &Snapshot::is_pusher_step);
  pySnapshot.def_static("is_marker", &Snapshot::is_pusher_step);
  pySnapshot.def_static("is_snapshot", &Snapshot::is_snapshot);
  pySnapshot.def_static("ast_json", &Snapshot::ast_json);

  pySnapshot.def("to_str", &Snapshot::to_str, py::arg("rle_encode") = false);
  pySnapshot.def("__str__", &Snapshot::str);
  pySnapshot.def("__repr__", &Snapshot::repr);

  pySnapshot.def_property_readonly("tessellation", &Snapshot::tessellation);

  pySnapshot.def_property(
    "moves_data", [](const Snapshot &self) { return self.moves_data(); },
    [](Snapshot &self, const string &rv) { self.set_moves_data(rv); });

  pySnapshot.def_property(
    "pusher_steps", [](const Snapshot &self) { return self.pusher_steps(); },
    [](Snapshot &self, const PusherSteps &rv) { self.set_pusher_steps(rv); });

  pySnapshot.def_property(
    "title", [](const Snapshot &self) { return self.title(); },
    [](Snapshot &self, const string &rv) { self.title() = rv; });

  pySnapshot.def_property(
    "solver", [](const Snapshot &self) { return self.solver(); },
    [](Snapshot &self, const string &rv) { self.solver() = rv; });

  pySnapshot.def_property(
    "notes", [](const Snapshot &self) { return self.notes(); },
    [](Snapshot &self, const Strings &rv) { self.notes() = rv; });

  pySnapshot.def_property_readonly("pushes_count", &Snapshot::pushes_count);
  pySnapshot.def_property_readonly("moves_count", &Snapshot::moves_count);
  pySnapshot.def_property_readonly("jumps_count", &Snapshot::jumps_count);
  pySnapshot.def_property_readonly("is_reverse", &Snapshot::is_reverse);

  auto pySokobanSnapshot =
    py::class_<SokobanSnapshot, Snapshot>(m, "SokobanSnapshot", py::is_final())
      .def(py::init<std::string>(), py::arg("moves_data") = "");

  auto pyHexobanSnapshot =
    py::class_<HexobanSnapshot, Snapshot>(m, "HexobanSnapshot", py::is_final())
      .def(py::init<std::string>(), py::arg("moves_data") = "");

  auto pyTriobanSnapshot =
    py::class_<TriobanSnapshot, Snapshot>(m, "TriobanSnapshot", py::is_final())
      .def(py::init<std::string>(), py::arg("moves_data") = "");

  auto pyOctobanSnapshot =
    py::class_<OctobanSnapshot, Snapshot>(m, "OctobanSnapshot", py::is_final())
      .def(py::init<std::string>(), py::arg("moves_data") = "");
}
