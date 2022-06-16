# ..............................................................................
# Configures cmake itself, before configuring libsokoengine source code

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(default_build_type "Release")

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    message(STATUS "Setting build type to '${default_build_type}' as none was specified.")
    set(CMAKE_BUILD_TYPE "${default_build_type}" CACHE STRING "Choose the type of build." FORCE)
    set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

include(CheckIncludeFileCXX)
include(CheckTypeSize)
include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

find_program(GZIP_FOUND gzip REQUIRED)
find_program(GIT_FOUND git REQUIRED)

include(libsokoengine_cppitertools)

# cmake --help-module FindBoost
set(Boost_USE_STATIC_LIBS ON)
set(Boost_USE_MULTITHREADED OFF)

# We are using C++14 bind and placeholders, this prevents name clashes
add_definitions(-DBOOST_BIND_NO_PLACEHOLDERS)

# Avoid name clashes with std, since we don't use Boost.Serialization
add_definitions(-DBOOST_MULTI_INDEX_DISABLE_SERIALIZATION)

find_package(Boost 1.65.0 REQUIRED)

# .......................................................................................
# `make dist` target
# .......................................................................................
add_custom_target(
    dist
    COMMAND git archive -7 --format=tar.gz --prefix=libsokoengine-${PROJECT_VERSION}/ --output=${CMAKE_BINARY_DIR}/libsokoengine-${PROJECT_VERSION}.tar.gz HEAD
    BYPRODUCTS
    ${CMAKE_BINARY_DIR}/libsokoengine-${PROJECT_VERSION}.tar.gz
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMAND_EXPAND_LISTS
    COMMENT "Generating distribution tarball..."
)
