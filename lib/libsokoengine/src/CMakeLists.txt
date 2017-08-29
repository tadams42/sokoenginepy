#..............................................................................
#                          sokoengine sources configuration
#..............................................................................
set(SOKOENGINE_HEADERS ${SOKOENGINE_HEADERS}
                       ${CMAKE_CURRENT_SOURCE_DIR}/sokoengine.hpp
                       ${CMAKE_CURRENT_SOURCE_DIR}/sokoengine_config.hpp
)

set(SOKOENGINE_INCLUDE_DIRS ${SOKOENGINE_INCLUDE_DIRS}
                            ${sokoenginecpp_BINARY_DIR}
                            ${CMAKE_CURRENT_SOURCE_DIR}
)

add_subdirectory (board)
add_subdirectory (game)
add_subdirectory (snapshot)
add_subdirectory (tessellation)
add_subdirectory (utilities)

#..............................................................................
#                          sokoengine OBJECT library
#..............................................................................
add_library(sokoengine_obj OBJECT ${SOKOENGINE_SOURCES}
                                  ${SOKOENGINE_HEADERS}
                                  ${LIBBACKWARD_SOURCES})

target_compile_definitions(sokoengine_obj PRIVATE "LIBSOKOENGINE_DLL_EXPORTS")
target_include_directories(sokoengine_obj PUBLIC ${SOKOENGINE_INCLUDE_DIRS})

#..............................................................................
#                          sokoengine SHARED library
#..............................................................................
add_library(sokoengine SHARED $<TARGET_OBJECTS:sokoengine_obj>)

target_include_directories(sokoengine PUBLIC
  $<BUILD_INTERFACE:$<TARGET_PROPERTY:sokoengine_obj,INCLUDE_DIRECTORIES>>)

target_compile_options(sokoengine PUBLIC "-std=c++14")
target_compile_options(sokoengine PRIVATE "-fvisibility=hidden"
                                  PRIVATE "-fvisibility-inlines-hidden")
target_compile_definitions(sokoengine PRIVATE "LIBSOKOENGINE_DLL_EXPORTS")

set_target_properties(sokoengine PROPERTIES
                      VERSION ${SOKOENGINECPP_VERSION}
                      SOVERSION ${SOKOENGINECPP_SOVERSION} )

set_property(TARGET sokoengine PROPERTY INTERFACE_sokoengine_MAJOR_VERSION ${SOKOENGINECPP_VERSION_MAJOR})
set_property(TARGET sokoengine APPEND PROPERTY COMPATIBLE_INTERFACE_STRING ${SOKOENGINECPP_VERSION_MAJOR})

target_link_libraries(sokoengine ${LIBBACKWARD_DEPENDENCIES})

#..............................................................................
#                            install library target
#..............................................................................
install(TARGETS sokoengine
        EXPORT sokoengine_targets
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        INCLUDES DESTINATION ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_INCLUDEDIR}/sokoengine)

install(FILES ${SOKOENGINE_HEADERS}
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/sokoengine)

#..............................................................................
#                      install CMake Config-file Package
#..............................................................................
include(CMakePackageConfigHelpers)

write_basic_package_version_file(
  "${sokoenginecpp_BINARY_DIR}/sokoengine-config-version.cmake"
  VERSION ${SOKOENGINECPP_VERSION}
  COMPATIBILITY AnyNewerVersion)

configure_package_config_file(
  "${sokoenginecpp_SOURCE_DIR}/cmake/sokoengine-config.cmake.in"
  "${sokoenginecpp_BINARY_DIR}/sokoengine-config.cmake"
  INSTALL_DESTINATION ${CMAKE_INSTALL_CMAKEPACKAGEDIR}
  PATH_VARS CMAKE_INSTALL_CMAKEPACKAGEDIR)

install(EXPORT sokoengine_targets DESTINATION ${CMAKE_INSTALL_CMAKEPACKAGEDIR})
install(FILES "${sokoenginecpp_BINARY_DIR}/sokoengine-config-version.cmake"
              "${sokoenginecpp_BINARY_DIR}/sokoengine-config.cmake"
        DESTINATION ${CMAKE_INSTALL_CMAKEPACKAGEDIR})
