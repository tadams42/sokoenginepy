set(PRIVATE_HEADERS
    io/collection/sok_file_format.hpp
    io/collection/SOK_format_specification.h

    io/rle/ast.hpp
    io/rle/ast_adapted.hpp
    io/rle/rle_config.hpp
    io/rle/error_handler.hpp
    io/rle/evaluator.hpp
    io/rle/grammar.hpp
    io/rle/json_printer.hpp

    io/snapshot/ast.hpp
    io/snapshot/ast_adapted.hpp
    io/snapshot/snapshot_config.hpp
    io/snapshot/error_handler.hpp
    io/snapshot/evaluator.hpp
    io/snapshot/grammar.hpp
    io/snapshot/json_printer.hpp
    io/snapshot/parser.hpp
)

set(INSTALL_HEADERS
    config.hpp
    sokoengine.hpp
    benchmarks.hpp

    game/board_cell.hpp
    game/board_graph.hpp
    game/board_state.hpp
    game/board_manager.hpp
    game/hashed_board_manager.hpp
    game/mover.hpp
    game/pusher_step.hpp
    game/sokoban_plus.hpp
    game/tessellation.hpp
    game/hexoban_tessellation.hpp
    game/octoban_tessellation.hpp
    game/sokoban_tessellation.hpp
    game/trioban_tessellation.hpp

    io/collection.hpp
    io/hexoban.hpp
    io/octoban.hpp
    io/puzzle.hpp
    io/rle.hpp
    io/snapshot.hpp
    io/sokoban.hpp
    io/trioban.hpp
)

set(SELF_SOURCES
    benchmarks.cpp

    game/board_cell.cpp
    game/board_graph.cpp
    game/board_manager.cpp
    game/board_state.cpp
    game/hashed_board_manager.cpp
    game/mover.cpp
    game/pusher_step.cpp
    game/sokoban_plus.cpp
    game/tessellation.cpp
    game/hexoban_tessellation.cpp
    game/octoban_tessellation.cpp
    game/sokoban_tessellation.cpp
    game/trioban_tessellation.cpp

    io/collection/collection.cpp
    io/collection/sok_file_format.cpp

    io/rle/rle.cpp

    io/snapshot/ast.cpp
    io/snapshot/parser.cpp
    io/snapshot/snapshot.cpp

    io/hexoban.cpp
    io/octoban.cpp
    io/puzzle.cpp
    io/sokoban.cpp
    io/trioban.cpp
)

set(SELF_INCLUDE_DIRS
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/game
    ${CMAKE_CURRENT_SOURCE_DIR}/io
)

# ..............................................................................
# sokoengine OBJECT library
# ..............................................................................
add_library(sokoengine_obj OBJECT ${INSTALL_HEADERS} ${PRIVATE_HEADERS} ${SELF_SOURCES})

target_include_directories(sokoengine_obj
    PUBLIC
    ${SELF_INCLUDE_DIRS}
    PRIVATE
    $<TARGET_PROPERTY:CPPITERTOOLS::cppitertools,INTERFACE_INCLUDE_DIRECTORIES>
)

# We link (where necessary) thse dependencies statically, there is no need to expose
# them to targes consuming sokoengine_obj.
# As a consequence, consumers of libsokoengine don't need to link against boost.
# They don't even need to have boost installed, since no libsokoengine public
# headers include anything from Boost.
# target_link_libraries(sokoengine_obj
# PRIVATE
# "$<BUILD_INTERFACE:Boost::boost>"
# "$<BUILD_INTERFACE:CPPITERTOOLS::cppitertools>"
# )
target_compile_features(sokoengine_obj PUBLIC cxx_std_17)

if(${BUILD_SHARED_LIBS})
    target_compile_definitions(sokoengine_obj
        PUBLIC
        LIBSOKOENGINE_DLL
        PRIVATE
        LIBSOKOENGINE_DLL_EXPORTS
    )
    target_compile_options(sokoengine_obj
        PUBLIC
        $<$<OR:$<CXX_COMPILER_ID:GNU>,$<CXX_COMPILER_ID:Clang>>:
        -fvisibility=hidden
        -fvisibility-inlines-hidden
        >

        # $<$<CXX_COMPILER_ID:MSVC>: ...>
    )
endif()

target_compile_options(sokoengine_obj
    PRIVATE
    $<$<OR:$<CXX_COMPILER_ID:GNU>,$<CXX_COMPILER_ID:Clang>>:
    $<$<CONFIG:Debug>: -Wall -Wextra -Wpedantic>
    -Wno-overloaded-virtual
    -Wno-unused-parameter

    # -Wno-attributes
    >

    # $<$<CXX_COMPILER_ID:MSVC>: ...>
)

# include(CMakePrintHelpers)
# cmake_print_properties(
# TARGETS sokoengine_obj
# PROPERTIES COMPILE_FEATURES COMPILE_FLAGS COMPILE_OPTIONS
# )
set_target_properties(sokoengine_obj
    PROPERTIES
    POSITION_INDEPENDENT_CODE ON
    INTERPROCEDURAL_OPTIMIZATION_RELEASE ON
    INTERPROCEDURAL_OPTIMIZATION_RELWITHDEBINFO ON
)

# ..............................................................................
# sokoengine library
# ..............................................................................
add_library(sokoengine sokoengine.hpp)

target_link_libraries(sokoengine PRIVATE sokoengine_obj)

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
    INTERPROCEDURAL_OPTIMIZATION_RELEASE ON
    INTERPROCEDURAL_OPTIMIZATION_RELWITHDEBINFO ON
)

if(${BUILD_SHARED_LIBS})
    # generate_export_header(sokoengine)
    set_property(TARGET sokoengine
        PROPERTY INTERFACE_sokoengine_MAJOR_VERSION 3)
    set_property(TARGET sokoengine
        APPEND PROPERTY COMPATIBLE_INTERFACE_STRING sokoengine_MAJOR_VERSION)
endif()

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
