#include "sokoenginepyext.hpp"

using namespace std;

using sokoengine::game::BoardSizeExceededError;
using sokoengine::game::BoxGoalSwitchError;
using sokoengine::game::CellAlreadyOccupiedError;
using sokoengine::game::IllegalMoveError;
using sokoengine::game::KeyError;
using sokoengine::game::NonPlayableBoardError;
using sokoengine::game::SokobanPlusDataError;
using sokoengine::io::Strings;

void export_pusher_step(py::module &);
void export_board_cell(py::module &);
void export_board_graph(py::module &);
void export_tessellations(py::module &);
void export_boards(py::module &m);
void export_sokoban_plus(py::module &m);
void export_board_manager(py::module &m);
void export_mover(py::module &m);
void export_io_snapshot(py::module &m);
void export_io_puzzle(py::module &m);
void export_io_collection(py::module &m);
void export_io_rle(py::module &m);

PYBIND11_MODULE(sokoenginepyext, m) {
  py::module_ m_game = m.def_submodule("game");
  py::module_ m_io = m.def_submodule("io");

  py::bind_vector<Strings>(m_io, "StringsList");

  py::register_exception<CellAlreadyOccupiedError>(m_game, "CellAlreadyOccupiedError",
                                                   PyExc_RuntimeError);

  py::register_exception<BoxGoalSwitchError>(m_game, "BoxGoalSwitchError",
                                             PyExc_RuntimeError);

  py::register_exception<SokobanPlusDataError>(m_game, "SokobanPlusDataError",
                                               PyExc_ValueError);

  py::register_exception<NonPlayableBoardError>(m_game, "NonPlayableBoardError",
                                                PyExc_RuntimeError);

  py::register_exception<IllegalMoveError>(m_game, "IllegalMoveError",
                                           PyExc_RuntimeError);

  py::register_exception<KeyError>(m_game, "ExtKeyError", PyExc_KeyError);

  py::register_exception<BoardSizeExceededError>(m_game, "BoardSizeExceededError",
                                                 PyExc_ValueError);
  export_pusher_step(m_game);
  export_board_cell(m_game);
  export_board_graph(m_game);
  export_tessellations(m_game);
  export_sokoban_plus(m_game);
  export_board_manager(m_game);
  export_mover(m_game);
  export_io_snapshot(m_io);
  export_io_puzzle(m_io);
  export_io_collection(m_io);
  export_io_rle(m_io);
}
