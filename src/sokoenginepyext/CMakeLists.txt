# ..............................................................................
# Python native extension - sokoenginepyext
# ..............................................................................

if(Python3_FOUND)
    if(pybind11_FOUND)
        pybind11_add_module(sokoenginepyext
            export_board_cell.cpp
            export_board_graph.cpp
            export_board_manager.cpp
            export_io_collection.cpp
            export_io_puzzle.cpp
            export_io_rle.cpp
            export_io_snapshot.cpp
            export_mover.cpp
            export_pusher_step.cpp
            export_sokoban_plus.cpp
            sokoenginepyext.cpp
            sokoenginepyext.hpp
        )

        target_link_libraries(sokoenginepyext PRIVATE sokoengine_obj_hidden)
        set_target_properties(sokoenginepyext
            PROPERTIES
            EXCLUDE_FROM_DEFAULT_BUILD 1
            EXCLUDE_FROM_ALL 1
        )

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
