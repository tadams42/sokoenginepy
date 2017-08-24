#include "tessellation_base.hpp"
#include "variant_board.hpp"

#include <typeinfo>

using namespace std;

namespace sokoengine {

using namespace implementation;

UnknownDirectionError::UnknownDirectionError(const string& mess):
  invalid_argument(mess)
{}

UnknownDirectionError::~UnknownDirectionError() = default;

TessellationBase::~TessellationBase() = default;

bool TessellationBase::operator== (const TessellationBase& rv) const {
  return typeid(*this) == typeid(rv);
}
bool TessellationBase::operator!= (const TessellationBase& rv) const {
  return !(*this == rv);
}

const VariantBoardResizer& TessellationBase::resizer() const {
  static const VariantBoardResizer retv = VariantBoardResizer();
  return retv;
}

const VariantBoardPrinter& TessellationBase::printer() const {
  static const VariantBoardPrinter retv = VariantBoardPrinter();
  return retv;
}

const VariantBoardParser& TessellationBase::parser() const {
  static const VariantBoardParser retv = VariantBoardParser();
  return retv;
}

} // namespace sokoengine
