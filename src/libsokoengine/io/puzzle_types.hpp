#ifndef PUZZLE_TYPES_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define PUZZLE_TYPES_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

namespace sokoengine {
  namespace io {

enum class LIBSOKOENGINE_API PuzzleTypes : unsigned short {
  SOKOBAN = 0,
  TRIOBAN,
  HEXOBAN,
  OCTOBAN,
};

  } // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
