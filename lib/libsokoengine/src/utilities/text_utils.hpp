#ifndef TEXT_UTILS_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define TEXT_UTILS_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

#include <string>
#include <deque>

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
  ///
  /// Separators used in RLE encoded board and snapshot texts
  ///
  ///
  enum RleCharacters {
    GROUP_LEFT_DELIM  = '(',
    GROUP_RIGHT_DELIM = ')',
    RLE_ROW_SEPARATOR = '|'
  };

  static bool is_blank(const std::string& tlne);
  static bool contains_only_digits_and_spaces (const std::string& line);
  static bool rle_encode (std::string& str);
  static bool rle_decode (std::string& str);

  static StringList normalize_width(
    const StringList& string_list, char fill_chr=' '
  );
  static size_t calculate_width(const StringList& string_list);

  // static std::string& strip_and_downcase(std::string& line);
  // static std::string strip_and_downcase(const std::string& line);
  // static void assign_to_blank(std::string& dest, const std::string& src);
};

} // namespace sokoengine

#endif // HEADER_GUARD
