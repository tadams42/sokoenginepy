#..............................................................................
#                             Python bindings module
#..............................................................................

#..............................................................................
#                                pybind11 library
#..............................................................................
if(NOT EXISTS "${sokoenginecpp_SOURCE_DIR}/lib/pybind11/")
  execute_process(
    COMMAND git clone https://github.com/pybind/pybind11.git
    WORKING_DIRECTORY "${sokoenginecpp_SOURCE_DIR}/lib"
  )
endif()

add_subdirectory("${sokoenginecpp_SOURCE_DIR}/lib/pybind11/"
                 "${sokoenginecpp_BINARY_DIR}/lib/pybind11/")

pybind11_add_module(
  sokoenginepyext
  $<TARGET_OBJECTS:sokoengine_obj>
  sokoenginepyext.cpp
)

target_include_directories(
  sokoenginepyext PUBLIC
  $<BUILD_INTERFACE:$<TARGET_PROPERTY:sokoengine_obj,INCLUDE_DIRECTORIES>>
)

target_link_libraries(sokoenginepyext PRIVATE ${LIBBACKWARD_DEPENDENCIES})

set_target_properties(sokoenginepyext PROPERTIES
                                      EXCLUDE_FROM_ALL TRUE
                                      EXCLUDE_FROM_DEFAULT_BUILD TRUE)
