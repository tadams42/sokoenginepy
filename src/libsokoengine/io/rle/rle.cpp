#include "rle.hpp"

#include "evaluator.hpp"
#include "grammar.hpp"
#include "json_printer.hpp"
#include "rle_config.hpp"

#include <algorithm>
#include <boost/algorithm/string.hpp>
#include <iostream>
#include <sstream>

using namespace std;

namespace sokoengine {
namespace io {
namespace sok_rle {

namespace x3 = boost::spirit::x3;

using sok_rle::ast::Evaluator;
using sok_rle::ast::JsonPrinter;
using sok_rle::parser::error_handler_type;
using sok_rle::parser::iterator_type;
using x3::with;

LIBSOKOENGINE_LOCAL bool _parse(iterator_type &iter, iterator_type end,
                                sok_rle::ast::RleData &into, std::ostream &err) {
  error_handler_type error_handler(iter, end, err);

  // we pass our error handler to the parser so we can access it later on in our
  // on_error and on_success handlers
  // clang-format off
    auto const parser =
      with<x3::error_handler_tag>(std::ref(error_handler))
      [
          sok_rle::grammar
      ];
  // clang-format on

  return x3::parse(iter, end, parser, into);
}

//
// Parses Sokoban RLE expression (board or snapshot) and produces JSON representation
// of AST. Prints JSON AST to dest.
//
// This one is mainly for experimentation and grammar debugging purposes.
//
LIBSOKOENGINE_LOCAL bool parse_to_ast(const std::string &src, std::ostream &dest,
                                      std::ostream &err) {
  iterator_type iter = src.begin();
  iterator_type end = src.end();
  sok_rle::ast::RleData ast;

  bool r = _parse(iter, end, ast, err);

  if (r && iter == end) {
    JsonPrinter print(dest);
    print(ast);
    return true;
  } else {
    std::string rest(iter, end);
    err << "Parsing failed, stopped at: \"" << rest << "\"" << std::endl;
    return false;
  }
}

//
// Parses Sokoban RLE expression (board or snapshot) and expands RLE expressions
// into Sokoban data. Prints evaluated data to dest.
//
LIBSOKOENGINE_LOCAL bool parse_to_eval(const std::string &src, std::ostream &dest,
                                       std::ostream &err) {
  iterator_type iter = src.begin();
  iterator_type end = src.end();
  sok_rle::ast::RleData ast;

  bool r = _parse(iter, end, ast, err);

  if (r && iter == end) {
    std::string out;
    Evaluator eval(out);
    eval(ast);
    dest << out;
    return true;
  } else {
    std::string rest(iter, end);
    err << "Parsing failed, stopped at: \"" << rest << "\"" << std::endl;
    return false;
  }
}

} // namespace sok_rle

string Rle::encode(const string &line) {
  string to_encode = line;

  if (any_of(to_encode.begin(), to_encode.end(), [](char c) { return isdigit(c); })) {
    throw invalid_argument("RLE can't encode strings with digits in them!");
  }

  if (to_encode.empty()) { return string(); }

  string::size_type found = 0, next_found = 0;
  ostringstream oss;
  next_found = to_encode.find_first_not_of(to_encode[found], found);
  while (next_found != string::npos) {
    if (next_found - found > 1) { oss << next_found - found; }
    oss << to_encode[found];
    found = next_found;
    next_found = to_encode.find_first_not_of(to_encode[found], found);
  }
  if (to_encode.length() - found > 1) { oss << to_encode.length() - found; }
  oss << to_encode[found];
  to_encode = oss.str();

  return to_encode;
}

string Rle::decode(const string &line) {
  ostringstream out, err;
  bool retv = sok_rle::parse_to_eval(line, out, err);

  if (!retv) { throw invalid_argument(err.str()); }

  return out.str();
}

string Rle::ast_json(const string &line) {
  ostringstream out, err;
  bool retv = sok_rle::parse_to_ast(line, out, err);

  if (!retv) { throw invalid_argument(err.str()); }

  return out.str();
}

} // namespace io
} // namespace sokoengine
