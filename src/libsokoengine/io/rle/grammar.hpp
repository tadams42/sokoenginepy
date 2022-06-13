#ifndef GRAMMAR_78FAAA5B_FC6F_4891_8173_B2B3C2BFA410
#define GRAMMAR_78FAAA5B_FC6F_4891_8173_B2B3C2BFA410

#include "puzzle.hpp"
#include "ast.hpp"
#include "ast_adapted.hpp"
#include "error_handler.hpp"
#include "snapshot.hpp"

namespace sokoengine {
namespace io {
namespace sok_rle {
namespace parser {
namespace ascii = boost::spirit::x3::ascii;

///////////////////////////////////////////////////////////////////////////
// Boost::X3 rule tags
//
// Rule tags can be annotated (x3::annotate_on_success) and can handle rule
// errors (inherit from our error_handler_base).
struct GrammarTag : ErrorHandlerBase {};
struct AtomsOrRleOrGroupTag {};
struct AtomOrGroupTag {};
struct RleChunkTag {};
struct GroupTag {};
struct AtomsTag {};
struct AtomTag {};

///////////////////////////////////////////////////////////////////////////
// Boost::X3 rules declaration
//
// clang-format off
x3::rule<GrammarTag, ast::RleData> const grammar = "grammar";
x3::rule<AtomsOrRleOrGroupTag, ast::AtomsOrRleOrGroup> const atoms_or_rle_or_group = "atoms_or_rle_or_group";
x3::rule<AtomOrGroupTag, ast::AtomOrGroup> const atom_or_group = "atom_or_group";
x3::rule<RleChunkTag, ast::RleChunk> const rle_chunk = "rle_chunk";
x3::rule<GroupTag, ast::Group> const group = "group";
x3::rule<AtomsTag, ast::Atoms> const atoms = "atoms";
x3::rule<AtomTag, ast::Atom> const atom = "atom";
// clang-format on

///////////////////////////////////////////////////////////////////////////
// Boost::X3 rules definition
//
// Grammar described by these rules is similar to following Peg.JS grammar
// (pegsh http://phrogz.net/js/pegsh/):
//
//   grammar               = atoms_or_rle_or_group+
//   atoms_or_rle_or_group = atoms / rle_chunk / group
//   atom_or_group         = atom / group
//   rle_chunk             = count atom_or_group
//   group                 = "(" atoms_or_rle_or_group+ ")"
//   atoms                 = atom+
//   atom                  = [a-zA-Z \r\n\t#@+$*.\-_\|]
//   count                 = [0-9]+
//
// clang-format off
auto const grammar_def               = (+atoms_or_rle_or_group);
auto const atoms_or_rle_or_group_def = (atoms | rle_chunk | group);
auto const atom_or_group_def         = (atom | group);
auto const rle_chunk_def             = (x3::uint_ > atom_or_group);
auto const group_def                 = (
                                         x3::lit(Rle::GROUP_START)
                                         > (+atoms_or_rle_or_group)
                                         > x3::lit(Rle::GROUP_END)
                                       );
auto const atoms_def                 = (+atom);
auto const atom_def                  = ascii::space
                                       | ascii::alpha
                                       | ascii::char_(Rle::EOL)
                                       | ascii::char_(Puzzle::WALL)
                                       | ascii::char_(Puzzle::PUSHER)
                                       | ascii::char_(Puzzle::PUSHER_ON_GOAL)
                                       | ascii::char_(Puzzle::BOX)
                                       | ascii::char_(Puzzle::BOX_ON_GOAL)
                                       | ascii::char_(Puzzle::GOAL)
                                       | ascii::char_(Puzzle::FLOOR)
                                       | ascii::char_(Puzzle::VISIBLE_FLOOR)
                                       | ascii::char_(Puzzle::ALT_VISIBLE_FLOOR1)
                                       | ascii::char_(Snapshot::JUMP_BEGIN)
                                       | ascii::char_(Snapshot::JUMP_END)
                                       | ascii::char_(Snapshot::PUSHER_CHANGE_BEGIN)
                                       | ascii::char_(Snapshot::PUSHER_CHANGE_END)
                                       | ascii::char_(Snapshot::CURRENT_POSITION_CH)
                                     ;
// clang-format on

BOOST_SPIRIT_DEFINE(atoms_or_rle_or_group, rle_chunk, group, atoms, atom, atom_or_group,
                    grammar)

} // namespace parser

using parser::grammar;

} // namespace sok_rle
} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
