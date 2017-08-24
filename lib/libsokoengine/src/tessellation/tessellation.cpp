#include "tessellation.hpp"
#include "tessellation_base.hpp"
#include "text_utils.hpp"

#include "sokoban_tessellation.hpp"
#include "trioban_tessellation.hpp"
#include "octoban_tessellation.hpp"
#include "hexoban_tessellation.hpp"

#include <boost/algorithm/string.hpp>

using namespace std;

namespace sokoengine {

UnknownTessellationError::UnknownTessellationError(const string& mess):
  invalid_argument(mess)
{}

UnknownTessellationError::~UnknownTessellationError() = default;

Tessellation::~Tessellation() = default;

const TessellationBase& Tessellation::instance_from(const string& name) {
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

const TessellationBase& Tessellation::instance_from(
  const TessellationBase& tessellation
) {
  return instance_from(tessellation.str());
}

} // namespace sokoengine
