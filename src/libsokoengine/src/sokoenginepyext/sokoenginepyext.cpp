#include "sokoenginepyext.hpp"

using namespace sokoengine;
using namespace std;

void export_direction(py::module &);
void export_atomic_move(py::module &);
void export_board_cell(py::module &);
void export_board_graph(py::module &);
void export_tessellations(py::module &);
void export_boards(py::module &m);
void export_board_manager(py::module &m);
void export_mover(py::module &m);

PYBIND11_MODULE(sokoenginepyext, m) {
  py::register_exception<sokoengine::BoardConversionError>(m, "BoardConversionError",
                                                           PyExc_RuntimeError);

  py::register_exception<sokoengine::CellAlreadyOccupiedError>(
    m, "CellAlreadyOccupiedError", PyExc_RuntimeError);

  py::register_exception<sokoengine::BoxGoalSwitchError>(m, "BoxGoalSwitchError",
                                                         PyExc_RuntimeError);

  // py::register_exception<sokoengine::InvalidPieceIdError>(
  //   m, "InvalidPieceIdError", PyExc_ValueError
  // );

  py::register_exception<sokoengine::SokobanPlusDataError>(m, "SokobanPlusDataError",
                                                           PyExc_ValueError);

  py::register_exception<sokoengine::NonPlayableBoardError>(m, "NonPlayableBoardError",
                                                            PyExc_RuntimeError);

  py::register_exception<sokoengine::IllegalMoveError>(m, "IllegalMoveError",
                                                       PyExc_RuntimeError);

  py::register_exception<sokoengine::KeyError>(m, "ExtKeyError", PyExc_KeyError);

  py::register_exception<sokoengine::BoardSizeExceededError>(
    m, "BoardSizeExceededError", PyExc_RuntimeError);

  export_direction(m);
  export_atomic_move(m);
  export_board_cell(m);
  export_board_graph(m);
  export_tessellations(m);
  export_boards(m);
  export_board_manager(m);
  export_mover(m);
}

namespace pybind11 {

position_t receive_position(const object &board_position, bool *converted) {
  py_int_t maybe_number;

  if (converted != nullptr) *converted = true;
  position_t retv = numeric_limits<position_t>::max();
  try {
    maybe_number = board_position.cast<py_int_t>();
    if (maybe_number >= 0 && maybe_number < MAX_POS) {
      retv = (position_t)maybe_number;
    } else {
      if (converted != nullptr) *converted = false;
    }
  } catch (cast_error &e) {
    if (converted != nullptr) *converted = false;
  }

  return retv;
}

position_t receive_position_throw(const object &board_position) {
  bool converted;
  position_t retv = receive_position(board_position, &converted);

  if (!converted)
    // In places where it is checked, Python implementation rises IndexError
    // instead of KeyError when position is not int
    throw index_error("Board position must be integer!");
  else
    return retv;
}

} // namespace pybind11
