include(libsokoengine_local_cache_dir)

if(NOT EXISTS "${LOCAL_CACHE_DIR}/cppitertools/")
    execute_process(
        COMMAND git clone --branch v1.0 https://github.com/ryanhaining/cppitertools.git
        WORKING_DIRECTORY "${LOCAL_CACHE_DIR}"
    )
endif()

add_library(CPPITERTOOLS::cppitertools INTERFACE IMPORTED)

set_target_properties(CPPITERTOOLS::cppitertools
    PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${LOCAL_CACHE_DIR}"
)
