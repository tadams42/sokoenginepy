#include "parser.hpp"

#include "error_handler.hpp"
#include "evaluator.hpp"
#include "grammar.hpp"
#include "json_printer.hpp"
#include "snapshot_config.hpp"

using std::endl;
using std::ostream;
using std::ostringstream;
using std::string;

namespace sokoengine {
namespace io {
namespace snapshot_parsing {

namespace x3 = boost::spirit::x3;

using evaluated_ast::SnapshotData;
using snapshot_parsing::parser::error_handler_type;
using snapshot_parsing::parser::iterator_type;
using x3::with;

LIBSOKOENGINE_LOCAL bool _parse(iterator_type &iter, iterator_type end,
                                ast::Snapshot &into, ostream &err) {
  error_handler_type error_handler(iter, end, err);

  // we pass our error handler to the parser so we can access it later on in our
  // on_error and on_success handlers
  // clang-format off
    auto const parser =
      with<x3::error_handler_tag>(std::ref(error_handler))
      [
          snapshot_parsing::grammar
      ];
  // clang-format on

  return x3::phrase_parse(iter, end, parser, x3::ascii::space, into);
}

//
// Parses Sokoban RLE expression (board or snapshot) and produces JSON representation
// of AST. Prints JSON AST to dest.
//
// This one is mainly for experimentation and grammar debugging purposes.
//
LIBSOKOENGINE_LOCAL bool parse_to_ast(const string &src, ostream &dest, ostream &err) {
  iterator_type iter = src.begin();
  iterator_type end = src.end();
  ast::Snapshot ast;

  bool r = _parse(iter, end, ast, err);

  if (r && iter == end) {
    ast::JsonPrinter print(dest);
    print(ast);
    return true;
  } else {
    string rest(iter, end);
    err << "Parsing failed, stopped at: \"" << rest << "\"" << endl;
    return false;
  }
}

//
// Parses Sokoban RLE expression (board or snapshot) and expands RLE expressions
// into Sokoban data. Prints evaluated data to dest.
//
LIBSOKOENGINE_LOCAL bool parse_to_eval(const string &src, SnapshotData &dest,
                                       ostream &err) {
  iterator_type iter = src.begin();
  iterator_type end = src.end();
  ast::Snapshot ast;

  bool r = _parse(iter, end, ast, err);

  if (r && iter == end) {
    ast::Evaluator eval(dest);
    eval(ast);
    return true;
  } else {
    string rest(iter, end);
    err << "Parsing failed, stopped at: \"" << rest << "\"" << endl;
    return false;
  }
}

SnapshotData Parser::parse(const string &src) {
  SnapshotData out;
  ostringstream err;
  bool retv = parse_to_eval(src, out, err);

  if (!retv) { throw std::invalid_argument(err.str()); }

  return out;
}

string Parser::ast_json(const string &line) {
  ostringstream out, err;
  bool retv = parse_to_ast(line, out, err);

  if (!retv) { throw std::invalid_argument(err.str()); }

  return out.str();
}

} // namespace snapshot_parsing
} // namespace io
} // namespace sokoengine
