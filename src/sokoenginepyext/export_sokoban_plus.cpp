#include "sokoenginepyext.hpp"

using sokoengine::game::Config;
using sokoengine::game::piece_id_t;
using sokoengine::game::PieceNotFoundError;
using sokoengine::game::Selectors;
using sokoengine::game::SokobanPlus;
using std::make_unique;

void export_sokoban_plus(py::module &m) {
  auto pySokobanPlus = py::class_<SokobanPlus>(m, "SokobanPlus");

  pySokobanPlus.def_readonly_static("DEFAULT_PLUS_ID", &SokobanPlus::DEFAULT_PLUS_ID);
  pySokobanPlus.def_readonly_static(
    "LEGACY_DEFAULT_PLUS_ID", &SokobanPlus::LEGACY_DEFAULT_PLUS_ID
  );

  pySokobanPlus.def_static(
    "is_valid_plus_id",
    [](py_int_t id) {
      if (id < 0 || id >= std::numeric_limits<piece_id_t>::max())
        return false;
      return SokobanPlus::is_valid_plus_id(static_cast<piece_id_t>(id));
    },
    py::arg("id")
  );

  pySokobanPlus.def(
    py::init([](
               py_int_t           pieces_count,
               const std::string &boxorder,
               const std::string &goalorder
             ) {
      if (pieces_count < 0 || pieces_count >= std::numeric_limits<piece_id_t>::max()) {
        throw std::invalid_argument("pieces_count must be >= 0!");
      }
      return make_unique<SokobanPlus>(
        static_cast<piece_id_t>(pieces_count), boxorder, goalorder
      );
    }),
    py::arg("pieces_count") = 0,
    py::arg("boxorder")     = "",
    py::arg("goalorder")    = ""
  );

  pySokobanPlus.def_property(
    "pieces_count",
    [](const SokobanPlus &self) {
      return self.pieces_count();
    },
    [](SokobanPlus &self, py_int_t rv) {
      if (rv < 0 || rv >= std::numeric_limits<piece_id_t>::max()) {
        throw std::invalid_argument("pieces_count must be >= 0!");
      }
      self.set_pieces_count(static_cast<piece_id_t>(rv));
    }
  );

  pySokobanPlus.def_property(
    "boxorder",
    [](const SokobanPlus &self) {
      return self.boxorder();
    },
    [](SokobanPlus &self, const std::string &rv) {
      self.set_boxorder(rv);
    }
  );

  pySokobanPlus.def_property(
    "goalorder",
    [](const SokobanPlus &self) {
      return self.goalorder();
    },
    [](SokobanPlus &self, const std::string &rv) {
      self.set_goalorder(rv);
    }
  );

  pySokobanPlus.def_property_readonly("is_valid", &SokobanPlus::is_valid);
  pySokobanPlus.def_property_readonly("is_validated", &SokobanPlus::is_validated);
  pySokobanPlus.def_property_readonly("errors", &SokobanPlus::errors);

  pySokobanPlus.def_property(
    "is_enabled",
    [](const SokobanPlus &self) {
      return self.is_enabled();
    },
    [](SokobanPlus &self, bool rv) {
      if (rv) {
        self.enable();
      } else {
        self.disable();
      }
    }
  );

  pySokobanPlus.def(
    "box_plus_id",
    [](const SokobanPlus &self, py_int_t piece_id) {
      if (piece_id < 0 || piece_id >= std::numeric_limits<piece_id_t>::max()) {
        if (self.is_enabled()) {
          throw PieceNotFoundError(Selectors::BOXES, piece_id);
        } else {
          return SokobanPlus::DEFAULT_PLUS_ID;
        }
      }
      return self.box_plus_id(static_cast<piece_id_t>(piece_id));
    },
    py::arg("for_box_id")
  );

  pySokobanPlus.def(
    "goal_plus_id",
    [](const SokobanPlus &self, py_int_t piece_id) {
      if (piece_id < 0 || piece_id >= std::numeric_limits<piece_id_t>::max()) {
        if (self.is_enabled()) {
          throw PieceNotFoundError(Selectors::BOXES, piece_id);
        } else {
          return SokobanPlus::DEFAULT_PLUS_ID;
        }
      }
      return self.goal_plus_id(static_cast<piece_id_t>(piece_id));
    },
    py::arg("for_box_id")
  );
}
