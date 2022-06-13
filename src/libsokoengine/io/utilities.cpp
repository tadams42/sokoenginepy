#include "utilities.hpp"

#include <algorithm>

using namespace std;

namespace sokoengine {
namespace io {

bool is_blank(const std::string &line) {
  return line.empty() || all_of(line.begin(), line.end(),
                                [](char c) -> bool { return isspace(c) != 0; });
}

} // namespace io
} // namespace sokoengine
