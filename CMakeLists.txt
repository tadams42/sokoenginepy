cmake_minimum_required(VERSION 3.22.0)

project(libsokoengine VERSION 1.0.2 LANGUAGES CXX)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/modules/")
include(libsokoengine_global_features)
include(libsokoengine_dependencies)
include(libsokoengine_custom_targets)

add_subdirectory(src/libsokoengine)
add_subdirectory(src/sokoenginepyext)

# include(CMakePrintHelpers)
# cmake_print_properties(
# TARGETS sokoengine
# PROPERTIES
# COMPILE_FEATURES COMPILE_FLAGS COMPILE_OPTIONS
# LINK_OPTIONS LINK_FLAGS INTERPROCEDURAL_OPTIMIZATION
# )
