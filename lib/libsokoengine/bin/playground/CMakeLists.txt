add_executable(playground EXCLUDE_FROM_ALL main.cpp)

set_target_properties(playground PROPERTIES
	                               EXCLUDE_FROM_DEFAULT_BUILD 1)

target_link_libraries(playground sokoengine)

add_valgrind_profile_dump_target(playground)
add_valgrind_memory_check_target(playground)
