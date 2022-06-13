#ifndef GRAMMAR_BDC825C2_4FAB_4173_9B94_185BD7430359
#define GRAMMAR_BDC825C2_4FAB_4173_9B94_185BD7430359

#include "ast.hpp"
#include "ast_adapted.hpp"
#include "error_handler.hpp"
#include "snapshot.hpp"

namespace sokoengine {
namespace io {
namespace snapshot_parsing {
namespace parser {

namespace ascii = boost::spirit::x3::ascii;

///////////////////////////////////////////////////////////////////////////
// Boost::X3 rule tags
//
// Rule tags can be annotated (x3::annotate_on_success) and can handle rule errors
// (inherit from our error_handler_base).
struct GrammarTag : ErrorHandlerBase {};
struct JumpOrSelectOrMoveTag {};
struct JumpTag {};
struct PusherSelectionTag {};
struct StepsTag {};
struct MovesOrPushesTag {};
struct PushesTag {};
struct MovesTag {};

///////////////////////////////////////////////////////////////////////////
// Boost::X3 rules declaration
//
// clang-format off
x3::rule<GrammarTag, ast::Snapshot> const grammar = "grammar";
x3::rule<JumpOrSelectOrMoveTag, ast::JumpOrSelectOrMove> const jump_or_select_or_move = "jump_or_select_or_move";
x3::rule<JumpTag, ast::Jump> const jump = "jump";
x3::rule<PusherSelectionTag, ast::PusherSelection> const pusher_selection = "pusher_selection";
x3::rule<StepsTag, ast::Steps> const steps = "steps";
x3::rule<MovesOrPushesTag, ast::MovesOrPushes> const moves_or_pushes = "moves_or_pushes";
x3::rule<PushesTag, ast::Pushes> const pushes = "pushes";
x3::rule<MovesTag, ast::Moves> const moves = "moves";
// clang-format on

///////////////////////////////////////////////////////////////////////////
// Boost::X3 rules definition
//
// Grammar described by these rules is similar to following Peg.JS grammar
// (pegsh http://phrogz.net/js/pegsh/):
//
//
//     grammar = (jump / pusher_selection / steps)+
//     jump = "[" moves* "]"
//     pusher_selection = "{" moves "}"
//     steps = (moves / pushes)+
//     moves = [dewnsulr\*]+
//     pushes = [SRENWUDL]+
//
// clang-format off

auto const grammar_def                = (+jump_or_select_or_move);
auto const jump_or_select_or_move_def = (jump | pusher_selection | steps);
auto const jump_def                   = (
                                            x3::lit(Snapshot::JUMP_BEGIN)
                                            > (*moves)
                                            > x3::lit(Snapshot::JUMP_END)
                                        );
auto const pusher_selection_def       = (
                                          x3::lit(Snapshot::PUSHER_CHANGE_BEGIN)
                                          > (+moves)
                                          > x3::lit(Snapshot::PUSHER_CHANGE_END)
                                        );
auto const moves_or_pushes_def        = (moves | pushes);
auto const steps_def                  = (+moves_or_pushes);
auto const moves_def                  = (+(
                                          ascii::char_(Snapshot::l)
                                          | ascii::char_(Snapshot::u)
                                          | ascii::char_(Snapshot::r)
                                          | ascii::char_(Snapshot::d)
                                          | ascii::char_(Snapshot::w)
                                          | ascii::char_(Snapshot::e)
                                          | ascii::char_(Snapshot::n)
                                          | ascii::char_(Snapshot::s)
                                          | ascii::char_(Snapshot::CURRENT_POSITION_CH)
                                        ));
auto const pushes_def                  = (+(
                                          ascii::char_(Snapshot::L)
                                          | ascii::char_(Snapshot::U)
                                          | ascii::char_(Snapshot::R)
                                          | ascii::char_(Snapshot::D)
                                          | ascii::char_(Snapshot::W)
                                          | ascii::char_(Snapshot::E)
                                          | ascii::char_(Snapshot::N)
                                          | ascii::char_(Snapshot::S)
                                        ));
// clang-format on

BOOST_SPIRIT_DEFINE(pushes, moves, steps, moves_or_pushes, pusher_selection, jump,
                    jump_or_select_or_move, grammar)

} // namespace parser

using parser::grammar;

} // namespace snapshot_parsing
} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
