#include <boost/python.hpp>
#include <sokoengine.hpp>

using namespace boost::python;
using namespace sokoengine;

void export_direction();
void export_board_cell();
void export_atomic_move();
void export_board_graph();
void export_tessellations();
void export_boards();
void export_board_state();
void export_mover();

void translator(const KeyError& exception) {
  PyErr_SetString(PyExc_KeyError, exception.what());
}

BOOST_PYTHON_MODULE(libsokoengine)
{
  register_exception_translator<KeyError>(translator);

  export_direction();
  export_board_cell();
  export_atomic_move();
  export_board_graph();
  export_tessellations();
  export_boards();
  export_board_state();
  export_mover();
}
