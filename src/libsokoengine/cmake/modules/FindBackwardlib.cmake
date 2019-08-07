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

set(SOURCE_LIBS "${CMAKE_SOURCE_DIR}/lib")
file(MAKE_DIRECTORY "${SOURCE_LIBS}")

if(NOT EXISTS "${SOURCE_LIBS}/backward-cpp/")
    execute_process(
        COMMAND git clone https://github.com/bombela/backward-cpp.git
        WORKING_DIRECTORY "${SOURCE_LIBS}"
    )
endif()

add_subdirectory("${SOURCE_LIBS}/backward-cpp")
