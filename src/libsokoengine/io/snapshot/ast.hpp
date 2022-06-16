#ifndef AST_BDC825C2_4FAB_4173_9B94_185BD7430359
#define AST_BDC825C2_4FAB_4173_9B94_185BD7430359

#include "config.hpp"

#include <boost/spirit/home/x3/support/ast/variant.hpp>
#include <list>
#include <variant>

namespace sokoengine {

namespace game {
class BaseTessellation;
class PusherStep;
} // namespace game

namespace io {
namespace snapshot_parsing {

namespace evaluated_ast {

typedef std::vector<game::PusherStep> Converted;

class LIBSOKOENGINE_LOCAL Steps {
public:
  std::string data;
  bool is_jump = false;

  size_t pushes_count() const;
  size_t moves_count() const;
  const std::string &to_str() const;
  Converted
  pusher_steps(const game::BaseTessellation &tessellation) const;
};

class LIBSOKOENGINE_LOCAL Jump {
public:
  std::string data;
  bool is_jump = true;

  size_t pushes_count() const;
  size_t moves_count() const;
  std::string to_str() const;
  Converted
  pusher_steps(const game::BaseTessellation &tessellation) const;
};

class LIBSOKOENGINE_LOCAL PusherSelection {
public:
  std::string data;
  bool is_jump = false;

  size_t pushes_count() const;
  size_t moves_count() const;
  std::string to_str() const;
  Converted
  pusher_steps(const game::BaseTessellation &tessellation) const;
};

typedef std::variant<Steps, PusherSelection, Jump> parsed_type_t;
typedef std::vector<parsed_type_t> SnapshotData;

} // namespace evaluated_ast

namespace ast {

namespace x3 = boost::spirit::x3;

struct LIBSOKOENGINE_LOCAL Moves {
  std::string data;
};

struct LIBSOKOENGINE_LOCAL Pushes {
  std::string data;
};

struct LIBSOKOENGINE_LOCAL MovesOrPushes : x3::variant<Moves, Pushes> {
  using base_type::base_type;
  using base_type::operator=;
};

struct LIBSOKOENGINE_LOCAL Steps {
  std::list<MovesOrPushes> data;
};

struct LIBSOKOENGINE_LOCAL PusherSelection {
  Moves data;
};

struct LIBSOKOENGINE_LOCAL Jump {
  Moves data;
};

struct LIBSOKOENGINE_LOCAL JumpOrSelectOrMove
  : x3::variant<Steps, PusherSelection, Jump> {
  using base_type::base_type;
  using base_type::operator=;
};

struct LIBSOKOENGINE_LOCAL Snapshot {
  std::list<JumpOrSelectOrMove> data;
};

} // namespace ast
} // namespace snapshot_parsing
} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
