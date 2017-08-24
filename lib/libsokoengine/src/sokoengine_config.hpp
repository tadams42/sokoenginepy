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
    #define LIBSOKOENGINE_HELPER_DLL_IMPORT __attribute__ ((visibility ("default")))
    #define LIBSOKOENGINE_HELPER_DLL_EXPORT __attribute__ ((visibility ("default")))
    #define LIBSOKOENGINE_HELPER_DLL_LOCAL  __attribute__ ((visibility ("hidden")))
  #else
    #define LIBSOKOENGINE_HELPER_DLL_IMPORT
    #define LIBSOKOENGINE_HELPER_DLL_EXPORT
    #define LIBSOKOENGINE_HELPER_DLL_LOCAL
  #endif
#endif

// Now we use the generic helper definitions above to define LIBSOKOENGINE_API and LIBSOKOENGINE_LOCAL.
// LIBSOKOENGINE_API is used for the public API symbols. It either DLL imports or DLL exports (or does nothing for static build)
// LIBSOKOENGINE_LOCAL is used for non-api symbols.

#ifdef LIBSOKOENGINE_DLL
  #undef LIBSOKOENGINE_DLL
#endif
#define LIBSOKOENGINE_DLL

#ifdef LIBSOKOENGINE_DLL // defined if LIBSOKOENGINE is compiled as a DLL
  #ifdef LIBSOKOENGINE_DLL_EXPORTS // defined if we are building the LIBSOKOENGINE DLL (instead of using it)
    #define LIBSOKOENGINE_API LIBSOKOENGINE_HELPER_DLL_EXPORT
  #else
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

enum {
  ///
  /// Default ID of a piece (box, goal or pusher)
  /// Piece ids are assigned sequentially on board creation and are not changed
  /// during lifetime of a board. Piece id is used to diferentiate this piece
  /// from other pieces of the same kind: ie. one box from another.
  ///
  DEFAULT_PIECE_ID = 1,
  ///
  /// Value that represents piece ID in cases where one ID was requested but it
  /// cant't be returned.
  ///
  NULL_ID = -2,
  ///
  /// Value that represents board position in cases where position was requested
  /// but it cant't be returned.
  ///
  NULL_POSITION = -1
};

typedef int position_t;
typedef int piece_id_t;

#endif // HEADER_GUARD
