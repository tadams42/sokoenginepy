find_program(GIT_FOUND git REQUIRED)
find_program(GZIP_FOUND gzip REQUIRED)

# cmake --help-module FindBoost
set(Boost_USE_STATIC_LIBS ON)
set(Boost_USE_MULTITHREADED OFF)

# Avoid name clashes with std, since we don't use Boost.Serialization
add_definitions(-DBOOST_MULTI_INDEX_DISABLE_SERIALIZATION)
add_definitions(-DBOOST_BIMAP_DISABLE_SERIALIZATION)

# find_package(Boost 1.65.0 CONFIG REQUIRED)
find_package(Boost 1.71.0 REQUIRED)
find_package(cppitertools CONFIG REQUIRED)
