#include "sokoenginepyext.hpp"

using namespace std;

using sokoengine::game::Config;
using sokoengine::game::BoardSizeExceededError;
using sokoengine::game::BoxGoalSwitchError;
using sokoengine::game::CellAlreadyOccupiedError;
using sokoengine::game::IllegalMoveError;
using sokoengine::game::KeyError;
using sokoengine::game::NonPlayableBoardError;
using sokoengine::position_t;
using sokoengine::game::Positions;
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

  // py::register_exception<sokoengine::InvalidPieceIdError>(
  //   m_game, "InvalidPieceIdError", PyExc_ValueError
  // );

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

namespace pybind11 {

position_t receive_position(const handle &board_position, bool *converted) {
  py_int_t maybe_number;

  if (converted != nullptr) *converted = true;
  position_t retv = numeric_limits<position_t>::max();
  try {
    maybe_number = board_position.cast<py_int_t>();
    if (maybe_number >= 0 && maybe_number < Config::MAX_POS) {
      retv = (position_t)maybe_number;
    } else {
      if (converted != nullptr) *converted = false;
    }
  } catch (cast_error &e) {
    if (converted != nullptr) *converted = false;
  }

  return retv;
}

position_t receive_position_throw(const handle &board_position) {
  bool converted;
  position_t retv = receive_position(board_position, &converted);

  if (!converted)
    // In places where it is checked, Python implementation rises IndexError
    // instead of KeyError when position is not int
    throw index_error("Board position must be integer!");
  else
    return retv;
}

Positions receive_positions_throw(const py::iterable &positions) {
  Positions retv;
  if (!positions.is_none()) {
    for (auto val : positions) {
      retv.push_back(receive_position_throw(val));
    }
  }
  return retv;
}

} // namespace pybind11
