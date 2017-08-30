add_executable(benchmarks EXCLUDE_FROM_ALL benchmarks.cpp)

set_target_properties(benchmarks PROPERTIES
	                               EXCLUDE_FROM_DEFAULT_BUILD 1)

target_link_libraries(benchmarks sokoengine)

add_valgrind_profile_dump_target(benchmarks)
add_valgrind_memory_check_target(benchmarks)
