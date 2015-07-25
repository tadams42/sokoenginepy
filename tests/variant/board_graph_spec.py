from sokoengine.variant import BoardGraph
import pytest


class DescribeBoardGraph(object):

    class describe_has_edge(object):
        @pytest.mark.xfail
        def test_true_if_source_vertice_has_edge_to_dest_vertice_in_given_direction(
            self
        ):
            assert False

    class describe_configure_edges(object):
        @pytest.mark.xfail
        def test_creates_edges_for_all_vertices_using_tessellation(self):
            assert False

        @pytest.mark.xfail
        def test_runs_only_if_edges_are_not_already_configured(self):
            assert False

    class describe_out_edge_weight(object):
        @pytest.mark.xfail
        def test_returns_max_weight_for_bloking_destination_vertice(self):
            assert False

        @pytest.mark.xfail
        def test_returns_one_for_non_blocking_destination_vertice(self):
            assert False

    class describe_reachables(object):
        @pytest.mark.xfail
        def test_calculates_all_positions_reachable_from_root(self):
            assert False

        @pytest.mark.xfail
        def test_skips_explicitly_excluded_positions(self):
            assert False

    class describe_clear(object):
        @pytest.mark.xfail
        def test_clears_board_cells_in_all_nodes(self):
            assert False

        @pytest.mark.xfail
        def test_doesnt_change_board_dimensions(self):
            assert False

    class describe_mark_play_area(object):
        @pytest.mark.xfail
        def test_calculates_playable_area_of_board_marking_all_cells_in_it(self):
            assert False

    class describe_positions_reachable_by_pusher(object):
        @pytest.mark.xfail
        def test_returns_list_of_positions_reachable_by_pusher_movement_only(self):
            assert False

        @pytest.mark.xfail
        def test_doesnt_require_that_start_position_actually_contain_pusher(self):
            assert False

    class describe_normalized_pusher_position(object):
        @pytest.mark.xfail
        def test_returns_top_left_position_of_pusher_in_his_reachable_area(self):
            assert False

    class describe_path_destination(object):
        @pytest.mark.xfail
        def test_calculates_destination_position_from_source_and_direction_path(self):
            assert False

    class describe_find_jump_path(object):
        @pytest.mark.xfail
        def test_returns_sequence_of_positions_defining_shortest_path_for_pusher_jump(self):
            assert False

    class describe_find_move_path(object):
        @pytest.mark.xfail
        def test_returns_sequence_of_positions_defining_shortest_path_for_pusher_movement_without_pushing_boxes(self):
            assert False

    class describe_cell_orientation(object):
        @pytest.mark.xfail
        def test_calculates_cell_orientation_using_tessellation_and_position(self):
            assert False
