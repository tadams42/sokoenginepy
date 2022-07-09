# ..............................................................................
# Python native extension - sokoenginepyext
# ..............................................................................

find_package(Python3 COMPONENTS Interpreter Development)

if(Python3_FOUND)
    find_package(
        pybind11
        CONFIG
        PATHS
        "${PYBIND11_CMAKE_DIR}" # Injected by pip when doing `pip install`
        "${Python3_SITELIB}/pybind11/share/cmake/pybind11"
    )

    if(pybind11_FOUND)
        pybind11_add_module(sokoenginepyext
            sokoenginepyext.cpp
            export_pusher_step.cpp
            export_board_cell.cpp
            export_board_graph.cpp
            export_tessellations.cpp
            export_board_manager.cpp
            export_mover.cpp
            export_sokoban_plus.cpp

            export_io_puzzle.cpp
            export_io_snapshot.cpp
            export_io_collection.cpp
            export_io_rle.cpp

            sokoenginepyext.hpp
        )

        target_link_libraries(sokoenginepyext PRIVATE sokoengine_obj_hidden)

    else(pybind11_FOUND)
        message(
            STATUS
            "sokoenginepyext Python C++ extension will not be configured because "
            "pybind11 was not found in '${Python3_SITELIB}'. "
            "If you need sokoenginepyext, run 'pip install pybind11' before running "
            "cmake."
        )
    endif(pybind11_FOUND)
else()
    message(
        STATUS
        "sokoenginepyext Python C++ extension will not be configured because Python3 "
        "was not found. If you need this, create Python virtual env and activate "
        "it before running cmake."
    )
endif(Python3_FOUND)

# ..............................................................................
# Development utilities
# ..............................................................................
file(WRITE
    "${CMAKE_BINARY_DIR}/benchmarks.cpp"
    "#include <sokoengine.hpp>\n\nint main() { return sokoengine::run_benchmarks(); }\n"
)
add_executable(benchmarks EXCLUDE_FROM_ALL "${CMAKE_BINARY_DIR}/benchmarks.cpp")
target_link_libraries(benchmarks PUBLIC sokoengine)

# add_valgrind_profile_dump_target(benchmarks)
# add_valgrind_memory_check_target(benchmarks)
set_target_properties(benchmarks
    PROPERTIES
    EXCLUDE_FROM_DEFAULT_BUILD 1
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
)
