#ifndef TESSELLATION_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define TESSELLATION_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

#include <stdexcept>

namespace sokoengine {

class LIBSOKOENGINE_API TessellationBase;

class LIBSOKOENGINE_API UnknownTessellationError: public std::invalid_argument {
public:
  UnknownTessellationError(const std::string& mess);
  virtual ~UnknownTessellationError();
};

class LIBSOKOENGINE_API Tessellation {
public:
  virtual ~Tessellation() = 0;

  static const TessellationBase& instance_from(const std::string& name);
  static const TessellationBase& instance_from(
    const TessellationBase& tessellation
  );
};

} // namespace sokoengine

#endif // HEADER_GUARD
