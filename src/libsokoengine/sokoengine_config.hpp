#ifndef SOKOENGINE_CONFIG_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define SOKOENGINE_CONFIG_0FEA723A_C86F_6753_04ABD475F6FCA5FB

// #############################################################################
//                    Macros for symbols exporting
//                  https://gcc.gnu.org/wiki/Visibility
// #############################################################################
// clang-format off

// Generic helper definitions for shared library support
#if defined _WIN32 || defined __CYGWIN__
  #define LIBSOKOENGINE_HELPER_DLL_IMPORT __declspec(dllimport)
  #define LIBSOKOENGINE_HELPER_DLL_EXPORT __declspec(dllexport)
  #define LIBSOKOENGINE_HELPER_DLL_LOCAL
#else
  #if __GNUC__ >= 4 || defined __clang__
    #define LIBSOKOENGINE_HELPER_DLL_IMPORT __attribute__((visibility("default")))
    #define LIBSOKOENGINE_HELPER_DLL_EXPORT __attribute__((visibility("default")))
    #define LIBSOKOENGINE_HELPER_DLL_LOCAL  __attribute__((visibility("hidden")))
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
  #else // libsokoengine shared library is being used
    #define LIBSOKOENGINE_API LIBSOKOENGINE_HELPER_DLL_IMPORT
  #endif
  #define LIBSOKOENGINE_LOCAL LIBSOKOENGINE_HELPER_DLL_LOCAL
#else // LIBSOKOENGINE_DLL is not defined: this means LIBSOKOENGINE is a static lib.
  #define LIBSOKOENGINE_API
  #define LIBSOKOENGINE_LOCAL
#endif // LIBSOKOENGINE_DLL

// clang-format on

#include <cstdint>
#include <filesystem>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#endif // HEADER_GUARD
