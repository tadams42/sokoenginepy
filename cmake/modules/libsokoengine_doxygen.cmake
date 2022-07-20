find_package(Doxygen COMPONENTS dot OPTIONAL_COMPONENTS mscgen dia)

# .......................................................................................
# `make docs` target
# .......................................................................................
if(DOXYGEN_FOUND)
    set(DOCS_OUT "${CMAKE_BINARY_DIR}/doxygen")
    file(MAKE_DIRECTORY "${DOCS_OUT}")

    set(PAGES_DIR "${DOCS_OUT}/generated_pages")
    file(MAKE_DIRECTORY "${PAGES_DIR}")
    set(PAGES_DOX "${PAGES_DIR}/pages.dox")
    file(
        WRITE
        ${PAGES_DOX} "\
        /// @file\n \
        \n \
        /// @page sok_fileformat SokobanYASC .sok file format\n \
        /// @include SOK_format_specification.txt\n \
        \n \
        /// @page license LICENSE\n \
        /// @include LICENSE\n \
    ")
    file(COPY "${CMAKE_SOURCE_DIR}/LICENSE" DESTINATION ${PAGES_DIR})
    file(COPY "${CMAKE_SOURCE_DIR}/src/sokoenginepy/io/SOK_format_specification.txt" DESTINATION ${PAGES_DIR})

    set(DOXYGEN_OUTPUT_DIRECTORY "${DOCS_OUT}")
    set(DOXYGEN_BRIEF_MEMBER_DESC "NO")
    set(DOXYGEN_ALWAYS_DETAILED_SEC "YES")
    set(DOXYGEN_INLINE_INHERITED_MEMB "YES")
    set(DOXYGEN_FULL_PATH_NAMES "NO")
    set(DOXYGEN_TAB_SIZE "2")
    set(DOXYGEN_BUILTIN_STL_SUPPORT "YES")
    set(DOXYGEN_DISTRIBUTE_GROUP_DOC "YES")
    set(DOXYGEN_TYPEDEF_HIDES_STRUCT "YES")
    set(DOXYGEN_EXTRACT_STATIC "YES")
    set(DOXYGEN_EXTRACT_LOCAL_CLASSES "NO")
    set(DOXYGEN_HIDE_FRIEND_COMPOUNDS "YES")
    set(DOXYGEN_HIDE_IN_BODY_DOCS "YES")
    set(DOXYGEN_SORT_MEMBERS_CTORS_1ST "YES")
    set(DOXYGEN_GENERATE_TODOLIST "NO")
    set(DOXYGEN_GENERATE_TESTLIST "NO")
    set(DOXYGEN_GENERATE_BUGLIST "NO")
    set(DOXYGEN_WARN_IF_UNDOCUMENTED "NO")
    set(DOXYGEN_RECURSIVE "YES")

    set(DOXYGEN_FILE_PATTERNS
        "*.hpp"
        "*.h"
    )

    set(DOXYGEN_EXCLUDE_PATTERNS
        "*/SOK_format_specification.h"
    )

    set(DOXYGEN_EXCLUDE_SYMBOLS
        "boost"
        "*BOOST_FILESYSTEM_*"
        "implementation"
        "sok_rle"
        "snapshot_parsing"
        "benchmarks"
    )

    set(DOXYGEN_EXAMPLE_PATH
        "${PAGES_DIR}"
    )

    set(DOXYGEN_IMAGE_PATH
        "${CMAKE_SOURCE_DIR}/docs/images"
        "${CMAKE_SOURCE_DIR}/docs/skin_format"
    )

    set(
        DOXYGEN_HTML_EXTRA_FILES
        "${CMAKE_SOURCE_DIR}/docs/skin_format/YASC_Skin_Tutorial_1_02.pdf"
    )

    set(DOXYGEN_VERBATIM_HEADERS "NO")
    set(DOXYGEN_GENERATE_TREEVIEW "YES")
    set(DOXYGEN_GENERATE_LATEX "NO")
    set(DOXYGEN_MACRO_EXPANSION "YES")
    set(DOXYGEN_EXPAND_ONLY_PREDEF "YES")
    set(DOXYGEN_PREDEFINED
        "__GNUC__=9"
        "LIBSOKOENGINE_DLL="
        "LIBSOKOENGINE_LOCAL="
        "LIBSOKOENGINE_API="
    )
    set(DOXYGEN_COLLABORATION_GRAPH "NO")
    set(DOXYGEN_GROUP_GRAPHS "NO")
    set(DOXYGEN_INCLUDED_BY_GRAPH "NO")
    set(DOXYGEN_DIRECTORY_GRAPH "NO")

    doxygen_add_docs(
        docs
        "${CMAKE_SOURCE_DIR}/src/libsokoengine"
        "${CMAKE_SOURCE_DIR}/INSTALL.md"
        "${CMAKE_SOURCE_DIR}/README.md"
        "${CMAKE_SOURCE_DIR}/docs/tutorial.md"
        "${CMAKE_SOURCE_DIR}/CHANGELOG.md"
        "${CMAKE_SOURCE_DIR}/docs/common_skins_format.md"
        "${PAGES_DOX}"
    )
endif(DOXYGEN_FOUND)
