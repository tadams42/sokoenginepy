#ifndef CONFIG_BDC825C2_4FAB_4173_9B94_185BD7430359
#define CONFIG_BDC825C2_4FAB_4173_9B94_185BD7430359

#include "error_handler.hpp"

#include <boost/spirit/home/x3.hpp>

namespace sokoengine {
namespace io {
namespace snapshot_parsing {

namespace x3 = boost::spirit::x3;

namespace parser {

// Our Iterator Type
typedef std::string::const_iterator iterator_type;

// Our Error Handler
typedef x3::error_handler<iterator_type> error_handler_type;

// The Phrase Parse Context that installs space skipper into parsing context

typedef x3::phrase_parse_context<x3::ascii::space_type>::type phrase_context_type;

// Combined Error Handler and Phrase Parse Context. This parsing context should be
// used in combination with `x3::phrase_parse`, ie:
//
//   x3::phrase_parse(iter, end, parser, x3::ascii::space, ast)

typedef x3::context<x3::error_handler_tag, std::reference_wrapper<error_handler_type>,
                    phrase_context_type>
  context_type;

} // namespace parser
} // namespace snapshot_parsing
} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
