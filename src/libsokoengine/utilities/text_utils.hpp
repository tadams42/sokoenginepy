#ifndef TEXT_UTILS_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define TEXT_UTILS_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

#include <deque>
#include <string>

namespace sokoengine {

///
/// Collection of strings.
///
typedef std::deque<std::string> StringList;

///
/// Helper utilities for string manipulation.
///
class LIBSOKOENGINE_API TextUtils {
public:
  //
  // Separators used in RLE encoded board and snapshot texts
  //

  static constexpr char GROUP_START = '(';
  static constexpr char GROUP_END = ')';
  static constexpr char ROW_SEPARATOR = '|';

  static bool is_blank(const std::string &tlne);
  static bool contains_only_digits_and_spaces(const std::string &line);
  static bool rle_encode(std::string &str);
  static bool rle_decode(std::string &str);

  static StringList normalize_width(const StringList &string_list, char fill_chr = ' ');
  static size_t calculate_width(const StringList &string_list);
};

} // namespace sokoengine

#endif // HEADER_GUARD
