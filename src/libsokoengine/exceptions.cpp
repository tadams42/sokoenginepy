#include "exceptions.hpp"

using namespace std;

namespace sokoengine {

UnknownDirectionError::UnknownDirectionError(const string& mess):
  invalid_argument(mess)
{}

UnknownDirectionError::~UnknownDirectionError() = default;

} // namespace sokoengine
