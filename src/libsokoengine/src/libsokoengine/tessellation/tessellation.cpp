#include "tessellation.hpp"
#include "text_utils.hpp"
#include "variant_board.hpp"

#include "hexoban_tessellation.hpp"
#include "octoban_tessellation.hpp"
#include "sokoban_tessellation.hpp"
#include "trioban_tessellation.hpp"

#include <typeinfo>

#include <boost/algorithm/string.hpp>

using namespace std;

namespace sokoengine {

using namespace implementation;

UnknownDirectionError::UnknownDirectionError(const string &mess)
    : invalid_argument(mess) {}

UnknownDirectionError::~UnknownDirectionError() = default;

UnknownTessellationError::UnknownTessellationError(const string &mess)
    : invalid_argument(mess) {}

UnknownTessellationError::~UnknownTessellationError() = default;

const SokobanTessellation &Tessellation::SOKOBAN = SokobanTessellation();
const HexobanTessellation &Tessellation::HEXOBAN = HexobanTessellation();
const TriobanTessellation &Tessellation::TRIOBAN = TriobanTessellation();
const OctobanTessellation &Tessellation::OCTOBAN = OctobanTessellation();

const Tessellation &Tessellation::instance_from(const string &name) {
  string check_name = boost::trim_copy(name);
  boost::to_lower(check_name);

  if (check_name == "sokoban" or TextUtils::is_blank(name))
    return SOKOBAN;
  if (check_name == "trioban")
    return TRIOBAN;
  if (check_name == "hexoban")
    return HEXOBAN;
  if (check_name == "octoban")
    return OCTOBAN;

  throw UnknownTessellationError(name);
}

Tessellation::~Tessellation() = default;

bool Tessellation::operator==(const Tessellation &rv) const {
  return typeid(*this) == typeid(rv);
}
bool Tessellation::operator!=(const Tessellation &rv) const { return !(*this == rv); }

const VariantBoardResizer &Tessellation::resizer() const {
  static const VariantBoardResizer retv = VariantBoardResizer();
  return retv;
}

const VariantBoardPrinter &Tessellation::printer() const {
  static const VariantBoardPrinter retv = VariantBoardPrinter();
  return retv;
}

const VariantBoardParser &Tessellation::parser() const {
  static const VariantBoardParser retv = VariantBoardParser();
  return retv;
}

GraphType Tessellation::graph_type() const { return GraphType::DIRECTED; }

CellOrientation Tessellation::cell_orientation(position_t position, board_size_t board_width,
                                               board_size_t board_height) const {
  return CellOrientation::DEFAULT;
}

} // namespace sokoengine
