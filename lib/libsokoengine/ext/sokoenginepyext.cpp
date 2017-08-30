#include <pybind11/pybind11.h>
#include <sokoengine.hpp>

using namespace sokoengine;
namespace py = pybind11;

// void init_ex1(py::module &);
// void init_ex2(py::module &);

int add(int i, int j) {
    return i + j;
}

PYBIND11_MODULE(sokoenginepyext, m) {
    // init_ex1(m);
    // init_ex2(m);

    m.def("add", &add, "A function which adds two numbers");
}
