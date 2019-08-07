# FindCppitertools.cmake
#
# git clones cppitertools library
#
# This will define the following imported targets
#
#     CPPITERTOOLS::cppitertools
#
# Author: Tomislav Adamic - tomislav.adamic@gmail.com

set(SOURCE_LIBS "${CMAKE_SOURCE_DIR}/lib")
file(MAKE_DIRECTORY "${SOURCE_LIBS}")


if(NOT EXISTS "${SOURCE_LIBS}/cppitertools/")
    execute_process(
        COMMAND git clone --branch v1.0 https://github.com/ryanhaining/cppitertools.git
        WORKING_DIRECTORY "${SOURCE_LIBS}"
    )
endif()

add_library(CPPITERTOOLS::cppitertools INTERFACE IMPORTED)

set_target_properties(CPPITERTOOLS::cppitertools
    PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${SOURCE_LIBS}"
)
