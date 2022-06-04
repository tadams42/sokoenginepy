#ifndef RLE_CONFIG_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define RLE_CONFIG_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "rle_error_handler.hpp"

#include <boost/spirit/home/x3.hpp>

namespace sokoengine {
namespace io {
namespace sok_rle {

namespace x3 = boost::spirit::x3;

namespace parser {

// Our Iterator Type
typedef std::string::const_iterator iterator_type;

// Our Error Handler
typedef x3::error_handler<iterator_type> error_handler_type;

// Phrase Parse Context without skipper. This one should be used in combination with
// `x3::parse`, ie
//
//   x3::parse(iter, end, parser, ast)
typedef x3::context<x3::error_handler_tag, std::reference_wrapper<error_handler_type>>
  context_type;

} // namespace parser
} // namespace sok_rle
} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
