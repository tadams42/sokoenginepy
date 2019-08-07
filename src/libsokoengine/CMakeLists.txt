cmake_minimum_required (VERSION 3.15.1)

project(libsokoengine VERSION 0.5.3 LANGUAGES CXX)

set(default_build_type "Release")
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to '${default_build_type}' as none was specified.")
  set(CMAKE_BUILD_TYPE "${default_build_type}" CACHE
      STRING "Choose the type of build." FORCE)
  # Set the possible values of build type for cmake-gui
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS
    "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_CURRENT_SOURCE_DIR}/cmake/modules/")
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include(CheckIncludeFileCXX)
include(CheckTypeSize)
include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

include(FindBackwardlib)
include(FindCppitertools)
include(LibsokoengineValgrind)

# cmake --help-module FindBoost
set(Boost_USE_STATIC_LIBS        ON)
set(Boost_USE_MULTITHREADED      OFF)
set(Boost_USE_STATIC_RUNTIME     OFF)
# We are using C++14 bind and placeholders, this prevents name clashes
add_definitions(-DBOOST_BIND_NO_PLACEHOLDERS)
# Avoid name clashes with std, since we don't use Boost.Serialization
add_definitions(-DBOOST_MULTI_INDEX_DISABLE_SERIALIZATION)
find_package(Boost 1.65.0 REQUIRED)

add_subdirectory (src/libsokoengine)
add_subdirectory (src/sokoenginepyext)
add_subdirectory (src/utilities)
add_subdirectory (docs)
