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
