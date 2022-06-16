#include "sokoenginepyext.hpp"

using namespace std;
using sokoengine::game::piece_id_t;
using sokoengine::game::SokobanPlus;

void export_sokoban_plus(py::module &m) {
  auto pySokobanPlus = py::class_<SokobanPlus>(m, "SokobanPlus");

  pySokobanPlus.def_readonly_static("DEFAULT_PLUS_ID", &SokobanPlus::DEFAULT_PLUS_ID);
  pySokobanPlus.def_readonly_static("LEGACY_DEFAULT_PLUS_ID",
                                    &SokobanPlus::LEGACY_DEFAULT_PLUS_ID);
  pySokobanPlus.def_static("is_valid_plus_id", &SokobanPlus::is_valid_plus_id);

  pySokobanPlus.def(py::init<piece_id_t, const std::string, const std::string>(),
                    py::arg("pieces_count") = 0, py::arg("boxorder") = "",
                    py::arg("goalorder") = "");

  pySokobanPlus.def_property(
    "pieces_count", [](const SokobanPlus &self) { return self.pieces_count(); },
    [](SokobanPlus &self, piece_id_t rv) { self.set_pieces_count(rv); });

  pySokobanPlus.def_property(
    "boxorder", [](const SokobanPlus &self) { return self.boxorder(); },
    [](SokobanPlus &self, const std::string &rv) { self.set_boxorder(rv); });

  pySokobanPlus.def_property(
    "goalorder", [](const SokobanPlus &self) { return self.goalorder(); },
    [](SokobanPlus &self, const std::string &rv) { self.set_goalorder(rv); });

  pySokobanPlus.def_property_readonly("is_valid", &SokobanPlus::is_valid);
  pySokobanPlus.def_property_readonly("is_validated", &SokobanPlus::is_validated);
  pySokobanPlus.def_property_readonly("errors", &SokobanPlus::errors);

  pySokobanPlus.def_property(
    "is_enabled", [](const SokobanPlus &self) { return self.is_enabled(); },
    [](SokobanPlus &self, bool rv) {
      if (rv) {
        self.enable();
      } else {
        self.disable();
      }
    });

  pySokobanPlus.def("box_plus_id", &SokobanPlus::box_plus_id, py::arg("for_box_id"));
  pySokobanPlus.def("goal_plus_id", &SokobanPlus::goal_plus_id, py::arg("for_box_id"));
}
