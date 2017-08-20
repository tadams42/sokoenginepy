#include <boost/python.hpp>

using namespace boost::python;

void export_common();
void export_direction();
void export_board_cell();
void export_atomic_move();
void export_board_graph();
void export_tessellations();

BOOST_PYTHON_MODULE(libsokoengine)
{
  export_common();
  export_direction();
  export_board_cell();
  export_atomic_move();
  export_board_graph();
  export_tessellations();
}
