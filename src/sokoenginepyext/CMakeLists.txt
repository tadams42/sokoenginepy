#..............................................................................
#                             Python bindings module
#..............................................................................

if(ENABLE_PYTHON_EXTENSION)
    include(libsokoengine_pybind11)

    pybind11_add_module(sokoenginepyext
        sokoenginepyext.cpp
        export_pusher_step.cpp
        export_board_cell.cpp
        export_board_graph.cpp
        export_tessellations.cpp
        export_board_manager.cpp
        export_mover.cpp
        export_sokoban_plus.cpp

        export_io_puzzle.cpp
        export_io_snapshot.cpp
        export_io_collection.cpp
        export_io_rle.cpp

        sokoenginepyext.hpp
    )

    target_link_libraries(sokoenginepyext PRIVATE sokoengine_obj)

    target_compile_features(sokoenginepyext PUBLIC cxx_std_17)

    set_target_properties(sokoenginepyext PROPERTIES
                                          EXCLUDE_FROM_ALL TRUE
                                          EXCLUDE_FROM_DEFAULT_BUILD TRUE)

endif(ENABLE_PYTHON_EXTENSION)

include(utilities_valgrind)

file(WRITE
     "${CMAKE_BINARY_DIR}/benchmarks.cpp"
     "#include <sokoengine.hpp>\n\nint main() { return sokoengine::run_benchmarks(); }\n"
)
add_executable(benchmarks EXCLUDE_FROM_ALL "${CMAKE_BINARY_DIR}/benchmarks.cpp")
target_link_libraries(benchmarks PUBLIC sokoengine)
target_compile_features(benchmarks PUBLIC cxx_std_17)
set_target_properties(benchmarks
    PROPERTIES
        EXCLUDE_FROM_DEFAULT_BUILD 1
        INTERPROCEDURAL_OPTIMIZATION_RELEASE ON
        INTERPROCEDURAL_OPTIMIZATION_RELWITHDEBINFO ON
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
)
add_valgrind_profile_dump_target(benchmarks)
add_valgrind_memory_check_target(benchmarks)

add_executable(playground EXCLUDE_FROM_ALL playground.cpp)
target_link_libraries(playground PUBLIC sokoengine)
target_compile_features(playground PUBLIC cxx_std_17)
set_target_properties(playground
    PROPERTIES
        EXCLUDE_FROM_DEFAULT_BUILD 1
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
)
add_valgrind_profile_dump_target(playground)
add_valgrind_memory_check_target(playground)
