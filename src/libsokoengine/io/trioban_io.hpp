#ifndef TRIOBAN_IO_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define TRIOBAN_IO_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

namespace sokoengine {
namespace implementation {

class PuzzleResizer;
class PuzzleParser;
class PuzzlePrinter;

class LIBSOKOENGINE_LOCAL TriobanIo {
public:
  static const PuzzleResizer &resizer();
  static const PuzzleParser  &parser();
  static const PuzzlePrinter &printer();
};

} // namespace implementation
} // namespace sokoengine

#endif // HEADER_GUARD
