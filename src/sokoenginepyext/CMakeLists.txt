#..............................................................................
#                             Python bindings module
#..............................................................................

if(ENABLE_PYTHON_EXTENSION)
    include(libsokoengine_pybind11)

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
        sokoenginepyext.hpp
    )

    target_link_libraries(sokoenginepyext PRIVATE sokoengine_obj)

    target_compile_features(sokoengine_obj PUBLIC cxx_std_17)

    set_target_properties(sokoenginepyext PROPERTIES
                                          EXCLUDE_FROM_ALL TRUE
                                          EXCLUDE_FROM_DEFAULT_BUILD TRUE)

endif(ENABLE_PYTHON_EXTENSION)

include(utilities_valgrind)

add_executable(benchmarks EXCLUDE_FROM_ALL benchmarks.cpp)
set_target_properties(benchmarks PROPERTIES EXCLUDE_FROM_DEFAULT_BUILD 1)
target_link_libraries(benchmarks PUBLIC sokoengine)
set_target_properties(benchmarks
    PROPERTIES
        INTERPROCEDURAL_OPTIMIZATION_RELEASE ON
        INTERPROCEDURAL_OPTIMIZATION_RELWITHDEBINFO ON
)
add_valgrind_profile_dump_target(benchmarks)
add_valgrind_memory_check_target(benchmarks)

add_executable(playground EXCLUDE_FROM_ALL playground.cpp)
set_target_properties(playground PROPERTIES EXCLUDE_FROM_DEFAULT_BUILD 1)
target_link_libraries(playground PUBLIC sokoengine)
add_valgrind_profile_dump_target(playground)
add_valgrind_memory_check_target(playground)
