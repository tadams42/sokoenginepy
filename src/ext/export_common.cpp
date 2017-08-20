#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <libsokoengine.hpp>

using namespace boost::python;
using namespace sokoengine;

void export_common() {
  class_<Positions>("Positions").def(vector_indexing_suite<Positions>());

  class_<Directions>("Directions").def(vector_indexing_suite<Directions>());

  enum_<CellOrientation>("CellOrientation")
    .value("DEFAULT", CellOrientation::DEFAULT)
    .value("TRIANGLE_DOWN", CellOrientation::TRIANGLE_DOWN)
    .value("OCTAGON", CellOrientation::OCTAGON)
    // We don't want constants be available in module scope
    // .export_values()
  ;

  enum_<GraphType>("GraphType")
    .value("DIRECTED", GraphType::DIRECTED)
    .value("DIRECTED_MULTI", GraphType::DIRECTED_MULTI)
    // We don't want constants be available in module scope
    // .export_values()
  ;
}
