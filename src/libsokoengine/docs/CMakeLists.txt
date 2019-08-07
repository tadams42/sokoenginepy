#..............................................................................#
#                                   docs target                                 #
#..............................................................................#
find_package(Doxygen)
if(DOXYGEN_FOUND)
  set(SOKOENGINE_DOCS_BUILD_DIR "${CMAKE_BINARY_DIR}/docs")
  file(MAKE_DIRECTORY "${SOKOENGINE_DOCS_BUILD_DIR}")
  set(SOKOENGINE_DOCS_OUTPUT_ROOT
      "${SOKOENGINE_DOCS_BUILD_DIR}/libsokoengine-v${libsokoengine_VERSION}")
  set(DOXYFILE_TEMPLATE "${CMAKE_CURRENT_SOURCE_DIR}/Doxyfile.in")
  configure_file("${DOXYFILE_TEMPLATE}" "${SOKOENGINE_DOCS_BUILD_DIR}/Doxyfile")
  add_custom_target(docs
                    COMMAND ${DOXYGEN_EXECUTABLE} Doxyfile
                    WORKING_DIRECTORY "${SOKOENGINE_DOCS_BUILD_DIR}"
                    SOURCES "${DOXYFILE_TEMPLATE}"
                    DEPENDS "${CMAKE_SOURCE_DIR}/src/libsokoengine/sokoengine.hpp")
  set_target_properties(docs PROPERTIES EXCLUDE_FROM_DEFAULT_BUILD 1)
else()
  message("Doxygen not found, 'make docs' target will not be configured...")
endif()
