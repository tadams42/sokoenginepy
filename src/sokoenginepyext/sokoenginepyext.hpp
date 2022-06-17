#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl/filesystem.h>
#include <pybind11/stl_bind.h>

#include <sokoengine.hpp>

namespace py = pybind11;

PYBIND11_MAKE_OPAQUE(sokoengine::io::Strings);

typedef long long py_int_t;
