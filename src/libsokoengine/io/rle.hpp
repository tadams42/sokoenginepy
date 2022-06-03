#ifndef RLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define RLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

namespace sokoengine {
namespace io {
namespace implementation {

///
/// Rle encoding and decoding.
///
class LIBSOKOENGINE_LOCAL Rle {
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

  static std::string encode(const std::string &line);
  static std::string decode(const std::string &line);
};

} // namespace implementation

using implementation::Rle;

} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
