#ifndef SOKOENGINE_CONFIG_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define SOKOENGINE_CONFIG_0FEA723A_C86F_6753_04ABD475F6FCA5FB

// #############################################################################
//                    Macros for symbols exporting
//                  https://gcc.gnu.org/wiki/Visibility
// #############################################################################

// Generic helper definitions for shared library support
#if defined _WIN32 || defined __CYGWIN__
    #define LIBSOKOENGINE_HELPER_DLL_IMPORT __declspec(dllimport)
    #define LIBSOKOENGINE_HELPER_DLL_EXPORT __declspec(dllexport)
    #define LIBSOKOENGINE_HELPER_DLL_LOCAL
#else
    #if __GNUC__ >= 4 || defined __clang__
        #define LIBSOKOENGINE_HELPER_DLL_IMPORT __attribute__((visibility("default")))
        #define LIBSOKOENGINE_HELPER_DLL_EXPORT __attribute__((visibility("default")))
        #define LIBSOKOENGINE_HELPER_DLL_LOCAL __attribute__((visibility("hidden")))
    #else
        #define LIBSOKOENGINE_HELPER_DLL_IMPORT
        #define LIBSOKOENGINE_HELPER_DLL_EXPORT
        #define LIBSOKOENGINE_HELPER_DLL_LOCAL
    #endif
#endif

// Now we use the generic helper definitions above to define LIBSOKOENGINE_API and
// LIBSOKOENGINE_LOCAL. LIBSOKOENGINE_API is used for the public API symbols. It either
// DLL imports or DLL exports (or does nothing for static build) LIBSOKOENGINE_LOCAL is
// used for non-api symbols.

#ifdef LIBSOKOENGINE_DLL         // defined if LIBSOKOENGINE is compiled as a DLL
    #ifdef LIBSOKOENGINE_DLL_EXPORTS // libsokoengine shared library is being built
        #define LIBSOKOENGINE_API LIBSOKOENGINE_HELPER_DLL_EXPORT
    #else                            // libsokoengine shared library is being used
        #define LIBSOKOENGINE_API LIBSOKOENGINE_HELPER_DLL_IMPORT
    #endif // LIBSOKOENGINE_DLL_EXPORTS
    #define LIBSOKOENGINE_LOCAL LIBSOKOENGINE_HELPER_DLL_LOCAL
#else // LIBSOKOENGINE_DLL is not defined: this means LIBSOKOENGINE is a static lib.
    #define LIBSOKOENGINE_API
    #define LIBSOKOENGINE_LOCAL
#endif // LIBSOKOENGINE_DLL

// #############################################################################
//                      typedefs and global constants
// #############################################################################

#include <cstdint>
#include <limits>
#include <vector>
#include <string>

///
/// Top namespace for libsokoengine
///
namespace sokoengine {

///
/// Namespace for game engine part of sokoengine
///
namespace game {}

///
/// Default type for sequence of strings.
///
typedef std::vector<std::string> Strings;

///
/// Board size type
///
typedef uint32_t board_size_t;

///
/// Board position type.
///
typedef uint32_t position_t;

///
/// Max board width.
///
constexpr static board_size_t MAX_WIDTH = 4096;

static_assert(MAX_WIDTH < std::numeric_limits<board_size_t>::max(),
              "MAX_WIDTH must be < std::numeric_limits<board_size_t>::max()");

///
/// Max board height.
///
constexpr static board_size_t MAX_HEIGHT = 4096;

static_assert(MAX_HEIGHT < std::numeric_limits<board_size_t>::max(),
              "MAX_HEIGHT must be < std::numeric_limits<board_size_t>::max()");

///
/// Max board 1D positions
///
constexpr static position_t MAX_POS = (position_t)(MAX_HEIGHT * MAX_WIDTH - 1);

static_assert(MAX_POS < MAX_HEIGHT * MAX_WIDTH,
              "MAX_POS must be < MAX_HEIGHT * MAX_WIDTH");

static_assert(MAX_POS < std::numeric_limits<position_t>::max(),
              "MAX_POS must be < std::numeric_limits<position_t>::max()");

///
/// Piece ID and Sokoban+ ID type.
///
typedef uint16_t piece_id_t;

///
/// Default ID of a piece (box, goal or pusher) - ID assigned to first pusher,
/// box or goal on board.
///
/// Piece ids are assigned sequentially to all board pieces starting  with
/// DEFAULT_PIECE_ID.
///
constexpr static const piece_id_t DEFAULT_PIECE_ID = 1;

///
/// Value that represents state where ID of a piece has not yet been assigned to it.
///
constexpr static const piece_id_t NULL_ID = 0;

static_assert(NULL_ID < DEFAULT_PIECE_ID, "NULL_ID must be < DEFAULT_PIECE_ID");

///
/// Zobrist key storage.
///
typedef uint64_t zobrist_key_t;

} // namespace sokoengine

#endif // HEADER_GUARD
