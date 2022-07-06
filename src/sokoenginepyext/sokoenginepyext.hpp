#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl/filesystem.h>
#include <pybind11/stl_bind.h>

#include <sokoengine.hpp>

namespace py = pybind11;

//
// pybind11 reduces all integer arguments to this type
//
// ie. exporting C++ function:
//
//	void foo(uint8_t bar);
//
// will still generate Python signature
//
//      void foo(int bar);
//
// When foo is called from Python side like this:
//
//     foo(1_000_000_000_000_000_000_000_000)
//
// pybind11 will raise exception:
//
// TypeError: foo(): incompatible function arguments. The following argument types are
// supported:
//     1. (bar: int) -> None
//
typedef int py_int_t;

typedef std::vector<py_int_t> py_int_vect_t;

static inline sokoengine::position_t position_or_throw(py_int_t position) {
  if (position < 0 || position >= std::numeric_limits<sokoengine::position_t>::max())
    throw sokoengine::game::InvalidPositionError(position);
  return static_cast<sokoengine::position_t>(position);
}

static inline sokoengine::game::Positions
positions_or_throw(const py_int_vect_t &positions) {
  sokoengine::game::Positions retv;
  for (auto p : positions) {
    retv.push_back(position_or_throw(p));
  }
  return retv;
}

static inline sokoengine::game::Positions
positions_no_throw(const py_int_vect_t &positions) {
  sokoengine::game::Positions retv;
  for (auto p : positions) {
    if (p >= 0 || p < std::numeric_limits<sokoengine::position_t>::max())
      retv.push_back(static_cast<sokoengine::position_t>(p));
  }
  return retv;
}

static inline sokoengine::game::piece_id_t
piece_or_throw(sokoengine::game::Selectors piece, py_int_t piece_id) {
  if (piece_id < 0 || piece_id >= std::numeric_limits<sokoengine::game::piece_id_t>::max())
    throw sokoengine::game::PieceNotFoundError(piece, piece_id);
  return static_cast<sokoengine::game::piece_id_t>(piece_id);
}

static inline sokoengine::game::piece_id_t no_id_if_invalid(py_int_t piece_id) {
  if (piece_id < 0 || piece_id >= std::numeric_limits<sokoengine::game::piece_id_t>::max())
    return sokoengine::game::Config::NO_ID;
  return static_cast<sokoengine::game::piece_id_t>(piece_id);
}

static inline sokoengine::game::piece_id_t default_if_invalid(py_int_t piece_id) {
  if (piece_id < 0 || piece_id >= std::numeric_limits<sokoengine::game::piece_id_t>::max())
    return sokoengine::game::Config::DEFAULT_ID;
  return static_cast<sokoengine::game::piece_id_t>(piece_id);
}

static inline sokoengine::board_size_t size_or_throw(py_int_t size) {
  if (size < 0 || size >= std::numeric_limits<sokoengine::board_size_t>::max())
    throw std::invalid_argument("Board size " + std::to_string(size) + " is invalid!");
  return static_cast<sokoengine::board_size_t>(size);
}
