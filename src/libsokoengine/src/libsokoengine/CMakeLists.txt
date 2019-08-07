set(MY_HEADERS
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
    utilities/text_utils.hpp
)

set(MY_SOURCES
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
    utilities/text_utils.cpp
)

set(MY_INCLUDE_DIRS
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
if(${CMAKE_SYSTEM_NAME} MATCHES "Linux" AND CMAKE_BUILD_TYPE MATCHES Debug)
    add_library(sokoengine_obj
        OBJECT
            ${MY_HEADERS} ${MY_SOURCES} ${BACKWARD_ENABLE}
    )
    add_backward(sokoengine_obj)
else()
    add_library(sokoengine_obj
        OBJECT
            ${MY_HEADERS} ${MY_SOURCES}
    )
endif()

target_include_directories(sokoengine_obj
    PUBLIC
        "$<BUILD_INTERFACE:${MY_INCLUDE_DIRS}>"
        "$<INSTALL_INTERFACE:include/sokoengine>"
    PRIVATE
        $<TARGET_PROPERTY:CPPITERTOOLS::cppitertools,INTERFACE_INCLUDE_DIRECTORIES>
)

target_link_libraries(sokoengine_obj
    PRIVATE
        # We don't actually link agains any of objects in following libraries
        # Thus we hide this dependency once we are installed
        # As a consequence, consumers of libsokoengine don't need to link against boost
        # if they don't want to
        "$<BUILD_INTERFACE:Boost::boost>"
        "$<BUILD_INTERFACE:CPPITERTOOLS::cppitertools>"
)

target_compile_features(sokoengine_obj
    PUBLIC
        cxx_std_14
)

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
            -Wno-overloaded-virtual
            -Wno-sign-compare
            -Wno-unused-parameter
            -Wno-attributes
            $<$<CONFIG:Debug>: -Wall -Wextra -Wpedantic -Werror>
        >
        # $<$<CXX_COMPILER_ID:MSVC>: ...>
)

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

target_link_libraries(sokoengine PUBLIC sokoengine_obj)

set_target_properties(sokoengine
    PROPERTIES
        VERSION ${PROJECT_VERSION}
        SOVERSION ${PROJECT_VERSION_MAJOR}
        POSITION_INDEPENDENT_CODE ON
        INTERPROCEDURAL_OPTIMIZATION_RELEASE ON
        INTERPROCEDURAL_OPTIMIZATION_RELWITHDEBINFO ON
)

# include(CMakePrintHelpers)
# cmake_print_properties(
#     TARGETS sokoengine_obj
#     PROPERTIES INTERFACE_INCLUDE_DIRECTORIES
# )

if(${BUILD_SHARED_LIBS})
    # generate_export_header(sokoengine)
    set_property(TARGET sokoengine
        PROPERTY INTERFACE_sokoengine_MAJOR_VERSION 3)
    set_property(TARGET sokoengine
        APPEND PROPERTY COMPATIBLE_INTERFACE_STRING sokoengine_MAJOR_VERSION)
endif()

#..............................................................................
#                                   install
#..............................................................................


# Note that although object files are not installed, we need to export sokoengine_obj
# because sokoengine depends on it
#   https://gitlab.kitware.com/cmake/cmake/issues/18935
install(
    TARGETS
        sokoengine sokoengine_obj
    EXPORT
        ${PROJECT_NAME}_Targets
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    # Might be that following is not needed since we define it on target
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/sokoengine
)

write_basic_package_version_file(
    ${PROJECT_BINARY_DIR}/${PROJECT_NAME}ConfigVersion.cmake
    VERSION
        ${PROJECT_VERSION}
    COMPATIBILITY
        SameMajorVersion
)

configure_package_config_file(
    ${PROJECT_SOURCE_DIR}/cmake/${PROJECT_NAME}Config.cmake.in
    ${PROJECT_BINARY_DIR}/${PROJECT_NAME}Config.cmake
    INSTALL_DESTINATION
        ${CMAKE_INSTALL_DATAROOTDIR}/${PROJECT_NAME}/cmake
)

install(
    EXPORT
        ${PROJECT_NAME}_Targets
    FILE
        ${PROJECT_NAME}Targets.cmake
    NAMESPACE
        ${PROJECT_NAME}::
    DESTINATION
        ${CMAKE_INSTALL_DATAROOTDIR}/${PROJECT_NAME}/cmake
)

install(
    FILES
        ${PROJECT_BINARY_DIR}/${PROJECT_NAME}Config.cmake
        ${PROJECT_BINARY_DIR}/${PROJECT_NAME}ConfigVersion.cmake
    DESTINATION
        ${CMAKE_INSTALL_DATAROOTDIR}/${PROJECT_NAME}/cmake
)

install(
    FILES
        ${MY_HEADERS}
    DESTINATION
        ${CMAKE_INSTALL_INCLUDEDIR}/sokoengine
)
