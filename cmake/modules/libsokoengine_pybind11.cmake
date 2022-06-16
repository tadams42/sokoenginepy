#..............................................................................
# Clones pybind11 library into ~/.cache/cmake or does nothing if clone is
# already there.
# Configures pybind11 CMake module.

include(libsokoengine_local_cache_dir)

if(NOT EXISTS "${LOCAL_CACHE_DIR}/pybind11")
  execute_process(
    COMMAND git clone --branch v2.9 https://github.com/pybind/pybind11.git
    WORKING_DIRECTORY "${LOCAL_CACHE_DIR}"
  )
endif()

add_subdirectory("${LOCAL_CACHE_DIR}/pybind11/" "${CMAKE_BINARY_DIR}/pybind11/")
