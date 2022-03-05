#..............................................................................
# Configures cmake itself, before configuring libsokoengine source code

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(default_build_type "Release")
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    message(STATUS "Setting build type to '${default_build_type}' as none was specified.")
    set(CMAKE_BUILD_TYPE "${default_build_type}" CACHE STRING "Choose the type of build." FORCE)
    set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

include(CheckIncludeFileCXX)
include(CheckTypeSize)
include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

find_program(GZIP_FOUND gzip REQUIRED)
find_program(GIT_FOUND git REQUIRED)

include(libsokoegine_backwardlib)
include(libsokoengine_cppitertools)

# cmake --help-module FindBoost
set(Boost_USE_STATIC_LIBS        ON)
set(Boost_USE_MULTITHREADED      OFF)
set(Boost_USE_STATIC_RUNTIME     OFF)
# We are using C++14 bind and placeholders, this prevents name clashes
add_definitions(-DBOOST_BIND_NO_PLACEHOLDERS)
# Avoid name clashes with std, since we don't use Boost.Serialization
add_definitions(-DBOOST_MULTI_INDEX_DISABLE_SERIALIZATION)
find_package(Boost 1.65.0 REQUIRED)

#.......................................................................................
#                    `make docs` target
#.......................................................................................
find_package(Doxygen COMPONENTS dot OPTIONAL_COMPONENTS mscgen dia)

if(DOXYGEN_FOUND)
    set(_FOO "${CMAKE_BINARY_DIR}/docs/libsokoengine-v${libsokoengine_VERSION}")
    file(MAKE_DIRECTORY "${_FOO}")

    set(DOXYGEN_OUTPUT_DIRECTORY       "${_FOO}")
    set(DOXYGEN_BRIEF_MEMBER_DESC      "NO")
    set(DOXYGEN_ALWAYS_DETAILED_SEC    "YES")
    set(DOXYGEN_INLINE_INHERITED_MEMB  "YES")
    set(DOXYGEN_FULL_PATH_NAMES        "NO")
    set(DOXYGEN_EXTENSION_MAPPING      "doxydoc=C++")
    set(DOXYGEN_TOC_INCLUDE_HEADINGS   "0")
    set(DOXYGEN_BUILTIN_STL_SUPPORT    "YES")
    set(DOXYGEN_DISTRIBUTE_GROUP_DOC   "YES")
    set(DOXYGEN_TYPEDEF_HIDES_STRUCT   "YES")
    set(DOXYGEN_EXTRACT_STATIC         "YES")
    set(DOXYGEN_EXTRACT_LOCAL_CLASSES  "NO")
    set(DOXYGEN_HIDE_UNDOC_CLASSES     "YES")
    set(DOXYGEN_HIDE_FRIEND_COMPOUNDS  "YES")
    set(DOXYGEN_HIDE_IN_BODY_DOCS      "YES")
    set(DOXYGEN_INLINE_INFO            "NO")
    set(DOXYGEN_SORT_BRIEF_DOCS        "YES")
    set(DOXYGEN_SORT_MEMBERS_CTORS_1ST "YES")
    set(DOXYGEN_SORT_GROUP_NAMES       "YES")
    set(DOXYGEN_SORT_BY_SCOPE_NAME     "YES")
    set(DOXYGEN_GENERATE_TODOLIST      "NO")
    set(DOXYGEN_GENERATE_TESTLIST      "NO")
    set(DOXYGEN_GENERATE_BUGLIST       "NO")
    set(DOXYGEN_TAB_SIZE               "2")
    set(DOXYGEN_RECURSIVE              "YES")
    set(DOXYGEN_EXCLUDE_SYMLINKS       "YES")
    set(DOXYGEN_REFERENCES_LINK_SOURCE "NO")
    set(DOXYGEN_COLS_IN_ALPHA_INDEX    "2")
    set(DOXYGEN_HTML_OUTPUT            "./html")
    set(DOXYGEN_HTML_TIMESTAMP         "YES")
    set(DOXYGEN_HTML_DYNAMIC_SECTIONS  "YES")
    set(DOXYGEN_BINARY_TOC             "YES")
    set(DOXYGEN_GENERATE_TREEVIEW      "YES")
    set(DOXYGEN_ENUM_VALUES_PER_LINE   "1")
    set(DOXYGEN_SEARCHENGINE           "NO")
    set(DOXYGEN_GENERATE_LATEX         "NO")
    set(DOXYGEN_GENERATE_XML           "YES")
    set(DOXYGEN_XML_OUTPUT             "./xml")
    set(DOXYGEN_MACRO_EXPANSION        "YES")
    set(DOXYGEN_EXPAND_ONLY_PREDEF     "YES")
    set(DOXYGEN_HIDE_UNDOC_RELATIONS   "NO")
    set(DOXYGEN_COLLABORATION_GRAPH    "NO")
    set(DOXYGEN_TEMPLATE_RELATIONS     "YES")
    set(DOXYGEN_INCLUDED_BY_GRAPH      "NO")
    set(DOXYGEN_DIRECTORY_GRAPH        "NO")

    set(DOXYGEN_FILE_PATTERNS
        "*.cpp"
        "*.hpp"
        "*.h"
        "*.doxydoc"
        "*.md"
    )
    set(DOXYGEN_EXCLUDE_PATTERNS
        "*/utf8/*"
        "*/boost/*"
        "*boost/*"
        "*/SOK_format_specification.h"
    )
    set(DOXYGEN_EXCLUDE_SYMBOLS
        "*boost*"
        "*boost/*"
        "*BOOST_FILESYSTEM_*"
        "*PIMPL*"
        "*sokoengine::operator!=*"
        "*sokoengine::operator==*"
        "implementation"
    )
    set(DOXYGEN_PREDEFINED
        "__GNUC__=3"
        "LIBSOKOENGINE_API"
        "LIBSOKOENGINE_LOCAL"
    )

    doxygen_add_docs(
        docs
        ${CMAKE_SOURCE_DIR}/src/libsokoengine
        ${CMAKE_SOURCE_DIR}/README.md
    )
endif(DOXYGEN_FOUND)

# .......................................................................................
#                   `make dist` target
# .......................................................................................
add_custom_target(
    dist
    COMMAND git archive -7 --format=tar.gz --prefix=libsokoengine-${PROJECT_VERSION}/ --output=${CMAKE_BINARY_DIR}/libsokoengine-${PROJECT_VERSION}.tar.gz HEAD
    BYPRODUCTS
        ${CMAKE_BINARY_DIR}/libsokoengine-${PROJECT_VERSION}.tar.gz
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMAND_EXPAND_LISTS
    COMMENT "Generating distribution tarball..."
)
