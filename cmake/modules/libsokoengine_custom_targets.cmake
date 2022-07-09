# .......................................................................................
# `make dist` target
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

# .......................................................................................
# `make docs` target
# .......................................................................................
if(DOXYGEN_FOUND)
    set(_FOO "${CMAKE_BINARY_DIR}/docs/libsokoengine-v${libsokoengine_VERSION}")
    file(MAKE_DIRECTORY "${_FOO}")

    # set(DOXYGEN_PROJECT_NAME "libsokoengine")
    # set(DOXYGEN_PROJECT_NUMBER "libsokoengine")
    set(DOXYGEN_OUTPUT_DIRECTORY "${_FOO}")
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
    set(DOXYGEN_FILE_PATTERNS
        "*.hpp"
        "*.h"
    )
    set(DOXYGEN_RECURSIVE "YES")
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
    set(DOXYGEN_EXAMPLE_PATH "${CMAKE_SOURCE_DIR}/docs/images")
    set(DOXYGEN_IMAGE_PATH "${CMAKE_SOURCE_DIR}/docs/images")
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
        ${CMAKE_SOURCE_DIR}/src/libsokoengine
    )
endif(DOXYGEN_FOUND)

# .......................................................................................
# make "valgrind_" targets
# Two functions that allow us to add valgring builds for executables
#
# 1. Builds executable, runs it under callgrind which dumps profile data into file.
# This file can later be analyzed via ie. KCacheGrind gui.
#
# add_executable(mytarget mysource.cpp)
# add_valgrind_profile_dump_target(mytarget)
#
# 2. Builds executable and runs it under memcheck
#
# add_executable(mytarget mysource.cpp)
# add_valgrind_memory_check_target(mytarget)
# .......................................................................................
function(add_valgrind_profile_dump_target for_target_name)
    if(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
        set(dump_file "${CMAKE_BINARY_DIR}/${for_target_name}_dump.pid")
        set(valgrind_args
            --dump-line=yes
            --dump-instr=yes
            --tool=callgrind
            --collect-jumps=yes
            --callgrind-out-file="${dump_file}"
        )
        set(valgrind_target_name "valgrind_profile_${for_target_name}")

        # get_target_property(binary_location ${for_target_name} LOCATION)
        # add_custom_target(${valgrind_target_name} COMMAND valgrind ${valgrind_args} ${binary_location})
        add_custom_target(
            ${valgrind_target_name}
            COMMAND valgrind ${valgrind_args} $<TARGET_FILE:${for_target_name}>
        )
        add_dependencies(${valgrind_target_name} ${for_target_name})
        set_target_properties(
            ${valgrind_target_name} PROPERTIES EXCLUDE_FROM_DEFAULT_BUILD 1
        )
    endif()
endfunction(add_valgrind_profile_dump_target)

function(add_valgrind_memory_check_target for_target_name)
    if(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
        set(valgrind_args
            --num-callers=50
            --leak-check=full
            --partial-loads-ok=yes
            --undef-value-errors=no
            --show-reachable=yes
            --error-limit=no

            # uncomment next two lines to generate suppression blocks in valgrind log
            # These blocks can then be added to .libsokoengine.supp
            # --gen-suppressions=all
            # --log-file="${CMAKE_BINARY_DIR}/valgrind_memcheck.log"
            # --suppressions="${CMAKE_SOURCE_DIR}/.libsokoengine.supp"
        )
        set(valgrind_target_name "valgrind_check_${for_target_name}")

        # get_target_property(binary_location ${for_target_name} LOCATION)
        # add_custom_target(${valgrind_target_name} COMMAND G_DEBUG=gc-friendly G_SLICE=always-malloc valgrind ${valgrind_args} ${binary_location})
        add_custom_target(
            ${valgrind_target_name}
            COMMAND G_DEBUG=gc-friendly G_SLICE=always-malloc valgrind ${valgrind_args} $<TARGET_FILE:${for_target_name}>
        )
        add_dependencies(${valgrind_target_name} ${for_target_name})
        set_target_properties(${valgrind_target_name}
            PROPERTIES EXCLUDE_FROM_DEFAULT_BUILD 1)
    endif()
endfunction(add_valgrind_memory_check_target)
