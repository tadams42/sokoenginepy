#include <typeinfo>

#include "tessellation_base.hpp"

using namespace std;

namespace sokoengine {

TessellationBase::~TessellationBase() = default;

bool TessellationBase::operator== (const TessellationBase& rv) const {
  return typeid(*this) == typeid(rv);
}
bool TessellationBase::operator!= (const TessellationBase& rv) const {
  return !(*this == rv);
}

} // namespace sokoengine
