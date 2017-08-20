#ifndef EXCEPTIONS_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define EXCEPTIONS_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include <string>
#include <stdexcept>

#include "sokoengine_config.hpp"

namespace sokoengine {


class LIBSOKOENGINE_API UnknownDirectionError: public std::invalid_argument {
public:
  UnknownDirectionError(const std::string& mess);
  virtual ~UnknownDirectionError();
};

} // namespace sokoengine

#endif // HEADER_GUARD
