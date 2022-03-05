if(DEFINED ENV{XDG_CACHE_HOME})
  set(LOCAL_CACHE_DIR "$ENV{XDG_CACHE_HOME}/cmake/git")
elseif(DEFINED ENV{HOME})
  set(LOCAL_CACHE_DIR "$ENV{HOME}/.cache/cmake/git")
else()
  set(LOCAL_CACHE_DIR "${CMAKE_BINARY_DIR}/.cache")
endif()

file(MAKE_DIRECTORY "${LOCAL_CACHE_DIR}")
