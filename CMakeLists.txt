cmake_minimum_required(VERSION 3.15.1)

project(libsokoengine VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/modules/")

include(libsokoengine_configure)

add_subdirectory(src/libsokoengine)
add_subdirectory(src/sokoenginepyext)
