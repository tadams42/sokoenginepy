set(SOKOENGINE_SOURCES ${SOKOENGINE_SOURCES}
  ${CMAKE_CURRENT_SOURCE_DIR}/board_cell.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/board_graph.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/variant_board.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/sokoban_board.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/octoban_board.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/trioban_board.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/hexoban_board.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/board_state.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/sokoban_plus.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/hashed_board_state.cpp
PARENT_SCOPE)

set(SOKOENGINE_HEADERS ${SOKOENGINE_HEADERS}
  ${CMAKE_CURRENT_SOURCE_DIR}/board_cell.hpp
  ${CMAKE_CURRENT_SOURCE_DIR}/board_graph.hpp
  ${CMAKE_CURRENT_SOURCE_DIR}/variant_board.hpp
  ${CMAKE_CURRENT_SOURCE_DIR}/sokoban_board.hpp
  ${CMAKE_CURRENT_SOURCE_DIR}/octoban_board.hpp
  ${CMAKE_CURRENT_SOURCE_DIR}/trioban_board.hpp
  ${CMAKE_CURRENT_SOURCE_DIR}/hexoban_board.hpp
  ${CMAKE_CURRENT_SOURCE_DIR}/board_state.hpp
  ${CMAKE_CURRENT_SOURCE_DIR}/sokoban_plus.hpp
  ${CMAKE_CURRENT_SOURCE_DIR}/hashed_board_state.hpp
PARENT_SCOPE)

set(SOKOENGINE_INCLUDE_DIRS ${SOKOENGINE_INCLUDE_DIRS}
  ${CMAKE_CURRENT_SOURCE_DIR}
PARENT_SCOPE)
