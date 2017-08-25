#..............................................................................
#         Check if we are on Linux to enable some development goodies
#..............................................................................
IF(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
  SET(LIBSOKONGINE_SYSTEM_IS_LINUX TRUE)
ENDIF()

#..............................................................................
#                  GCC compiler settings common to all targets.
#..............................................................................
if(CMAKE_COMPILER_IS_GNUCXX OR "${CMAKE_CXX_COMPILER}" MATCHES ".*clang")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14")
  set(DISABLED_CXX_WARNINGS "-Wno-overloaded-virtual -Wno-sign-compare -Wno-unused-parameter -Wno-attributes")
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -Wpedantic -Wall -Wextra ${DISABLED_CXX_WARNINGS}")
endif()

if("${CMAKE_CXX_COMPILER}" MATCHES ".*clang")
  set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -lstdc++")
  set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
endif()

#..............................................................................
#                  CMake settings common to all targets.
#..............................................................................
set(CMAKE_POSITION_INDEPENDENT_CODE ON) # Always produce position independent code (-fPIC on gcc)
# set(EXECUTABLE_OUTPUT_PATH "${sokoenginecpp_BINARY_DIR}/bin")
# set(LIBRARY_OUTPUT_PATH "${sokoenginecpp_BINARY_DIR}/bin")
link_directories("${LIBRARY_OUTPUT_PATH}") # Linker should find libsokoengine binaries

include(GNUInstallDirs)
set(CMAKE_INSTALL_CMAKEPACKAGEDIR ${CMAKE_INSTALL_LIBDIR}/sokoengine/cmake CACHE PATH  "cmake Config-Package files installation destination")
mark_as_advanced(FORCE CMAKE_INSTALL_CMAKEPACKAGEDIR)

#..............................................................................
#                           Standard headers
#..............................................................................
include(CheckIncludeFileCXX)
CHECK_INCLUDE_FILE_CXX(iostream LIBSOKOENGINE_HAVE_STD_IOSTREAM)
CHECK_INCLUDE_FILE_CXX(iomanip LIBSOKOENGINE_HAVE_STD_IOMANIP)
CHECK_INCLUDE_FILE_CXX(fstream LIBSOKOENGINE_HAVE_STD_FSTREAM)
CHECK_INCLUDE_FILE_CXX(sstream LIBSOKOENGINE_HAVE_STD_SSTREAM)

CHECK_INCLUDE_FILE_CXX(string LIBSOKOENGINE_HAVE_STD_STRING)
CHECK_INCLUDE_FILE_CXX(cctype LIBSOKOENGINE_HAVE_STD_CCTYPE)

CHECK_INCLUDE_FILE_CXX(vector LIBSOKOENGINE_HAVE_STD_VECTOR)
CHECK_INCLUDE_FILE_CXX(deque LIBSOKOENGINE_HAVE_STD_DEQUE)
CHECK_INCLUDE_FILE_CXX(set LIBSOKOENGINE_HAVE_STD_SET)
CHECK_INCLUDE_FILE_CXX(map LIBSOKOENGINE_HAVE_STD_MAP)
CHECK_INCLUDE_FILE_CXX(unordered_map LIBSOKOENGINE_HAVE_STD_UNORDERED_MAP)
CHECK_INCLUDE_FILE_CXX(tuple LIBSOKOENGINE_HAVE_STD_TUPLE)
CHECK_INCLUDE_FILE_CXX(array LIBSOKOENGINE_HAVE_STD_ARRAY)
CHECK_INCLUDE_FILE_CXX(bitset LIBSOKOENGINE_HAVE_STD_BITSET)

CHECK_INCLUDE_FILE_CXX(algorithm LIBSOKOENGINE_HAVE_STD_ALGORITHM)
CHECK_INCLUDE_FILE_CXX(iterator LIBSOKOENGINE_HAVE_STD_ITERATOR)
CHECK_INCLUDE_FILE_CXX(functional LIBSOKOENGINE_HAVE_STD_FUNCTIONAL)

CHECK_INCLUDE_FILE_CXX(stdexcept LIBSOKOENGINE_HAVE_STD_STDEXCEPT)
CHECK_INCLUDE_FILE_CXX(typeinfo LIBSOKOENGINE_HAVE_STD_TYPEINFO)

CHECK_INCLUDE_FILE_CXX(memory LIBSOKOENGINE_HAVE_STD_MEMORY)
CHECK_INCLUDE_FILE_CXX(numeric LIBSOKOENGINE_HAVE_STD_NUMERIC)
CHECK_INCLUDE_FILE_CXX(random LIBSOKOENGINE_HAVE_STD_RANDOM)

CHECK_INCLUDE_FILE_CXX(ctime LIBSOKOENGINE_HAVE_STD_CTIME)
CHECK_INCLUDE_FILE_CXX(cstdint LIBSOKOENGINE_HAVE_STD_CSTDINT)

include(CheckTypeSize)
CHECK_TYPE_SIZE(size_t LIBSOKOENGINE_HAVE_SIZE_T)
CHECK_TYPE_SIZE(time_t LIBSOKOENGINE_HAVE_TIME_T)
CHECK_TYPE_SIZE(wchar_t LIBSOKOENGINE_HAVE_WCHAR_T)

#..............................................................................
#                                 Boost library
#..............................................................................
# cmake --help-module FindBoost
# Next line is needed if we want to avoid dependence on boost shared libs
# Currently disabled because boost static libraries aren't compiled with position independent code on 64b Ubuntu
# set(Boost_USE_STATIC_LIBS        ON)
set(Boost_USE_MULTITHREADED      OFF)
set(Boost_USE_STATIC_RUNTIME     OFF)
add_definitions(-DBOOST_BIND_NO_PLACEHOLDERS)              # We are using C++14 bind and placeholders, this prevents name clashes
add_definitions(-DBOOST_MULTI_INDEX_DISABLE_SERIALIZATION) # Avoid name clashes with std, since we don't use Boost.Serialization
find_package(Boost 1.55.0)
include_directories(${Boost_INCLUDE_DIRS})

#..............................................................................
#                            uninstall target
#..............................................................................
configure_file(
  "${sokoenginecpp_SOURCE_DIR}/cmake/cmake_uninstall.cmake.in"
  "${sokoenginecpp_BINARY_DIR}/cmake/cmake_uninstall.cmake"
  IMMEDIATE @ONLY)
add_custom_target(uninstall
  "${CMAKE_COMMAND}" -P "${sokoenginecpp_BINARY_DIR}/cmake/cmake_uninstall.cmake")

#..............................................................................
#                                cppitertools library
#..............................................................................
if(NOT EXISTS "${sokoenginecpp_SOURCE_DIR}/lib/cppitertools/")
  execute_process(
    COMMAND git clone https://github.com/ryanhaining/cppitertools.git
    WORKING_DIRECTORY "${sokoenginecpp_SOURCE_DIR}/lib"
  )
endif()

include_directories("${sokoenginecpp_SOURCE_DIR}/lib")

#..............................................................................
#                                Backward library
#..............................................................................
# sudo apt-get install libdw-dev
# or
# sudo apt-get install binutils-dev
if(LIBSOKONGINE_SYSTEM_IS_LINUX AND CMAKE_BUILD_TYPE MATCHES Debug)
  if(NOT EXISTS "${sokoenginecpp_SOURCE_DIR}/lib/backward-cpp/")
    execute_process(
      COMMAND git clone https://github.com/bombela/backward-cpp.git
      WORKING_DIRECTORY "${sokoenginecpp_SOURCE_DIR}/lib"
    )
  endif()

  # Following two don't work for some reason...
  # list(APPEND CMAKE_MODULE_PATH "${sokoenginecpp_SOURCE_DIR}/lib/backward-cpp/")
  # find_package(Backward)

  CHECK_INCLUDE_FILE("elfutils/libdw.h" HAVE_DW_H)
  if(HAVE_DW_H)
    include_directories("${sokoenginecpp_SOURCE_DIR}/lib/backward-cpp")
    add_definitions(-DBACKWARD_HAS_DW=1)
    set(LIBBACKWARD_DEPENDENCIES dw)
    set(LIBBACKWARD_SOURCES "${sokoenginecpp_SOURCE_DIR}/lib/backward-cpp/backward.cpp")
  else()
    CHECK_INCLUDE_FILE("bfd.h" HAVE_BFD_H)
    if (HAVE_BFD_H)
      include_directories("${sokoenginecpp_SOURCE_DIR}/lib/backward-cpp")
      add_definitions(-DBACKWARD_HAS_BFD=1)
      set(LIBBACKWARD_DEPENDENCIES bfd)
      set(LIBBACKWARD_SOURCES "${sokoenginecpp_SOURCE_DIR}/lib/backward-cpp/backward.cpp")
    endif()
  endif()
endif()

# #..............................................................................#
# #                                   doc target                                 #
# #..............................................................................#
# find_package(Doxygen)
# if(DOXYGEN_FOUND)
#   set(SOKOENGINECPP_DOCS_OUTPUT_ROOT "${sokoenginecpp_BINARY_DIR}/doc/libsokoengine-v${SOKOENGINECPP_VERSION}")
#   # set(SOKOENGINECPP_DOCS_OUTPUT_ROOT "${sokoenginecpp_SOURCE_DIR}/doc")
#   set(DOXYFILE_TEMPLATE "${sokoenginecpp_SOURCE_DIR}/doc/Doxyfile.in")
#   configure_file("${DOXYFILE_TEMPLATE}" "${sokoenginecpp_BINARY_DIR}/doc/Doxyfile")
#   add_custom_target(doc
#     COMMAND ${DOXYGEN_EXECUTABLE} Doxyfile
#     WORKING_DIRECTORY "${sokoenginecpp_BINARY_DIR}/doc"
#     SOURCES "${DOXYFILE_TEMPLATE}"
#     DEPENDS "${sokoenginecpp_SOURCE_DIR}/VERSION" )
#   set_target_properties(doc PROPERTIES EXCLUDE_FROM_DEFAULT_BUILD 1)
# else()
#   message("Doxygen not found, 'make doc' target will not be configured...")
# endif()
#
# #..............................................................................#
# #                             valgrind targets
# #..............................................................................#
# function(add_valgrind_profile_dump_target for_target_name)
#   if(LIBSOKONGINE_SYSTEM_IS_LINUX)
#     set(dump_file "${sokoenginecpp_BINARY_DIR}/${for_target_name}_dump.pid")
#     set(valgrind_args --dump-line=yes
#                       --dump-instr=yes
#                       --tool=callgrind
#                       --collect-jumps=yes
#                       --callgrind-out-file="${dump_file}" )
#     set(valgrind_target_name "valgrind_profile_${for_target_name}")
#     # get_target_property(binary_location ${for_target_name} LOCATION)
#     # add_custom_target(${valgrind_target_name} COMMAND valgrind ${valgrind_args} ${binary_location})
#     add_custom_target(${valgrind_target_name} COMMAND valgrind ${valgrind_args} $<TARGET_FILE:${for_target_name}>)
#     add_dependencies(${valgrind_target_name} ${for_target_name})
#     set_target_properties(${valgrind_target_name} PROPERTIES EXCLUDE_FROM_DEFAULT_BUILD 1)
#   endif()
# endfunction(add_valgrind_profile_dump_target)
#
# function(add_valgrind_memory_check_target for_target_name)
#   if(LIBSOKONGINE_SYSTEM_IS_LINUX)
#     set(valgrind_args --num-callers=50
#                       --leak-check=full
#                       --partial-loads-ok=yes
#                       --undef-value-errors=no
#                       --show-reachable=yes
#                       --error-limit=no
#                       # uncomment next two lines to generate suppression blocks in valgrind log
#                       # These blocks can then be added to .libsokoengine.supp
#                       # --gen-suppressions=all
#                       # --log-file="${sokoenginecpp_BINARY_DIR}/valgrind_memcheck.log"
#                       --suppressions="${sokoenginecpp_SOURCE_DIR}/.libsokoengine.supp" )
#     set(valgrind_target_name "valgrind_check_${for_target_name}")
#     # get_target_property(binary_location ${for_target_name} LOCATION)
#     # add_custom_target(${valgrind_target_name} COMMAND G_DEBUG=gc-friendly G_SLICE=always-malloc valgrind ${valgrind_args} ${binary_location})
#     add_custom_target(${valgrind_target_name} COMMAND G_DEBUG=gc-friendly G_SLICE=always-malloc valgrind ${valgrind_args} $<TARGET_FILE:${for_target_name}>)
#     add_dependencies(${valgrind_target_name} ${for_target_name})
#     set_target_properties(${valgrind_target_name} PROPERTIES EXCLUDE_FROM_DEFAULT_BUILD 1)
#   endif()
# endfunction(add_valgrind_memory_check_target)
#
# #..............................................................................#
# #                             'make dist' target
# #..............................................................................#
# set(dist_archive "libsokoengine-${SOKOENGINECPP_VERSION}.tar.gz")
# add_custom_target(dist
#   COMMAND
#     git archive HEAD --format=tar.gz --output="${sokoenginecpp_BINARY_DIR}/${dist_archive}" --prefix="libsokoengine-${SOKOENGINECPP_VERSION}/"
#   WORKING_DIRECTORY "${sokoenginecpp_SOURCE_DIR}")
#
# #..............................................................................#
# #                           gcov coverage option
# #..............................................................................#
# if(CMAKE_COMPILER_IS_GNUCXX AND CMAKE_BUILD_TYPE MATCHES Debug)
#   option(WITH_COVERAGE "Build for code coverage report (only for gcc, requires gcov, lcov and genhtml)" OFF)
#
#   if(WITH_COVERAGE)
#     find_program(GCOV_PATH gcov)
#     mark_as_advanced(GCOV_PATH)
#     find_program(LCOV_PATH lcov)
#     mark_as_advanced(LCOV_PATH)
#     find_program(GENHTML_PATH genhtml)
#     mark_as_advanced(GENHTML_PATH)
#
#     if(NOT GCOV_PATH)
#         messagE(FATAL_ERROR "gcov not found! Aborting...")
#     endif()
#
#     if(NOT LCOV_PATH)
#         message(FATAL_ERROR "lcov not found! Aborting...")
#     endif()
#
#     if(NOT GENHTML_PATH)
#         message(FATAL_ERROR "genhtml not found! Aborting...")
#     endif()
#
#     set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --coverage")
#   endif()
# endif()
#
# function(SETUP_TARGET_FOR_COVERAGE for_target)
#   if(WITH_COVERAGE AND CMAKE_COMPILER_IS_GNUCXX AND CMAKE_BUILD_TYPE MATCHES Debug)
#     set(_outputname "coverage_${for_target}_output")
#     set(_targetname "coverage_${for_target}")
#
#     add_custom_target(${_targetname}
#       # Reset all execution counts to zero.
#       COMMAND ${LCOV_PATH} --directory . --zerocounters
#
#       # Run tests.
#       COMMAND ${for_target} ${ARGV3}
#
#       # Capture coverage data.
#       COMMAND ${LCOV_PATH} --compat-libtool --directory . --capture --output-file ${_outputname}.info
#       COMMAND ${LCOV_PATH} --remove ${_outputname}.info 'spec/*' '/usr/*' 'lib/*' '${sokoenginecpp_BINARY_DIR}/*' 'tmp/*' --output-file coverage.info
#
#       # Generating the report.
#       COMMAND ${GENHTML_PATH} -o ${_outputname} coverage.info
#
#       # COMMAND ${CMAKE_COMMAND} -E remove ${_outputname}.info ${_outputname}.info.cleaned
#       WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
#       COMMENT "Resetting code coverage counters to zero.\nProcessing code coverage counters and generating report."
#     )
#
#     # Show info where to find the report
#     ADD_CUSTOM_COMMAND(TARGET ${_targetname} POST_BUILD
#       COMMAND ;
#       COMMENT "Open ./${_outputname}/index.html in your browser to view the coverage report."
#     )
#   endif()
# endfunction()
