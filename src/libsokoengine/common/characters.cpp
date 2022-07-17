/// @file
#include "characters.hpp"

#include <boost/algorithm/string.hpp>

using std::string;

namespace sokoengine {

namespace io {} // namespace io

namespace implementation {

bool Characters::is_board(const string &line) {
  bool only_digits_and_spaces = all_of(line.cbegin(), line.cend(), [](char c) -> bool {
    return (isdigit(c) != 0) || (isspace(c) != 0);
  });

  return !only_digits_and_spaces
      && all_of(line.begin(), line.end(), [](char c) -> bool {
           return isspace(c) || isdigit(c) || Characters::is_pusher(c)
               || Characters::is_box(c) || Characters::is_goal(c)
               || Characters::is_empty_floor(c) || Characters::is_wall(c)
               || c == Characters::RLE_EOL || c == Characters::RLE_GROUP_START
               || c == Characters::RLE_GROUP_END;
         });
}

bool Characters::is_sokoban_plus(const string &line) {
  bool only_digits_and_spaces = all_of(line.cbegin(), line.cend(), [](char c) -> bool {
    return (isdigit(c) != 0) || (isspace(c) != 0);
  });

  return only_digits_and_spaces && !is_blank(line);
}

bool Characters::is_snapshot(const string &line) {
  bool only_digits_and_spaces = all_of(line.cbegin(), line.cend(), [](char c) -> bool {
    return (isdigit(c) != 0) || (isspace(c) != 0);
  });
  return !only_digits_and_spaces
      && all_of(line.begin(), line.end(), [](char c) -> bool {
           return isdigit(c) || isspace(c) || is_pusher_step(c) || is_marker(c);
         });
}

} // namespace implementation
} // namespace sokoengine
