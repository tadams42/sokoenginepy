#ifndef AST_BDC825C2_4FAB_4173_9B94_185BD7430359
#define AST_BDC825C2_4FAB_4173_9B94_185BD7430359

#include "sokoengine_config.hpp"

#include <boost/spirit/home/x3/support/ast/variant.hpp>
#include <list>
#include <variant>

namespace sokoengine {

  namespace game {
    namespace implementation {
      class BaseTessellation;
    } // namespace implementation
    class PusherStep;
  } // namespace game

  namespace io {
    namespace snapshot_parsing {
      namespace evaluated_ast {

        typedef std::vector<game::PusherStep> Converted;

        class LIBSOKOENGINE_LOCAL Steps {
        public:
          std::string data;
          bool        is_jump = false;

          size_t             pushes_count() const;
          size_t             moves_count() const;
          const std::string &to_str() const;
          Converted
          pusher_steps(const game::implementation::BaseTessellation &tessellation
          ) const;
        };

        class LIBSOKOENGINE_LOCAL Jump {
        public:
          std::string data;
          bool        is_jump = true;

          size_t      pushes_count() const;
          size_t      moves_count() const;
          std::string to_str() const;
          Converted
          pusher_steps(const game::implementation::BaseTessellation &tessellation
          ) const;
        };

        class LIBSOKOENGINE_LOCAL PusherSelection {
        public:
          std::string data;
          bool        is_jump = false;

          size_t      pushes_count() const;
          size_t      moves_count() const;
          std::string to_str() const;
          Converted
          pusher_steps(const game::implementation::BaseTessellation &tessellation
          ) const;
        };

        typedef std::variant<Steps, PusherSelection, Jump> parsed_type_t;
        typedef std::vector<parsed_type_t>                 SnapshotData;

      } // namespace evaluated_ast

      namespace ast {

        // clang-format off
        // Beware of single-member-is-container AST structs
        //
        // https://github.com/boostorg/spirit/issues/463
        // https://github.com/boostorg/spirit/pull/178
        // https://stackoverflow.com/questions/50252680/boost-spirit-x3-parser-no-type-named-type-in
        //
        // When making an AST type, I'm always going into 1 of these:
        //
        // AST type of 1 member T: overload operator=(T)
        // AST type of 2+ members: BOOST_FUSION_ADAPT_STRUCT
        // AST type that inherits from some container (no further code required but must not contain members)
        // AST type that inherits from x3::variant: add using base_type::base_type;, using base_type::operator=, must not contain members
        // Other mixes of AST types end in various (long long) compilation errors.
        // clang-format on

        namespace x3 = boost::spirit::x3;

        struct LIBSOKOENGINE_LOCAL Moves : std::vector<char> {
          using std::vector<char>::vector;
          using std::vector<char>::operator=;
        };

        struct LIBSOKOENGINE_LOCAL Pushes : std::vector<char> {
          using std::vector<char>::vector;
          using std::vector<char>::operator=;
        };

        struct LIBSOKOENGINE_LOCAL MovesOrPushes : x3::variant<Moves, Pushes> {
          using base_type::base_type;
          using base_type::operator=;
        };

        struct LIBSOKOENGINE_LOCAL Steps : std::list<MovesOrPushes> {
          using std::list<MovesOrPushes>::list;
          using std::list<MovesOrPushes>::operator=;
        };

        struct LIBSOKOENGINE_LOCAL PusherSelection : std::vector<char> {
          using std::vector<char>::vector;
          using std::vector<char>::operator=;
        };

        struct LIBSOKOENGINE_LOCAL Jump : std::vector<char> {
          using std::vector<char>::vector;
          using std::vector<char>::operator=;
        };

        struct LIBSOKOENGINE_LOCAL JumpOrSelectOrMove
          : x3::variant<Steps, PusherSelection, Jump> {
          using base_type::base_type;
          using base_type::operator=;
        };

        // struct LIBSOKOENGINE_LOCAL Snapshot { std::list<JumpOrSelectOrMove> data; };
        struct LIBSOKOENGINE_LOCAL Snapshot : std::list<JumpOrSelectOrMove> {
          using std::list<JumpOrSelectOrMove>::list;
          using std::list<JumpOrSelectOrMove>::operator=;
        };

      } // namespace ast
    }   // namespace snapshot_parsing
  }     // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
