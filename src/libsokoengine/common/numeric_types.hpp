#ifndef NUMERIC_TYPES_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define NUMERIC_TYPES_0FEA723A_C86F_6753_04ABD475F6FCA5FB
/// @file

#include "sokoengine_config.hpp"

///
/// Top namespace for libsokoengine
///
namespace sokoengine {

///
/// Board size type
///
typedef uint32_t board_size_t;

///
/// Board position type.
///
typedef uint32_t position_t;

///
/// Ordered collection of board positions usually describing continuous board path.
///
typedef std::vector<position_t> Positions;

///
/// Piece ID and Sokoban+ ID type.
///
typedef uint16_t piece_id_t;

///
/// Zobrist hash type
///
typedef uint64_t zobrist_key_t;

} // namespace sokoengine

#endif // HEADER_GUARD
