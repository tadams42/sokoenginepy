#..............................................................................
#                             Python bindings module
#..............................................................................

#..............................................................................
#                                pybind11 library
#..............................................................................
if(NOT EXISTS "${sokoenginecpp_SOURCE_DIR}/lib/pybind11/")
  execute_process(
    COMMAND git clone --branch v2.2.0 https://github.com/pybind/pybind11.git
    WORKING_DIRECTORY "${sokoenginecpp_SOURCE_DIR}/lib"
  )
endif()

add_subdirectory("${sokoenginecpp_SOURCE_DIR}/lib/pybind11/"
                 "${sokoenginecpp_BINARY_DIR}/lib/pybind11/")

pybind11_add_module(
  sokoenginepyext
  $<TARGET_OBJECTS:sokoengine_obj>
  sokoenginepyext.cpp
  export_direction.cpp
  export_atomic_move.cpp
  export_board_cell.cpp
  export_board_graph.cpp
  export_tessellations.cpp
  export_boards.cpp
  export_board_state.cpp
  export_mover.cpp
)

target_include_directories(
  sokoenginepyext PUBLIC
  $<BUILD_INTERFACE:$<TARGET_PROPERTY:sokoengine_obj,INCLUDE_DIRECTORIES>>
)

target_link_libraries(sokoenginepyext PRIVATE ${LIBBACKWARD_DEPENDENCIES})

set_target_properties(sokoenginepyext PROPERTIES
                                      EXCLUDE_FROM_ALL TRUE
                                      EXCLUDE_FROM_DEFAULT_BUILD TRUE)
