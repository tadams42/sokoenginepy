# FindBackwardlib.cmake
#
# git clones backward library
#
# and configures it to be uses out of source like this:
#
#     add_executable(mytarget mysource.cpp ${BACKWARD_ENABLE})
#     add_backward(mytarget)
#
# You'll also need:
#
#     sudo apt-get install libdw-dev
#
# or
#
#     sudo apt-get install binutils-dev
#
#
# Author: Tomislav Adamic - tomislav.adamic@gmail.com

include(libsokoengine_local_cache_dir)

if(NOT EXISTS "${LOCAL_CACHE_DIR}/backward-cpp/")
    execute_process(
        COMMAND git clone https://github.com/bombela/backward-cpp.git
        WORKING_DIRECTORY "${LOCAL_CACHE_DIR}"
    )
endif()

list(APPEND CMAKE_PREFIX_PATH "${LOCAL_CACHE_DIR}/backward-cpp/")
find_package(Backward)
