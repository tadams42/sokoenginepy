#include "utilities.hpp"

#include <algorithm>

using namespace std;

namespace sokoengine {
namespace io {

bool is_blank(const std::string &line) {
  return line.empty() || all_of(line.begin(), line.end(),
                                [](char c) -> bool { return isspace(c) != 0; });
}

namespace implementation {

bool contains_only_digits_and_spaces(const std::string &line) {
  return all_of(line.begin(), line.end(),
                [](char c) -> bool { return (isdigit(c) != 0) || (isspace(c) != 0); });
}

bool should_insert_line_break_at(uint8_t break_long_lines_at, size_t at_pos) {
  bool retv = false;
  if (break_long_lines_at > 0 && at_pos > 0) {
    retv = (at_pos % break_long_lines_at == 0);
  }
  return retv;
}

} // namespace implementation

} // namespace io
} // namespace sokoengine
