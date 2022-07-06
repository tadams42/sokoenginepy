#ifndef RLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define RLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

namespace sokoengine {
namespace io {

///
/// Rle encoding and decoding.
///
class LIBSOKOENGINE_API Rle {
public:
  static constexpr char GROUP_START = '(';
  static constexpr char GROUP_END   = ')';
  static constexpr char EOL         = '|';

  ///
  /// RLE encodes string, ie "aaabbbb" becomes "3a4b".
  ///
  static std::string encode(const std::string &line);

  ///
  /// Decodes RLE encoded string.
  ///
  /// Supports RLE groups, ie strings like "3(a2b)4b"
  ///
  static std::string decode(const std::string &line);

  ///
  /// Returns JSON representation of parser AST. For debugging purposes.
  ///
  static std::string ast_json(const std::string &line);
};

} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
