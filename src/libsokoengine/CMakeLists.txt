set(SELF_HEADERS
    board/board_cell.hpp
    board/hexoban_board.hpp
    board/octoban_board.hpp
    board/sokoban_board.hpp
    board/trioban_board.hpp
    board/variant_board.hpp
    game/mover.hpp
    graph/board_graph.hpp
    manager/board_manager.hpp
    manager/board_state.hpp
    manager/hashed_board_manager.hpp
    manager/sokoban_plus.hpp
    snapshot/atomic_move.hpp
    sokoengine_config.hpp
    sokoengine.hpp
    tessellation/direction.hpp
    tessellation/hexoban_tessellation.hpp
    tessellation/octoban_tessellation.hpp
    tessellation/sokoban_tessellation.hpp
    tessellation/tessellation.hpp
    tessellation/trioban_tessellation.hpp
    utilities/benchmarks.hpp
    utilities/text_utils.hpp
)

set(SELF_SOURCES
    board/board_cell.cpp
    board/hexoban_board.cpp
    board/octoban_board.cpp
    board/sokoban_board.cpp
    board/trioban_board.cpp
    board/variant_board.cpp
    game/mover.cpp
    graph/board_graph.cpp
    manager/board_manager.cpp
    manager/board_state.cpp
    manager/hashed_board_manager.cpp
    manager/sokoban_plus.cpp
    snapshot/atomic_move.cpp
    tessellation/direction.cpp
    tessellation/hexoban_tessellation.cpp
    tessellation/octoban_tessellation.cpp
    tessellation/sokoban_tessellation.cpp
    tessellation/tessellation.cpp
    tessellation/trioban_tessellation.cpp
    utilities/benchmarks.cpp
    utilities/text_utils.cpp
)

set(SELF_INCLUDE_DIRS
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/board
    ${CMAKE_CURRENT_SOURCE_DIR}/game
    ${CMAKE_CURRENT_SOURCE_DIR}/graph
    ${CMAKE_CURRENT_SOURCE_DIR}/manager
    ${CMAKE_CURRENT_SOURCE_DIR}/snapshot
    ${CMAKE_CURRENT_SOURCE_DIR}/tessellation
    ${CMAKE_CURRENT_SOURCE_DIR}/utilities
)

#..............................................................................
#                       sokoengine OBJECT library
#..............................................................................
add_library(sokoengine_obj OBJECT ${SELF_HEADERS} ${SELF_SOURCES})

if(${CMAKE_SYSTEM_NAME} MATCHES "Linux" AND CMAKE_BUILD_TYPE MATCHES Debug)
    target_link_libraries(sokoengine_obj PRIVATE Backward::Backward)
endif()

target_include_directories(sokoengine_obj
    PUBLIC
        ${SELF_INCLUDE_DIRS}
    PRIVATE
        $<TARGET_PROPERTY:CPPITERTOOLS::cppitertools,INTERFACE_INCLUDE_DIRECTORIES>
)

target_link_libraries(sokoengine_obj
    PRIVATE
        # We don't actually link agains any of objects in following libraries Thus we
        # hide this dependency once we are installed. As a consequence, consumers of
        # libsokoengine don't need to link against boost - they don't even need to have
        # boost installed
        "$<BUILD_INTERFACE:Boost::boost>"
        "$<BUILD_INTERFACE:CPPITERTOOLS::cppitertools>"
)

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
#     TARGETS sokoengine_obj
#     PROPERTIES COMPILE_FEATURES COMPILE_FLAGS COMPILE_OPTIONS
# )

set_target_properties(sokoengine_obj
    PROPERTIES
        POSITION_INDEPENDENT_CODE ON
        INTERPROCEDURAL_OPTIMIZATION_RELEASE ON
        INTERPROCEDURAL_OPTIMIZATION_RELWITHDEBINFO ON
)

#..............................................................................
#                            sokoengine library
#..............................................................................
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

#..............................................................................
#                                   install
# 1. Install targets and export them unto common namespace:
#   - INSTALL(TARGETS target1 EXPORT fooTargets ...)
#   - INSTALL(TARGETS target2 EXPORT fooTargets ...)
# 2. Install additional files (ie. library headers):
#   - INSTALL(FILES ...)
# 3. Install generated config for all exported targets:
#   - INSTALL(EXPORT FooTargets ...)
# 4. Generate CMake package so that it can be found via find_package:
#   - configure_package_config_file
#   - write_basic_package_version_file
# 5. Install CMake package configs:
#   - INSTALL(FILES ...)
# 6. Export targets for consuming from within build dir
#..............................................................................

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
    FILES ${SELF_HEADERS}
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
#     /tmp/builds/libsokoengine/debug
#     /tmp/builds/libsokoengine/release
#
# then other package can consume it via:
#
#   find_package(
#       libsokoengine 0.5.0 REQUIRED
#       CONFIG
#       PATHS "/tmp/builds/libsokoengine/debug" "/tmp/builds/libsokoengine/release"
#   )
export(
    EXPORT libsokoengineTargets
    FILE "${PROJECT_BINARY_DIR}/libsokoengineTargets.cmake"
    NAMESPACE libsokoengine::
)
