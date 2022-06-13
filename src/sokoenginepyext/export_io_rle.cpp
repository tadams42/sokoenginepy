#include "sokoenginepyext.hpp"

using namespace std;
using namespace sokoengine::io;

void export_io_rle(py::module &m) {
  auto pyRle = py::class_<Rle>(m, "Rle");

  pyRle.def_readonly_static("GROUP_START", &Rle::GROUP_START);
  pyRle.def_readonly_static("GROUP_END", &Rle::GROUP_END);
  pyRle.def_readonly_static("EOL", &Rle::EOL);

  pyRle.def_static("encode", &Rle::encode);
  pyRle.def_static("decode", &Rle::decode);
  pyRle.def_static("ast_json", &Rle::ast_json);
}
