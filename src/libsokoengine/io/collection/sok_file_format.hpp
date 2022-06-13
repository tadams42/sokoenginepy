#ifndef SOK_FILE_FORMAT_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define SOK_FILE_FORMAT_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

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
            const std::string &puzzle_type_hint = "sokoban");
  bool write(const Puzzle &puzzle, std::ostream &dest);
  bool write(const Collection &collection, std::ostream &dest);
};

} // namespace implementation
} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
