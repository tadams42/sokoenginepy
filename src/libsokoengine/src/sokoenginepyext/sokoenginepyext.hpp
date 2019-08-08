#include <pybind11/pybind11.h>
#include <sokoengine.hpp>

namespace py = pybind11;

namespace pybind11 {

// https://sourceforge.net/p/ngsolve/git/ci/master/tree/ngstd/python_ngstd.hpp

template <typename T> bool CheckCast(py::handle obj) {
  try {
    obj.cast<T>();
    return true;
  } catch (py::cast_error &e) {
    return false;
  } catch (py::error_already_set &e) {
    return false;
  }
}

template <typename T> struct extract {
  py::handle obj;
  explicit extract(py::handle aobj) : obj(aobj) {}

  bool check() { return CheckCast<T>(obj); }
  T operator()() { return obj.cast<T>(); }
};

template <typename NativeVectorT>
py::list copy_sequence_to_pylist(const NativeVectorT &rv) {
  py::list retv;
  for (auto val : rv)
    retv.append(val);
  return retv;
}

template <typename NativeVectorT>
NativeVectorT copy_pylist_to_sequence(const py::list &rv) {
  NativeVectorT retv;
  if (!rv.is_none()) {
    for (auto val : rv)
      retv.push_back(val.cast<typename NativeVectorT::value_type>());
  }
  return retv;
}

template <typename NativeT>
py::object none_if_equal_to(const NativeT &to_cast, const NativeT &val) {
  if (to_cast == val)
    return py::none();
  return py::cast(to_cast);
}

} // namespace pybind11
