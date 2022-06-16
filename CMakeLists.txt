cmake_minimum_required(VERSION 3.15.1)

project(libsokoengine VERSION 0.6.0 LANGUAGES CXX)

# set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -D_GLIBCXX_DEBUG")
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/modules/")

include(libsokoengine_configure)

add_subdirectory(src/libsokoengine)
add_subdirectory(src/sokoenginepyext)
