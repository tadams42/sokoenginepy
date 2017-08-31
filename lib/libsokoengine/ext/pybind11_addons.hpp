#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace pybind11 {

  // https://sourceforge.net/p/ngsolve/git/ci/master/tree/ngstd/python_ngstd.hpp

  template<typename T>
  bool CheckCast( py::handle obj ) {
    try{
      obj.cast<T>();
      return true;
    }
    catch (py::cast_error &e) {
      return false;
    }
    catch (py::error_already_set &e) {
      return false;
    }
  }


  template <typename T>
  struct extract
  {
    py::handle obj;
    extract( py::handle aobj ) : obj(aobj) {}

    bool check() { return CheckCast<T>(obj); }
    T operator()() { return obj.cast<T>(); }
  };

}
