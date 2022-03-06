#..............................................................................
#                             Python bindings module
#..............................................................................

if(ENABLE_PYTHON_EXTENSION)
    include(libsokoengine_pybind11)

    pybind11_add_module(sokoenginepyext
        sokoenginepyext.cpp
        export_direction.cpp
        export_atomic_move.cpp
        export_board_cell.cpp
        export_board_graph.cpp
        export_tessellations.cpp
        export_boards.cpp
        export_board_manager.cpp
        export_mover.cpp
        sokoenginepyext.hpp
    )

    target_link_libraries(sokoenginepyext PRIVATE sokoengine_obj)

    set_target_properties(sokoenginepyext PROPERTIES
                                          EXCLUDE_FROM_ALL TRUE
                                          EXCLUDE_FROM_DEFAULT_BUILD TRUE)

endif(ENABLE_PYTHON_EXTENSION)
