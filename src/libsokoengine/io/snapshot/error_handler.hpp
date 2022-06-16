#ifndef ERROR_BDC825C2_4FAB_4173_9B94_185BD7430359
#define ERROR_BDC825C2_4FAB_4173_9B94_185BD7430359

#include "config.hpp"

#include <boost/spirit/home/x3.hpp>
#include <boost/spirit/home/x3/support/utility/error_reporting.hpp>
#include <map>

namespace sokoengine {
namespace io {
namespace snapshot_parsing {
namespace x3 = boost::spirit::x3;
namespace parser {

struct LIBSOKOENGINE_LOCAL ErrorHandlerBase {
  ErrorHandlerBase() {
    id_map["grammar"] = "Snapshot";
    id_map["jump_or_select_or_move"] =
      "jump, pusher selection or pusher steps (moves or pushes)";
    id_map["jump"] = "jump";
    id_map["pusher_selection"] = "pusher selection";
    id_map["steps"] = "pusher steps (moves or pushes)";
    id_map["moves_or_pushes"] = "pusher steps (moves or pushes)";
    id_map["pushes"] = "one or more box pushes";
    id_map["moves"] = "one or more pusher moves (without pushing the box)";
  }

  template <typename Iterator, typename Exception, typename Context>
  x3::error_handler_result on_error(Iterator &first, Iterator const &last,
                                    Exception const &x, Context const &context);

  std::map<std::string, std::string> id_map;
};

template <typename Iterator, typename Exception, typename Context>
inline x3::error_handler_result
ErrorHandlerBase::on_error(Iterator &first, Iterator const &last, Exception const &x,
                           Context const &context) {
  auto &handler = x3::get<x3::error_handler_tag>(context).get();

  std::string which = boost::core::demangle(x.which().c_str());
  auto iter = id_map.find(which);
  if (iter != id_map.end()) which = iter->second;

  std::string message = "Error! Expecting: " + which + " here:";
  handler(x.where(), message);
  return x3::error_handler_result::fail;
}

} // namespace parser
} // namespace snapshot_parsing
} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
