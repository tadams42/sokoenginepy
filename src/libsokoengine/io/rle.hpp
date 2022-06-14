#ifndef RLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define RLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "config.hpp"

namespace sokoengine {
namespace io {

///
/// Rle encoding and decoding.
///
class LIBSOKOENGINE_API Rle {
public:
  ///
  /// Counted group delimiter. ie. "ab3(cd)e4f" will be decoded as "abcdcdcdefff".
  ///
  static constexpr char GROUP_START = '(';

  ///
  /// Counted group delimiter. ie. "ab3(cd)e4f" will be decoded as "abcdcdcdefff".
  ///
  static constexpr char GROUP_END = ')';

  ///
  /// Line separator in encoded strings
  ///
  static constexpr char EOL = '|';

  ///
  /// RLE encodes string.
  ///
  ///   - "aaabbbb"                       -> "3a4b"
  ///   - "aabbbbccddeeeeffddeeeeff"      -> "2a4b2c2d4e2f2d4e2f"
  ///   - "aabbbbccddee\neeffddeeeeff"    -> "2a4b2c2d2e|2e2f2d4e2f"
  ///   - "aabbbbccddee     eeffddeeeeff" -> "2a4b2c2d2e5 2e2f2d4e2f
  ///
  static std::string encode(const std::string &line);

  ///
  /// Decodes RLE encoded string.
  ///
  /// Supports RLE groups, ie strings like:
  ///
  ///   - "3(a2b)4b"               -> "abbabbabbbbbb"
  ///
  /// Returns a list of RLE decoded lines:
  ///
  ///   - "2a4b2c2d2e|2e2f2d4e2f"  -> "aabbbbccddee\neeffddeeeeff"
  ///
  static std::string decode(const std::string &line);

  ///
  /// Returns JSON representation of parser AST. Intended to be used for debugging
  /// purposes.
  ///
  static std::string ast_json(const std::string &line);
};

} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
