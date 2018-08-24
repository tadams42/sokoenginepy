#include <pybind11/pybind11.h>
#include <sokoengine.hpp>

using namespace sokoengine;
namespace py = pybind11;


void export_direction(py::module &);
void export_atomic_move(py::module &);
void export_board_cell(py::module &);
void export_board_graph(py::module &);
void export_tessellations(py::module &);
void export_boards(py::module& m);
void export_board_state(py::module& m);
void export_mover(py::module& m);


PYBIND11_MODULE(sokoenginepyext, m) {
  py::register_exception<sokoengine::BoardConversionError>(
    m, "BoardConversionError", PyExc_RuntimeError
  );

  py::register_exception<sokoengine::IllegalBoardCharacterError>(
    m, "IllegalBoardCharacterError", PyExc_ValueError
  );

  py::register_exception<sokoengine::CellAlreadyOccupiedError>(
    m, "CellAlreadyOccupiedError", PyExc_RuntimeError
  );

  py::register_exception<sokoengine::BoxGoalSwitchError>(
    m, "BoxGoalSwitchError", PyExc_RuntimeError
  );

  // py::register_exception<sokoengine::InvalidPieceIdError>(
  //   m, "InvalidPieceIdError", PyExc_ValueError
  // );

  py::register_exception<sokoengine::SokobanPlusDataError>(
    m, "SokobanPlusDataError", PyExc_ValueError
  );

  py::register_exception<sokoengine::NonPlayableBoardError>(
    m, "NonPlayableBoardError", PyExc_RuntimeError
  );

  py::register_exception<sokoengine::IllegalMoveError>(
    m, "IllegalMoveError", PyExc_RuntimeError
  );

  py::register_exception<sokoengine::KeyError>(
    m, "ExtKeyError", PyExc_KeyError
  );

  py::register_exception<sokoengine::InvalidAtomicMoveError>(
    m, "InvalidAtomicMoveError", PyExc_ValueError
  );

  // py::register_exception<sokoengine::SnapshotConversionError>(
  //   m, "SnapshotConversionError", PyExc_ValueError
  // );

  py::register_exception<sokoengine::UnknownDirectionError>(
    m, "UnknownDirectionError", PyExc_ValueError
  );

  py::register_exception<sokoengine::UnknownTessellationError>(
    m, "UnknownTessellationError", PyExc_ValueError
  );

  export_direction(m);
  export_atomic_move(m);
  export_board_cell(m);
  export_board_graph(m);
  export_tessellations(m);
  export_boards(m);
  export_board_state(m);
  export_mover(m);
}
