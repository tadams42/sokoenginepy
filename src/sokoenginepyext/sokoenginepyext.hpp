#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl/filesystem.h>
#include <pybind11/stl_bind.h>

#include <sokoengine.hpp>

namespace py = pybind11;

PYBIND11_MAKE_OPAQUE(sokoengine::io::Strings);

namespace pybind11 {

// https://sourceforge.net/p/ngsolve/git/ci/master/tree/ngstd/python_ngstd.hpp

template <typename T> bool CheckCast(py::handle obj) {
  try {
    obj.cast<T>();
    return true;
  } catch (py::cast_error &e) { return false; } catch (py::error_already_set &e) {
    return false;
  }
}

template <typename T> struct extract {
  py::handle obj;
  explicit extract(py::handle aobj) : obj(aobj) {}

  bool check() { return CheckCast<T>(obj); }
  T operator()() { return obj.cast<T>(); }
};

typedef long long py_int_t;

sokoengine::position_t receive_position(const py::handle &board_position,
                                              bool *converted = nullptr);
sokoengine::position_t receive_position_throw(const py::handle &board_position);

sokoengine::game::Positions
receive_positions_throw(const py::iterable &pushers_positions);

} // namespace pybind11
