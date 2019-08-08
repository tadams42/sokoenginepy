#..............................................................................
#                             Python bindings module
#..............................................................................

#..............................................................................
#                                pybind11 library
#..............................................................................
set(SOURCE_LIBS "${CMAKE_SOURCE_DIR}/lib")
file(MAKE_DIRECTORY "${SOURCE_LIBS}")

if(NOT EXISTS "${SOURCE_LIBS}/pybind11")
  execute_process(
    COMMAND git clone --branch v2.3 https://github.com/pybind/pybind11.git
    WORKING_DIRECTORY "${SOURCE_LIBS}"
  )
endif()

add_subdirectory("${SOURCE_LIBS}/pybind11/" "${CMAKE_BINARY_DIR}/pybind11/")

pybind11_add_module(sokoenginepyext
  sokoenginepyext.cpp
  export_direction.cpp
  export_atomic_move.cpp
  export_board_cell.cpp
  export_board_graph.cpp
  export_tessellations.cpp
  export_boards.cpp
  export_board_manager.cpp
  export_mover.cpp
)

target_link_libraries(sokoenginepyext PRIVATE sokoengine_obj)

set_target_properties(sokoenginepyext PROPERTIES
                                      EXCLUDE_FROM_ALL TRUE
                                      EXCLUDE_FROM_DEFAULT_BUILD TRUE)
