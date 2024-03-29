set(INSTALL_HEADERS
    sokoengine_config.hpp
    sokoengine.hpp
    benchmarks.hpp

    common/tile_shape.hpp
    common/direction.hpp
    common/game_config.hpp
    common/numeric_types.hpp
    common/tessellation.hpp

    game/board_cell.hpp
    game/board_graph.hpp
    game/board_manager.hpp
    game/board_state.hpp
    game/hashed_board_manager.hpp
    game/mover.hpp
    game/pusher_step.hpp
    game/sokoban_plus.hpp

    io/collection.hpp
    io/puzzle.hpp
    io/rle.hpp
    io/snapshot.hpp

    skins/skin.hpp
    skins/image.hpp
)

set(SELF_SOURCES
    common/characters.cpp
    common/characters.hpp
    common/direction.cpp
    common/hexoban_tessellation.cpp
    common/hexoban_tessellation.hpp
    common/octoban_tessellation.cpp
    common/octoban_tessellation.hpp
    common/sokoban_tessellation.cpp
    common/sokoban_tessellation.hpp
    common/tessellation_impl.cpp
    common/tessellation_impl.hpp
    common/trioban_tessellation.cpp
    common/trioban_tessellation.hpp

    game/board_cell.cpp
    game/board_graph.cpp
    game/board_manager.cpp
    game/board_state.cpp
    game/hashed_board_manager.cpp
    game/mover.cpp
    game/pusher_step.cpp
    game/sokoban_plus.cpp

    io/collection/collection.cpp
    io/collection/sok_file_format.cpp
    io/collection/sok_file_format.hpp
    io/collection/SOK_format_specification.h
    io/hexoban_io.cpp
    io/hexoban_io.hpp
    io/octoban_io.cpp
    io/octoban_io.hpp
    io/puzzle_parsing.cpp
    io/puzzle_parsing.hpp
    io/puzzle.cpp
    io/rle/ast_adapted.hpp
    io/rle/ast.hpp
    io/rle/error_handler.hpp
    io/rle/evaluator.hpp
    io/rle/grammar.hpp
    io/rle/json_printer.hpp
    io/rle/rle_config.hpp
    io/rle/rle.cpp
    io/snapshot/ast.cpp
    io/snapshot/ast.hpp
    io/snapshot/error_handler.hpp
    io/snapshot/evaluator.hpp
    io/snapshot/grammar.hpp
    io/snapshot/json_printer.hpp
    io/snapshot/parser.cpp
    io/snapshot/parser.hpp
    io/snapshot/snapshot_config.hpp
    io/snapshot/snapshot.cpp
    io/sokoban_io.cpp
    io/sokoban_io.hpp
    io/trioban_io.cpp
    io/trioban_io.hpp

    benchmarks.cpp

    skins/geometry.cpp
    skins/geometry.hpp
    skins/image_impl.cpp
    skins/image_impl.hpp
    skins/image.cpp
    skins/skin.cpp
    skins/common_skins_format.hpp
    skins/common_skins_format.cpp
    skins/sokoban_common_skins_format.hpp
    skins/sokoban_common_skins_format.cpp
    skins/trioban_common_skins_format.hpp
    skins/trioban_common_skins_format.cpp
    skins/hexoban_common_skins_format.hpp
    skins/hexoban_common_skins_format.cpp
    skins/octoban_common_skins_format.hpp
    skins/octoban_common_skins_format.cpp
)

set(SELF_INCLUDE_DIRS
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/common
    ${CMAKE_CURRENT_SOURCE_DIR}/game
    ${CMAKE_CURRENT_SOURCE_DIR}/io
    ${CMAKE_CURRENT_SOURCE_DIR}/skins
)

# ..............................................................................
# sokoengine OBJECT library with all sybmbols hidden
#
# This object library doesn't define "LIBSOKOENGINE_DLL" so all symbols in it will get
# default visibility. In combination with compile option "-fvisibility=hidden" net
# result is that all symbols in this object library are hidden
# ..............................................................................
add_library(sokoengine_obj_hidden OBJECT ${INSTALL_HEADERS} ${SELF_SOURCES})
target_include_directories(sokoengine_obj_hidden PUBLIC ${SELF_INCLUDE_DIRS})
target_link_libraries(sokoengine_obj_hidden PUBLIC
    cppitertools::cppitertools
    Boost::boost
    PNG::PNG
)
set_target_properties(sokoengine_obj_hidden PROPERTIES
    POSITION_INDEPENDENT_CODE ON
    EXCLUDE_FROM_DEFAULT_BUILD 1
    EXCLUDE_FROM_ALL 1
)

if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang" OR "${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
    target_link_options(sokoengine_obj_hidden PUBLIC "-Wl,--exclude-libs,ALL")
    target_compile_options(sokoengine_obj_hidden PUBLIC
        -fvisibility=hidden
        -fvisibility-inlines-hidden
    )
endif()

# ..............................................................................
# sokoengine OBJECT library with some sybmbols visible
#
# This object library defines "LIBSOKOENGINE_DLL" so symbols in it marked as
# "LIBSOKOENGINE_API" will remain visible even though it later defines
# "-fvisibility=hidden" compile option.
# ..............................................................................
add_library(sokoengine_obj OBJECT ${INSTALL_HEADERS} ${SELF_SOURCES})
target_include_directories(sokoengine_obj PUBLIC ${SELF_INCLUDE_DIRS})
target_link_libraries(sokoengine_obj PUBLIC
    cppitertools::cppitertools
    Boost::boost
    PNG::PNG
)
target_compile_definitions(sokoengine_obj PUBLIC
    LIBSOKOENGINE_DLL
    PRIVATE
    LIBSOKOENGINE_DLL_EXPORTS
)
set_target_properties(sokoengine_obj PROPERTIES
    POSITION_INDEPENDENT_CODE ON
)

if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang" OR "${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
    target_link_options(sokoengine_obj PUBLIC "-Wl,--exclude-libs,ALL")
    target_compile_options(sokoengine_obj
        PUBLIC
        -fvisibility=hidden
        -fvisibility-inlines-hidden
        PRIVATE
        $<$<CONFIG:Debug>: -Wall -Wextra -Wpedantic>
        -Wno-overloaded-virtual
        -Wno-unused-parameter
    )
endif()

# ..............................................................................
# sokoengine library
# ..............................................................................
add_library(sokoengine SHARED sokoengine.hpp)
target_link_libraries(sokoengine PRIVATE sokoengine_obj)
target_link_options(sokoengine PRIVATE "-Wl,--exclude-libs,ALL")
target_include_directories(sokoengine
    PUBLIC
    "$<BUILD_INTERFACE:${SELF_INCLUDE_DIRS}>"
    "$<INSTALL_INTERFACE:include/sokoengine>"
)
set_target_properties(sokoengine
    PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION ${PROJECT_VERSION_MAJOR}
    POSITION_INDEPENDENT_CODE ON
)

# generate_export_header(sokoengine)
set_property(TARGET sokoengine
    PROPERTY INTERFACE_sokoengine_MAJOR_VERSION ${PROJECT_VERSION_MAJOR})
set_property(TARGET sokoengine
    APPEND PROPERTY COMPATIBLE_INTERFACE_STRING sokoengine_MAJOR_VERSION)
add_symbols_export(sokoengine)

# ..............................................................................
# install
# 1. Install targets and export them unto common namespace:
# - INSTALL(TARGETS target1 EXPORT fooTargets ...)
# - INSTALL(TARGETS target2 EXPORT fooTargets ...)
# 2. Install additional files (ie. library headers):
# - INSTALL(FILES ...)
# 3. Install generated config for all exported targets:
# - INSTALL(EXPORT FooTargets ...)
# 4. Generate CMake package so that it can be found via find_package:
# - configure_package_config_file
# - write_basic_package_version_file
# 5. Install CMake package configs:
# - INSTALL(FILES ...)
# 6. Export targets for consuming from within build dir
# ..............................................................................

# Here, the EXPORT option tells CMake to create an export called libsokoengineTargets.
# Note, we have not asked CMake to install the export yet.
install(
    TARGETS sokoengine
    EXPORT libsokoengineTargets
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/sokoengine
)

# Install header files
install(
    FILES ${INSTALL_HEADERS}
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/sokoengine
)

# This command generates the libsokoengineTargets.cmake file and arranges to install it
# to lib/cmake. The file contains code suitable for use by downstreams to import all
# targets listed in the install command from the installation tree.
#
# Any number of target installations may be associated with the same export name. The
# install(EXPORT) command only needs to be called once to install a file that references
# all targets.
install(
    EXPORT libsokoengineTargets
    FILE libsokoengineTargets.cmake
    NAMESPACE libsokoengine::

    # was: DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/libsokoengine/cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/libsokoengine
)

configure_package_config_file(
    ${PROJECT_SOURCE_DIR}/cmake/libsokoengineConfig.cmake.in
    ${PROJECT_BINARY_DIR}/libsokoengineConfig.cmake

    # was INSTALL_DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/libsokoengine/cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/libsokoengine
)

write_basic_package_version_file(
    ${PROJECT_BINARY_DIR}/libsokoengineConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

install(
    FILES ${PROJECT_BINARY_DIR}/libsokoengineConfig.cmake
    ${PROJECT_BINARY_DIR}/libsokoengineConfigVersion.cmake

    # was DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/libsokoengine/cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/libsokoengine
)

# Exports libsokoengineTargets into current binary dir.
# This allows clients to consume libsokoengine from local build. Ie. if we build
# libosokengine in
#
# /tmp/builds/libsokoengine/debug
# /tmp/builds/libsokoengine/release
#
# then other package can consume it via:
#
# find_package(
# libsokoengine 0.5.0 REQUIRED
# CONFIG
# PATHS "/tmp/builds/libsokoengine/debug" "/tmp/builds/libsokoengine/release"
# )
export(
    EXPORT libsokoengineTargets
    FILE "${PROJECT_BINARY_DIR}/libsokoengineTargets.cmake"
    NAMESPACE libsokoengine::
)

# ..............................................................................
# Development utilities
# ..............................................................................

# ..................
# benchmarks utility
# ..................
file(WRITE
    "${CMAKE_BINARY_DIR}/benchmarks.cpp"
    "#include <sokoengine.hpp>\n\nint main() { return sokoengine::run_benchmarks(); }\n"
)
add_executable(benchmarks EXCLUDE_FROM_ALL "${CMAKE_BINARY_DIR}/benchmarks.cpp")
target_link_libraries(benchmarks PUBLIC sokoengine)

# add_callgrind_target(benchmarks)
# add_memcheck_target(benchmarks)
set_target_properties(benchmarks
    PROPERTIES
    EXCLUDE_FROM_DEFAULT_BUILD 1
    EXCLUDE_FROM_ALL 1
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
)

# ..................
# skindump utility
# ..................
add_executable(skindump skindump.cpp)
target_link_libraries(skindump PRIVATE sokoengine CLI11::CLI11)

# add_valgrind_profile_dump_target(playground)
set_target_properties(
    skindump
    PROPERTIES
    EXCLUDE_FROM_DEFAULT_BUILD 1
    EXCLUDE_FROM_ALL 1
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
)
