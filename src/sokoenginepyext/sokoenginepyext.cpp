#include "sokoenginepyext.hpp"

using sokoengine::BoxGoalSwitchError;
using sokoengine::CellAlreadyOccupiedError;
using sokoengine::IllegalMoveError;
using sokoengine::InvalidPositionError;
using sokoengine::NonPlayableBoardError;
using sokoengine::PieceNotFoundError;
using sokoengine::SokobanPlusDataError;

void export_pusher_step(py::module &);
void export_board_cell(py::module &);
void export_board_graph(py::module &);
void export_boards(py::module &m);
void export_sokoban_plus(py::module &m);
void export_board_manager(py::module &m);
void export_mover(py::module &m);
void export_io_snapshot(py::module &m);
void export_io_puzzle(py::module &m);
void export_io_collection(py::module &m);
void export_io_rle(py::module &m);

PYBIND11_MODULE(sokoenginepyext, m) {
  py::register_exception<CellAlreadyOccupiedError>(
    m, "CellAlreadyOccupiedError", PyExc_ValueError
  );

  py::register_exception<BoxGoalSwitchError>(m, "BoxGoalSwitchError", PyExc_ValueError);

  py::register_exception<SokobanPlusDataError>(
    m, "SokobanPlusDataError", PyExc_ValueError
  );

  py::register_exception<NonPlayableBoardError>(
    m, "NonPlayableBoardError", PyExc_ValueError
  );

  py::register_exception<IllegalMoveError>(m, "IllegalMoveError", PyExc_ValueError);

  py::register_exception<PieceNotFoundError>(m, "PieceNotFoundError", PyExc_KeyError);

  py::register_exception<InvalidPositionError>(
    m, "InvalidPositionError", PyExc_IndexError
  );

  export_pusher_step(m);
  export_board_cell(m);
  export_board_graph(m);
  export_sokoban_plus(m);
  export_board_manager(m);
  export_mover(m);
  export_io_snapshot(m);
  export_io_puzzle(m);
  export_io_collection(m);
  export_io_rle(m);
}
