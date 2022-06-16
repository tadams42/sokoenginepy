#ifndef ERR_78FAAA5B_FC6F_4891_8173_B2B3C2BFA410
#define ERR_78FAAA5B_FC6F_4891_8173_B2B3C2BFA410

#include "config.hpp"

#include <boost/spirit/home/x3.hpp>
#include <boost/spirit/home/x3/support/utility/error_reporting.hpp>
#include <map>
#include <string>

namespace sokoengine {
namespace io {
namespace sok_rle {
namespace x3 = boost::spirit::x3;
namespace parser {

struct LIBSOKOENGINE_LOCAL ErrorHandlerBase {
  ErrorHandlerBase() {
    id_map["grammar"] = "Sokoban RLE expression";
    id_map["atoms_or_rle_or_group"] =
      "one or more atoms, counted expresion or RLE group";
    id_map["atom_or_group"] = "single atom or RLE group";
    id_map["rle_chunk"] = "counted RLE expresion";
    id_map["group"] = "RLE group";
    id_map["atoms"] = "one or more atoms";
    id_map["atom"] = "single atom";
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
} // namespace sok_rle
} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
