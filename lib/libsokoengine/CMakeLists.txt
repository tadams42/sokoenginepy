cmake_minimum_required (VERSION 2.8.12)

project(sokoenginecpp)

# Parse version information from file VERSION
file(STRINGS "VERSION" VERSIONS_READ LIMIT_COUNT 1)
list( GET VERSIONS_READ 0 SOKOENGINECPP_VERSION )   # Package version
# Parse package version components
string(REPLACE "." ";" VERSION_PARSED ${SOKOENGINECPP_VERSION})
list( GET VERSION_PARSED 0 SOKOENGINECPP_SOVERSION ) # SONAME version
list( GET VERSION_PARSED 0 SOKOENGINECPP_VERSION_MAJOR )
list( GET VERSION_PARSED 1 SOKOENGINECPP_VERSION_MINOR )
list( GET VERSION_PARSED 2 SOKOENGINECPP_VERSION_PATCH )

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release CACHE STRING
      "Choose the type of build, options are: Debug Release RelWithDebInfo MinSizeRel."
      FORCE)
endif()

include("${sokoenginecpp_SOURCE_DIR}/cmake/configure.cmake")

add_subdirectory (src)
add_subdirectory (bin)
add_subdirectory (ext)
