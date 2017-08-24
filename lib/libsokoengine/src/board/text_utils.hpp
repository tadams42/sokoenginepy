#ifndef TEXT_UTILS_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define TEXT_UTILS_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

#include <string>
#include <deque>

namespace sokoengine {

typedef std::deque<std::string> StringList;

///
/// Helper utilities for string manipulation and Sokoban data
/// parsing. Mostly related to SOK file format, but
/// probably useful for parsing any Sokoban file format.
///
/// @see SOKFileFormat
///
class LIBSOKOENGINE_API TextUtils {
public:
  ///
  /// Separators used in RLE encoded board and snapshot texts
  ///
  /// @see SOKFileFormat
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
};

} // namespace sokoengine

#endif // HEADER_GUARD
