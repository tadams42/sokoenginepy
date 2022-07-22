find_program(GIT_FOUND git)
find_program(GZIP_FOUND gzip)
find_program(NM_FOUND nm)
find_program(CUT_FOUND nm)
find_program(SORT_FOUND nm)
find_program(VALGRIND_FOUND valgrind)

find_package(Python3 COMPONENTS Interpreter Development)

if(Python3_FOUND)
    file(TO_CMAKE_PATH "${Python3_SITELIB}" NORMALIZED_SITELIB_DIR)

    if(PYBIND11_CMAKE_DIR)
        # Injected by pip when doing `pip install`
        file(TO_CMAKE_PATH "${PYBIND11_CMAKE_DIR}" NORMALIZED_PYBIND11_DIR)
    endif()

    find_package(
        pybind11
        CONFIG
        PATHS
        "${NORMALIZED_PYBIND11_DIR}"
        "${NORMALIZED_SITELIB_DIR}/pybind11/share/cmake/pybind11"
    )
endif()

# cmake --help-module FindBoost
set(Boost_USE_STATIC_LIBS ON)
set(Boost_USE_MULTITHREADED OFF)

# Avoid name clashes with std, since we don't use Boost.Serialization
add_definitions(-DBOOST_MULTI_INDEX_DISABLE_SERIALIZATION)
add_definitions(-DBOOST_BIMAP_DISABLE_SERIALIZATION)

find_package(Boost 1.71.0 REQUIRED)

find_package(cppitertools CONFIG REQUIRED)

find_package(PNG REQUIRED)

find_package(CLI11 CONFIG REQUIRED)
