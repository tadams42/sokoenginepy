#ifndef SOK_FILE_FORMAT_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define SOK_FILE_FORMAT_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "puzzle_types.hpp"

#include <iostream>

namespace sokoengine {
namespace io {

class Puzzle;
class Collection;

namespace implementation {

class LIBSOKOENGINE_LOCAL SOKFileFormat {
public:
  virtual ~SOKFileFormat();

  void read(std::istream &src, Collection &dest,
            const PuzzleTypes &puzzle_type_hint = PuzzleTypes::SOKOBAN);
  bool write(const Puzzle &puzzle, std::ostream &dest);
  bool write(const Collection &collection, std::ostream &dest);
};

} // namespace implementation
} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
