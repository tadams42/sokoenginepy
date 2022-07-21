# .......................................................................................
# `make dist` target
# .......................................................................................
if(GIT_FOUND AND GZIP_FOUND)
    add_custom_target(
        dist
        COMMAND git archive -7 --format=tar.gz --prefix=libsokoengine-${PROJECT_VERSION}/ --output=${CMAKE_BINARY_DIR}/libsokoengine-${PROJECT_VERSION}.tar.gz HEAD
        BYPRODUCTS ${CMAKE_BINARY_DIR}/libsokoengine-${PROJECT_VERSION}.tar.gz
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        COMMAND_EXPAND_LISTS
        COMMENT "Generating distribution tarball..."
    )
endif()

# .......................................................................................
# `make symbols` and `make subols_pyext` targets
# .......................................................................................

# WARNING: This is wrong for multi-config generators because they don't use
# and typically don't even set CMAKE_BUILD_TYPE
if(
    NM_FOUND AND CUT_FOUND AND SORT_FOUND
    AND(
    CMAKE_BUILD_TYPE STREQUAL Release
    OR CMAKE_BUILD_TYPE STREQUAL MinSizeRel
    OR CMAKE_BUILD_TYPE STREQUAL RelWithDebInfo
    )
)
    add_custom_target(
        symbols
        COMMAND ${CMAKE_SOURCE_DIR}/bin/symbols.sh $<TARGET_FILE:sokoengine> "${CMAKE_SOURCE_DIR}/docs/internal/symbols_libsokoengine"
        BYPRODUCTS "${CMAKE_SOURCE_DIR}/docs/internal/symbols_libsokoengine"
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        COMMAND_EXPAND_LISTS
        COMMENT "Generating library symbols list..."
    )
    add_dependencies(symbols sokoengine)

    if(Python3_FOUND AND pybind11_FOUND)
        add_custom_target(
            symbols_pyext
            COMMAND ${CMAKE_SOURCE_DIR}/bin/symbols.sh $<TARGET_FILE:sokoenginepyext> "${CMAKE_SOURCE_DIR}/docs/internal/symbols_sokoenginepyext"
            BYPRODUCTS "${CMAKE_SOURCE_DIR}/docs/internal/symbols_sokoenginepyext"
            WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
            COMMAND_EXPAND_LISTS
            COMMENT "Generating Python extension symbols list..."
        )
        add_dependencies(symbols_pyext sokoenginepyext)
    endif()
endif()

# .......................................................................................
# make "valgrind_" targets
# Two functions that allow us to add valgring builds for executables
#
# 1. Builds executable, runs it under callgrind which dumps profile data into file.
# This file can later be analyzed via ie. KCacheGrind gui.
#
# add_executable(mytarget mysource.cpp)
# add_callgrind_target(mytarget)
#
# 2. Builds executable and runs it under memcheck
#
# add_executable(mytarget mysource.cpp)
# add_memcheck_target(mytarget)
# .......................................................................................
function(add_callgrind_target for_target_name)
    if(VALGRIND_FOUND)
        set(dump_file "${CMAKE_BINARY_DIR}/${for_target_name}_dump.pid")
        set(valgrind_args
            --dump-line=yes
            --dump-instr=yes
            --tool=callgrind
            --collect-jumps=yes
            --callgrind-out-file="${dump_file}"
        )
        set(valgrind_target_name "callgrind_${for_target_name}")

        # get_target_property(binary_location ${for_target_name} LOCATION)
        # add_custom_target(${valgrind_target_name} COMMAND valgrind ${valgrind_args} ${binary_location})
        add_custom_target(
            ${valgrind_target_name}
            COMMAND valgrind ${valgrind_args} $<TARGET_FILE:${for_target_name}>
        )
        add_dependencies(${valgrind_target_name} ${for_target_name})
        set_target_properties(
            ${valgrind_target_name}
            PROPERTIES
            EXCLUDE_FROM_ALL 1
            EXCLUDE_FROM_DEFAULT_BUILD 1
        )
    endif()
endfunction(add_callgrind_target)

function(add_memcheck_target for_target_name)
    if(VALGRIND_FOUND)
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
        set(valgrind_target_name "memcheck_${for_target_name}")

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
endfunction(add_memcheck_target)
