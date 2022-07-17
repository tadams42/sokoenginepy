#ifndef SOK_FILE_FORMAT_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define SOK_FILE_FORMAT_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "tessellation.hpp"

namespace sokoengine {
namespace io {
class Puzzle;
class Collection;
} // namespace io

namespace implementation {

class LIBSOKOENGINE_LOCAL SOKFileFormat {
public:
  virtual ~SOKFileFormat();

  void read(
    std::istream   &src,
    io::Collection &dest,
    Tessellation    tessellation_hint = Tessellation::SOKOBAN
  );
  bool write(const io::Collection &collection, std::ostream &dest);
};

} // namespace implementation
} // namespace sokoengine

#endif // HEADER_GUARD
