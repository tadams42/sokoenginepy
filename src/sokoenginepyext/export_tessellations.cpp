#include "sokoenginepyext.hpp"

#include <map>

using sokoengine::game::Tessellation;

void export_tessellations(py::module &m) {
  py::enum_<Tessellation>(m, "Tessellation")
    .value("SOKOBAN", Tessellation::SOKOBAN)
    .value("HEXOBAN", Tessellation::HEXOBAN)
    .value("TRIOBAN", Tessellation::TRIOBAN)
    .value("OCTOBAN", Tessellation::OCTOBAN);
}
