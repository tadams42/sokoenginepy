#include <boost/python.hpp>

using namespace boost::python;

void export_common();
void export_direction();
void export_board_cell();

BOOST_PYTHON_MODULE(libsokoengine)
{
  export_common();
  export_direction();
  export_board_cell();
}
