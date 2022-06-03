#ifndef UTILITIES_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define UTILITIES_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

namespace sokoengine {
namespace io {

///
/// Test if line is zero length or contains only spaces.
///
bool LIBSOKOENGINE_API is_blank(const std::string &line);


namespace implementation {

///
/// Test if we need line break on given position.
///
bool LIBSOKOENGINE_LOCAL should_insert_line_break_at(uint8_t break_long_lines_at,
                                                     size_t at_pos);

///
/// Test if line contains only digits and spaces
///
bool LIBSOKOENGINE_LOCAL contains_only_digits_and_spaces(const std::string &line);

} // namespace implementation
} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
