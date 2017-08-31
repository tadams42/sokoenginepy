#include "tessellation.hpp"
#include "variant_board.hpp"
#include "text_utils.hpp"

#include "sokoban_tessellation.hpp"
#include "trioban_tessellation.hpp"
#include "octoban_tessellation.hpp"
#include "hexoban_tessellation.hpp"

#include <typeinfo>

#include <boost/algorithm/string.hpp>

using namespace std;

namespace sokoengine {

using namespace implementation;

UnknownDirectionError::UnknownDirectionError(const string& mess):
  invalid_argument(mess)
{}

UnknownDirectionError::~UnknownDirectionError() = default;

UnknownTessellationError::UnknownTessellationError(const string& mess):
  invalid_argument(mess)
{}

UnknownTessellationError::~UnknownTessellationError() = default;

const Tessellation& Tessellation::instance_from(const string& name) {
  static const SokobanTessellation sokoban_tessellation = SokobanTessellation();
  static const TriobanTessellation trioban_tessellation = TriobanTessellation();
  static const OctobanTessellation octoban_tessellation = OctobanTessellation();
  static const HexobanTessellation hexoban_tessellation = HexobanTessellation();

  string check_name = boost::trim_copy(name);
  boost::to_lower(check_name);

  if (check_name == "sokoban" or TextUtils::is_blank(name))
    return sokoban_tessellation;
  if (check_name == "trioban") return trioban_tessellation;
  if (check_name == "hexoban") return hexoban_tessellation;
  if (check_name == "octoban") return octoban_tessellation;

  throw UnknownTessellationError(name);
}

const Tessellation& Tessellation::instance_from(
  const Tessellation& tessellation
) {
  return instance_from(tessellation.str());
}

Tessellation::~Tessellation() = default;

bool Tessellation::operator== (const Tessellation& rv) const {
  return typeid(*this) == typeid(rv);
}
bool Tessellation::operator!= (const Tessellation& rv) const {
  return !(*this == rv);
}

const VariantBoardResizer& Tessellation::resizer() const {
  static const VariantBoardResizer retv = VariantBoardResizer();
  return retv;
}

const VariantBoardPrinter& Tessellation::printer() const {
  static const VariantBoardPrinter retv = VariantBoardPrinter();
  return retv;
}

const VariantBoardParser& Tessellation::parser() const {
  static const VariantBoardParser retv = VariantBoardParser();
  return retv;
}

GraphType Tessellation::graph_type() const { return GraphType::DIRECTED; }

CellOrientation Tessellation::cell_orientation(
  position_t position, size_t board_width, size_t board_height
) const {
  return CellOrientation::DEFAULT;
}

} // namespace sokoengine
