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
        ${CMAKE_SOURCE_DIR}/README.libsokoengine.md
    )
endif(DOXYGEN_FOUND)
