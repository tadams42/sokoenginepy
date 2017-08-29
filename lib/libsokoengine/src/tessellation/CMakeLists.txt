set(SOKOENGINE_SOURCES ${SOKOENGINE_SOURCES}
  ${CMAKE_CURRENT_SOURCE_DIR}/direction.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/tessellation.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/hexoban_tessellation.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/octoban_tessellation.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/sokoban_tessellation.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/trioban_tessellation.cpp
PARENT_SCOPE)

set(SOKOENGINE_HEADERS ${SOKOENGINE_HEADERS}
  ${CMAKE_CURRENT_SOURCE_DIR}/direction.hpp
  ${CMAKE_CURRENT_SOURCE_DIR}/tessellation.hpp
  ${CMAKE_CURRENT_SOURCE_DIR}/hexoban_tessellation.hpp
  ${CMAKE_CURRENT_SOURCE_DIR}/octoban_tessellation.hpp
  ${CMAKE_CURRENT_SOURCE_DIR}/sokoban_tessellation.hpp
  ${CMAKE_CURRENT_SOURCE_DIR}/trioban_tessellation.hpp
PARENT_SCOPE)

set(SOKOENGINE_INCLUDE_DIRS ${SOKOENGINE_INCLUDE_DIRS}
  ${CMAKE_CURRENT_SOURCE_DIR}
PARENT_SCOPE)
