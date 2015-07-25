from sokoengine.variant.board_graph import BoardGraph


class DescribeBoardGraph(object):
    pass

    class describe_has_edge(object):
        def test_true_if_source_vertice_has_edge_to_dest_vertice_in_given_direction(
            self
        ):
            pass

    class describe_configure_edges(object):
        def test_creates_edges_for_all_vertices_using_tessellation(self):
            pass

        def test_runs_only_if_edges_are_not_already_configured(self):
            pass


    class describe_out_edge_weight(object):
        def test_returns_max_weight_for_bloking_destination_vertice(self):
            pass

        def test_returns_one_for_non_blocking_destination_vertice(self):
            pass

    class describe_reachables(object):
        def test_calculates_all_positions_reachable_from_root(self):
            pass

        def test_skips_explicitly_excluded_positions(self):
            pass

    class describe_clear(object):
        def test_clears_board_cells_in_all_nodes(self):
            pass

        def test_doesnt_change_board_dimensions(self):
            pass

    class describe_mark_play_area(object):
        def test_calculates_playable_area_of_board_marking_all_cells_in_it(self):
            pass

    class describe_positions_reachable_by_pusher(object):
        def test_returns_list_of_positions_reachable_by_pusher_movement_only(self):
            pass

        def test_doesnt_require_that_start_position_actually_contain_pusher(self):
            pass

    class describe_normalized_pusher_position(object):
        def test_returns_top_left_position_of_pusher_in_his_reachable_area(self):
            pass

    class describe_path_destination(object):
        def test_calculates_destination_position_from_source_and_path(self):
            pass

    class describe_(object):
        def test_(self):
            pass

    class describe_find_jump_path(object):
        def test_returns_sequence_of_positions_defining_shortest_path_for_pusher_jump(self):
            pass

    class describe_find_move_path(object):
        def test_returns_sequence_of_positions_defining_shortest_path_for_pusher_movement_without_pushing_boxes(self):
            pass

    class describe_cell_orientation(object):
        def test_calculates_cell_orientation_using_tessellation_and_position(self):
            pass
