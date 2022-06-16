#ifndef PARSER_BDC825C2_4FAB_4173_9B94_185BD7430359
#define PARSER_BDC825C2_4FAB_4173_9B94_185BD7430359

#include "ast.hpp"

namespace sokoengine {
namespace io {
namespace snapshot_parsing {

class LIBSOKOENGINE_LOCAL Parser {
public:
  ///
  /// Parses src to AST, evaluates that AST and returns snapshot data as a sequence of
  /// steps, jumps and pusher selections.
  ///
  static evaluated_ast::SnapshotData parse(const std::string &src);

  ///
  /// Returns JSON representation of parser AST. Intended to be used for debugging
  /// purposes.
  ///
  static std::string ast_json(const std::string &line);
};

} // namespace snapshot_parsing
} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
