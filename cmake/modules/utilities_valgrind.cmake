# LibsokoengineValgrind.cmake
#
# Two functions that allow us to add valgring builds for executables
#
# 1. Builds executable, runs it under callgrind which dumps profile data into file.
#    This file can later be analyzed via ie. KCacheGrind gui.
#
#     add_executable(mytarget mysource.cpp)
#     add_valgrind_profile_dump_target(mytarget)
#
# 2. Builds executable and runs it under memcheck
#
#     add_executable(mytarget mysource.cpp)
#     add_valgrind_memory_check_target(mytarget)
#
# Author: Tomislav Adamic - tomislav.adamic@gmail.com

function(add_valgrind_profile_dump_target for_target_name)
  if(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
    set(dump_file "${CMAKE_BINARY_DIR}/${for_target_name}_dump.pid")
    set(valgrind_args
      --dump-line=yes
      --dump-instr=yes
      --tool=callgrind
      --collect-jumps=yes
      --callgrind-out-file="${dump_file}"
    )
    set(valgrind_target_name "valgrind_profile_${for_target_name}")
    # get_target_property(binary_location ${for_target_name} LOCATION)
    # add_custom_target(${valgrind_target_name} COMMAND valgrind ${valgrind_args} ${binary_location})
    add_custom_target(
      ${valgrind_target_name}
      COMMAND valgrind ${valgrind_args} $<TARGET_FILE:${for_target_name}>
    )
    add_dependencies(${valgrind_target_name} ${for_target_name})
    set_target_properties(
      ${valgrind_target_name} PROPERTIES EXCLUDE_FROM_DEFAULT_BUILD 1
    )
  endif()
endfunction(add_valgrind_profile_dump_target)

function(add_valgrind_memory_check_target for_target_name)
  if(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
    set(valgrind_args
      --num-callers=50
      --leak-check=full
      --partial-loads-ok=yes
      --undef-value-errors=no
      --show-reachable=yes
      --error-limit=no
      # uncomment next two lines to generate suppression blocks in valgrind log
      # These blocks can then be added to .libsokoengine.supp
      # --gen-suppressions=all
      # --log-file="${CMAKE_BINARY_DIR}/valgrind_memcheck.log"
      # --suppressions="${CMAKE_SOURCE_DIR}/.libsokoengine.supp"
    )
    set(valgrind_target_name "valgrind_check_${for_target_name}")
    # get_target_property(binary_location ${for_target_name} LOCATION)
    # add_custom_target(${valgrind_target_name} COMMAND G_DEBUG=gc-friendly G_SLICE=always-malloc valgrind ${valgrind_args} ${binary_location})
    add_custom_target(
      ${valgrind_target_name}
      COMMAND G_DEBUG=gc-friendly G_SLICE=always-malloc valgrind ${valgrind_args} $<TARGET_FILE:${for_target_name}>
    )
    add_dependencies(${valgrind_target_name} ${for_target_name})
    set_target_properties(${valgrind_target_name}
                          PROPERTIES EXCLUDE_FROM_DEFAULT_BUILD 1)
  endif()
endfunction(add_valgrind_memory_check_target)
