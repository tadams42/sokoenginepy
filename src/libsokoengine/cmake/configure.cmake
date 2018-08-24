include(CheckIncludeFileCXX)
include(CheckTypeSize)

#..............................................................................
#         Check if we are on Linux to enable some development goodies
#..............................................................................
IF(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
  SET(LIBSOKONGINE_SYSTEM_IS_LINUX TRUE)
ENDIF()

set(CMAKE_INTERPROCEDURAL_OPTIMIZATION, TRUE)

#..............................................................................
#                  GCC compiler settings common to all targets.
#..............................................................................
if(CMAKE_COMPILER_IS_GNUCXX OR "${CMAKE_CXX_COMPILER}" MATCHES ".*clang")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14")
  set(DISABLED_CXX_WARNINGS "-Wno-overloaded-virtual -Wno-sign-compare -Wno-unused-parameter -Wno-attributes")
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -Wpedantic -Wall -Wextra ${DISABLED_CXX_WARNINGS}")
  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -flto")
  set(CMAKE_EXE_LINKER_FLAGS_RELEASE "${CMAKE_EXE_LINKER_FLAGS_RELEASE} -flto")
  set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
endif()

if("${CMAKE_CXX_COMPILER}" MATCHES ".*clang")
  set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -lstdc++")
  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -flto")
  set(CMAKE_EXE_LINKER_FLAGS_RELEASE "${CMAKE_EXE_LINKER_FLAGS_RELEASE} -flto")
  set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
endif()

#..............................................................................
#                  CMake settings common to all targets.
#..............................................................................
# Always produce position independent code (-fPIC on gcc)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
# Linker should ba able to find libsokoengine binaries when building utilities
link_directories("${LIBRARY_OUTPUT_PATH}")

include(GNUInstallDirs)
set(CMAKE_INSTALL_CMAKEPACKAGEDIR ${CMAKE_INSTALL_LIBDIR}/sokoengine/cmake CACHE PATH  "cmake Config-Package files installation destination")
mark_as_advanced(FORCE CMAKE_INSTALL_CMAKEPACKAGEDIR)

#..............................................................................
#                                 Boost library
#..............................................................................
# cmake --help-module FindBoost
# Next line is needed if we want to avoid dependence on boost shared libs
# Currently disabled because boost static libraries aren't compiled with
# position independent code on 64b Ubuntu
# set(Boost_USE_STATIC_LIBS        ON)
set(Boost_USE_MULTITHREADED      OFF)
set(Boost_USE_STATIC_RUNTIME     OFF)
# We are using C++14 bind and placeholders, this prevents name clashes
add_definitions(-DBOOST_BIND_NO_PLACEHOLDERS)
# Avoid name clashes with std, since we don't use Boost.Serialization
add_definitions(-DBOOST_MULTI_INDEX_DISABLE_SERIALIZATION)
find_package(Boost 1.55.0)
include_directories(${Boost_INCLUDE_DIRS})

#..............................................................................
#                            uninstall target
#..............................................................................
configure_file(
  "${CMAKE_SOURCE_DIR}/cmake/cmake_uninstall.cmake.in"
  "${CMAKE_BINARY_DIR}/cmake/cmake_uninstall.cmake"
  IMMEDIATE @ONLY)
add_custom_target(uninstall
  "${CMAKE_COMMAND}" -P "${CMAKE_BINARY_DIR}/cmake/cmake_uninstall.cmake")

#..............................................................................
#                   external build dependencies' directory
#..............................................................................
set(EXTERNAL_DEPENDENCIES_DIR "${CMAKE_BINARY_DIR}/dependencies")
file(MAKE_DIRECTORY "${EXTERNAL_DEPENDENCIES_DIR}")

#..............................................................................
#                           cppitertools library
#..............................................................................
if(NOT EXISTS "${EXTERNAL_DEPENDENCIES_DIR}/cppitertools/")
  execute_process(
    COMMAND git clone --branch v1.0 https://github.com/ryanhaining/cppitertools.git
    WORKING_DIRECTORY "${EXTERNAL_DEPENDENCIES_DIR}"
  )
endif()

include_directories("${EXTERNAL_DEPENDENCIES_DIR}")

#..............................................................................
#                              Backward library
#..............................................................................
# sudo apt-get install libdw-dev
# or
# sudo apt-get install binutils-dev
if(LIBSOKONGINE_SYSTEM_IS_LINUX AND CMAKE_BUILD_TYPE MATCHES Debug)
  if(NOT EXISTS "${EXTERNAL_DEPENDENCIES_DIR}/backward-cpp/")
    execute_process(
      COMMAND git clone https://github.com/bombela/backward-cpp.git
      WORKING_DIRECTORY "${EXTERNAL_DEPENDENCIES_DIR}"
    )
  endif()

  # Following two don't work for some reason...
  # list(APPEND CMAKE_MODULE_PATH
  #               "${EXTERNAL_DEPENDENCIES_DIR}/backward-cpp/")
  # find_package(Backward)

  CHECK_INCLUDE_FILE("elfutils/libdw.h" HAVE_DW_H)
  if(HAVE_DW_H)
    include_directories("${EXTERNAL_DEPENDENCIES_DIR}/backward-cpp")
    add_definitions(-DBACKWARD_HAS_DW=1)
    set(LIBBACKWARD_DEPENDENCIES dw)
    set(LIBBACKWARD_SOURCES
        "${EXTERNAL_DEPENDENCIES_DIR}/backward-cpp/backward.cpp")
  else()
    CHECK_INCLUDE_FILE("bfd.h" HAVE_BFD_H)
    if (HAVE_BFD_H)
      include_directories("${EXTERNAL_DEPENDENCIES_DIR}/backward-cpp")
      add_definitions(-DBACKWARD_HAS_BFD=1)
      set(LIBBACKWARD_DEPENDENCIES bfd)
      set(LIBBACKWARD_SOURCES
          "${EXTERNAL_DEPENDENCIES_DIR}/backward-cpp/backward.cpp")
    endif()
  endif()
endif()

#..............................................................................#
#                                   docs target                                 #
#..............................................................................#
find_package(Doxygen)
if(DOXYGEN_FOUND)
  set(SOKOENGINECPP_DOCS_BUILD_DIR "${CMAKE_BINARY_DIR}/docs")
  file(MAKE_DIRECTORY "${SOKOENGINECPP_DOCS_BUILD_DIR}")
  set(SOKOENGINECPP_DOCS_OUTPUT_ROOT
      "${SOKOENGINECPP_DOCS_BUILD_DIR}/libsokoengine-v${SOKOENGINECPP_VERSION}")
  set(DOXYFILE_TEMPLATE "${CMAKE_SOURCE_DIR}/docs/Doxyfile.in")
  configure_file("${DOXYFILE_TEMPLATE}" "${SOKOENGINECPP_DOCS_BUILD_DIR}/Doxyfile")
  add_custom_target(docs
                    COMMAND ${DOXYGEN_EXECUTABLE} Doxyfile
                    WORKING_DIRECTORY "${SOKOENGINECPP_DOCS_BUILD_DIR}"
                    SOURCES "${DOXYFILE_TEMPLATE}"
                    DEPENDS "${CMAKE_SOURCE_DIR}/VERSION")
  set_target_properties(docs PROPERTIES EXCLUDE_FROM_DEFAULT_BUILD 1)
  # add_dependencies(docs, sokoengine)
else()
  message("Doxygen not found, 'make docs' target will not be configured...")
endif()

#..............................................................................#
#                             valgrind targets
#..............................................................................#
function(add_valgrind_profile_dump_target for_target_name)
  if(LIBSOKONGINE_SYSTEM_IS_LINUX)
    set(dump_file "${CMAKE_BINARY_DIR}/${for_target_name}_dump.pid")
    set(valgrind_args
      --dump-line=yes
      --dump-instr=yes
      --tool=callgrind
      --collect-jumps=yes
      --callgrind-out-file="${dump_file}"
    )
    set(valgrind_target_name "valgrind_profile_${for_target_name}")
    # get_target_property(binary_location ${for_target_name} LOCATION)
    # add_custom_target(${valgrind_target_name} COMMAND valgrind ${valgrind_args} ${binary_location})
    add_custom_target(
      ${valgrind_target_name}
      COMMAND valgrind ${valgrind_args} $<TARGET_FILE:${for_target_name}>
    )
    add_dependencies(${valgrind_target_name} ${for_target_name})
    set_target_properties(
      ${valgrind_target_name} PROPERTIES EXCLUDE_FROM_DEFAULT_BUILD 1
    )
  endif()
endfunction(add_valgrind_profile_dump_target)

function(add_valgrind_memory_check_target for_target_name)
  if(LIBSOKONGINE_SYSTEM_IS_LINUX)
    set(valgrind_args
      --num-callers=50
      --leak-check=full
      --partial-loads-ok=yes
      --undef-value-errors=no
      --show-reachable=yes
      --error-limit=no
      # uncomment next two lines to generate suppression blocks in valgrind log
      # These blocks can then be added to .libsokoengine.supp
      # --gen-suppressions=all
      # --log-file="${CMAKE_BINARY_DIR}/valgrind_memcheck.log"
      # --suppressions="${CMAKE_SOURCE_DIR}/.libsokoengine.supp"
    )
    set(valgrind_target_name "valgrind_check_${for_target_name}")
    # get_target_property(binary_location ${for_target_name} LOCATION)
    # add_custom_target(${valgrind_target_name} COMMAND G_DEBUG=gc-friendly G_SLICE=always-malloc valgrind ${valgrind_args} ${binary_location})
    add_custom_target(
      ${valgrind_target_name}
      COMMAND G_DEBUG=gc-friendly G_SLICE=always-malloc valgrind ${valgrind_args} $<TARGET_FILE:${for_target_name}>
    )
    add_dependencies(${valgrind_target_name} ${for_target_name})
    set_target_properties(${valgrind_target_name}
                          PROPERTIES EXCLUDE_FROM_DEFAULT_BUILD 1)
  endif()
endfunction(add_valgrind_memory_check_target)
