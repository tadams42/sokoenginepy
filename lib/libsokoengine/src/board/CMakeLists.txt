set(SOKOENGINE_SOURCES ${SOKOENGINE_SOURCES}
  board/board_cell.cpp
  board/board_graph.cpp
  board/text_utils.cpp
  board/variant_board.cpp
  board/sokoban_board.cpp
  board/octoban_board.cpp
  board/trioban_board.cpp
  board/hexoban_board.cpp
  board/board_state.cpp
  board/sokoban_plus.cpp
  board/hashed_board_state.cpp
PARENT_SCOPE)

set(SOKOENGINE_PUBLIC_HEADERS ${SOKOENGINE_PUBLIC_HEADERS}
  board/board_cell.hpp
  board/board_graph.hpp
  board/text_utils.hpp
  board/variant_board.hpp
  board/sokoban_board.hpp
  board/octoban_board.hpp
  board/trioban_board.hpp
  board/hexoban_board.hpp
  board/board_state.hpp
  board/sokoban_plus.hpp
  board/hashed_board_state.hpp
PARENT_SCOPE)
