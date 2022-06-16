#ifndef SOK_FILE_FORMAT_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define SOK_FILE_FORMAT_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "config.hpp"

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
            game::Tessellation tessellation_hint = game::Tessellation::SOKOBAN);
  bool write(const Collection &collection, std::ostream &dest);
};

} // namespace implementation
} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
