set(SOKOENGINE_SOURCES ${SOKOENGINE_SOURCES}
  tessellation/direction.cpp
  tessellation/tessellation.cpp
  tessellation/tessellation_base.cpp
  tessellation/hexoban_tessellation.cpp
  tessellation/octoban_tessellation.cpp
  tessellation/sokoban_tessellation.cpp
  tessellation/trioban_tessellation.cpp
PARENT_SCOPE)

set(SOKOENGINE_PUBLIC_HEADERS ${SOKOENGINE_PUBLIC_HEADERS}
  tessellation/direction.hpp
  tessellation/tessellation.hpp
  tessellation/tessellation_base.hpp
  tessellation/hexoban_tessellation.hpp
  tessellation/octoban_tessellation.hpp
  tessellation/sokoban_tessellation.hpp
  tessellation/trioban_tessellation.hpp
PARENT_SCOPE)
