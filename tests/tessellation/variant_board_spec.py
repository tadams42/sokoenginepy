from unittest.mock import patch

import pytest
from sokoenginepy.board import BoardConversionError
from sokoenginepy.common import Direction, Variant
from sokoenginepy.input_output import OutputSettings
from sokoenginepy.tessellation import (BoardGraph, SokobanBoard, TriobanBoard,
                                       index_1d)


class DescribeVariantBoard:

    class describe_init:

        def it_creates_board_of_specified_size_and_tessellation(self):
            b = TriobanBoard(4, 2)
            assert b.width == 4
            assert b.height == 2
            assert b.variant == Variant.TRIOBAN

        def it_ignores_specified_size_if_string_given_and_parses_string_instead(
            self, board_str, board_str_width, board_str_height
        ):
            b = SokobanBoard(4, 2, board_str=board_str)
            assert b.width == board_str_width
            assert b.height == board_str_height
            assert b.to_s() == board_str

        def it_raises_on_illegal_board_string(self):
            with pytest.raises(BoardConversionError):
                SokobanBoard(board_str="ZOOMG!")

    class describe__reinit:

        def it_reinitializes_graph_vertices(self, variant_board):
            variant_board._reinit(width=2, height=3)
            assert variant_board._graph.vertices_count() == 2 * 3

            for position in range(0, variant_board.size):
                assert variant_board[position].is_empty_floor

        def it_reinitializes_width_and_height(self, variant_board):
            variant_board._reinit(width=4, height=5)
            assert variant_board.width == 4
            assert variant_board.height == 5

        def it_optionally_recreates_all_adges(self, variant_board):
            variant_board._reinit(width=4, height=5, reconfigure_edges=False)
            assert variant_board._graph.edges_count() == 0
            variant_board._reinit(width=4, height=5)
            assert variant_board._graph.edges_count() > 0

    class describe_clear:

        def it_clears_board_cells_in_all_nodes(self, variant_board):
            variant_board.clear()
            for pos in range(0, variant_board.size):
                assert variant_board[pos].is_empty_floor

        def it_doesnt_change_board_dimensions(self, variant_board):
            old_width = variant_board.width
            old_height = variant_board.height
            variant_board.clear()
            assert variant_board.width == old_width
            assert variant_board.height == old_height

    class describe_mark_play_area:
        board_str = "\n".join([
            # 123456
            "#######",  # 0
            "#.$# @#",  # 1
            "#######",  # 2
            "#     #",  # 3
            "#######",  # 4
        ])
        variant_board = SokobanBoard(board_str=board_str)

        expected_playable_cells = [
            index_1d(1, 1, 7),
            index_1d(2, 1, 7),
            index_1d(4, 1, 7),
            index_1d(5, 1, 7),
        ]

        def it_calculates_playable_area_of_board_marking_all_playable_cells(
            self
        ):
            self.variant_board.mark_play_area()
            for pos in range(0, self.variant_board.size):
                if pos in self.expected_playable_cells:
                    assert self.variant_board[pos].is_in_playable_area
                else:
                    assert not self.variant_board[pos].is_in_playable_area

    class describe_positions_reachable_by_pusher:
        board_str = "\n".join([
            # 123456
            "#######",  # 0
            "#.$  @#",  # 1
            "# # ###",  # 2
            "#   #  ",  # 3
            "#####  ",  # 4
        ])
        variant_board = SokobanBoard(board_str=board_str)

        def it_returns_list_of_positions_reachable_by_pusher_movement_only(
            self
        ):
            expected = [
                index_1d(5, 1, 7),
                index_1d(4, 1, 7),
                index_1d(3, 1, 7),
                index_1d(3, 2, 7),
                index_1d(3, 3, 7),
                index_1d(2, 3, 7),
                index_1d(1, 3, 7),
                index_1d(1, 2, 7),
                index_1d(1, 1, 7),
            ]
            assert self.variant_board.positions_reachable_by_pusher(
                pusher_position=index_1d(5, 1, 7)
            ) == expected

        def it_doesnt_require_that_start_position_actually_contain_pusher(self):
            expected = [
                index_1d(4, 1, 7),
                index_1d(3, 1, 7),
                index_1d(3, 2, 7),
                index_1d(3, 3, 7),
                index_1d(2, 3, 7),
                index_1d(1, 3, 7),
                index_1d(1, 2, 7),
                index_1d(1, 1, 7),
            ]
            assert self.variant_board.positions_reachable_by_pusher(
                pusher_position=index_1d(4, 1, 7)
            ) == expected

        def it_can_exclude_some_positions(self):
            expected = [
                index_1d(5, 1, 7),
                index_1d(4, 1, 7),
                index_1d(3, 1, 7),
                index_1d(3, 2, 7),
            ]
            excluded = [
                index_1d(3, 3, 7),
                index_1d(2, 3, 7),
                index_1d(1, 3, 7),
                index_1d(1, 2, 7),
                index_1d(1, 1, 7),
            ]
            assert self.variant_board.positions_reachable_by_pusher(
                pusher_position=index_1d(5, 1, 7), excluded_positions=excluded
            ) == expected

        def it_raises_if_start_position_is_of_board(self):
            with pytest.raises(IndexError):
                self.variant_board.positions_reachable_by_pusher(42000)

    class describe_normalized_pusher_position:
        board_str = "\n".join([
            # 123456
            "#######",  # 0
            "#.$  @#",  # 1
            "# # ###",  # 2
            "#   #  ",  # 3
            "#####  ",  # 4
        ])
        variant_board = SokobanBoard(board_str=board_str)

        def test_returns_top_left_position_of_pusher_in_his_reachable_area(
            self
        ):
            assert self.variant_board.normalized_pusher_position(
                pusher_position=index_1d(5, 1, 7)
            ) == index_1d(1, 1, 7)

        def test_doesnt_require_that_start_position_actually_contain_pusher(
            self
        ):
            assert self.variant_board.normalized_pusher_position(
                pusher_position=index_1d(4, 1, 7)
            ) == index_1d(1, 1, 7)

        def test_can_exclude_some_positions(self):
            assert self.variant_board.normalized_pusher_position(
                pusher_position=index_1d(4, 1, 7),
                excluded_positions=[index_1d(1, 1, 7)]
            ) == index_1d(3, 1, 7)

        def test_raises_if_start_position_is_of_board(self):
            with pytest.raises(IndexError):
                self.variant_board.normalized_pusher_position(42000)

    class describe_path_destination:

        def test_calculates_destination_position_from_source_and_direction_path(
            self, variant_board
        ):
            direction_path = [Direction.UP, Direction.RIGHT]
            start_position = index_1d(11, 8, variant_board.width)
            assert variant_board.path_destination(
                start_position, direction_path
            ) == index_1d(12, 7, variant_board.width)

        def test_silently_stops_search_on_first_of_board_position(
            self, variant_board
        ):
            direction_path = [Direction.DOWN, Direction.DOWN, Direction.DOWN]
            start_position = index_1d(11, 8, variant_board.width)
            assert variant_board.path_destination(
                start_position, direction_path
            ) == index_1d(11, 10, variant_board.width)

        def test_silently_stops_search_on_illegal_direction(
            self, variant_board
        ):
            direction_path = [Direction.DOWN, Direction.NORTH_WEST]
            start_position = index_1d(11, 8, variant_board.width)
            assert variant_board.path_destination(
                start_position, direction_path
            ) == index_1d(11, 9, variant_board.width)

        def test_raises_if_start_position_is_of_board(self, variant_board):
            with pytest.raises(IndexError):
                variant_board.path_destination(42000, []),

    class describe_find_jump_path:

        def test_returns_sequence_of_positions_defining_shortest_path_for_pusher_jump(
            self, variant_board
        ):
            start_position = index_1d(11, 8, variant_board.width)
            end_position = index_1d(8, 5, variant_board.width)
            expected = variant_board.position_path_to_direction_path(
                variant_board.find_jump_path(start_position, end_position)
            )
            assert expected['path'] == [
                Direction.UP,
                Direction.UP,
                Direction.UP,
                Direction.LEFT,
                Direction.LEFT,
                Direction.LEFT,
            ]

        def test_raises_if_start_position_is_of_board(self, variant_board):
            with pytest.raises(IndexError):
                variant_board.find_jump_path(42000, 42)

        def test_returns_empty_sequence_if_jumping_of_board(
            self, variant_board
        ):
            assert variant_board.find_jump_path(42, 42000) == []

    class describe_find_move_path:

        def test_returns_sequence_of_positions_defining_shortest_path_for_pusher_movement_without_pushing_boxes(
            self, variant_board
        ):
            start_position = index_1d(11, 8, variant_board.width)
            end_position = index_1d(8, 5, variant_board.width)
            expected = variant_board.position_path_to_direction_path(
                variant_board.find_move_path(start_position, end_position)
            )
            assert expected['path'] == [
                Direction.UP,
                Direction.LEFT,
                Direction.LEFT,
                Direction.LEFT,
                Direction.UP,
                Direction.UP,
            ]

        def test_raises_if_start_position_is_of_board(self, variant_board):
            with pytest.raises(IndexError):
                variant_board.find_move_path(42000, 42)

        def test_returns_empty_sequence_if_moving_of_board(self, variant_board):
            assert variant_board.find_move_path(42, 42000) == []

        def test_returns_empty_sequence_if_movement_is_blocked(
            self, variant_board
        ):
            assert variant_board.find_move_path(
                index_1d(11, 8, variant_board.width), 0
            ) == []

    class describe_neighbor:

        def test_returns_neighbor_position_in_given_direction(
            self, variant_board
        ):
            assert variant_board.neighbor(0, Direction.RIGHT) == 1

        def test_returns_none_for_of_board_target_position(self, variant_board):
            assert variant_board.neighbor(0, Direction.UP) is None

        def test_raises_for_of_board_source_position(self, variant_board):
            with pytest.raises(IndexError):
                variant_board.neighbor(42000, Direction.UP)

        def test_returns_none_for_illegal_direction(self, variant_board):
            assert variant_board.neighbor(0, Direction.NORTH_WEST) is None

    class describe_resize:

        def test_adds_right_columns_and_bottom_rows_when_enlarging(
            self, variant_board
        ):
            output = "\n".join([
                "----#####------------",
                "----#--@#------------",
                "----#$--#------------",
                "--###--$##-----------",
                "--#--$-$-#-----------",
                "###-#-##-#---######--",
                "#---#-##-#####--..#--",
                "#-$--$----------..#--",
                "#####-###-#@##--..#--",
                "----#-----#########--",
                "----#######----------",
                "---------------------",
                "---------------------",
            ])
            old_width = variant_board.width
            old_height = variant_board.height
            variant_board.resize(old_width + 2, old_height + 2)
            assert variant_board.width == old_width + 2
            assert variant_board.height == old_height + 2
            assert variant_board.to_s(OutputSettings(use_visible_floors=True)
                                     ) == output

        def test_removes_right_columns_and_bottom_rows_when_compacting(
            self, variant_board
        ):
            output = "\n".join([
                "----#####--------",
                "----#--@#--------",
                "----#$--#--------",
                "--###--$##-------",
                "--#--$-$-#-------",
                "###-#-##-#---####",
                "#---#-##-#####--.",
                "#-$--$----------.",
                "#####-###-#@##--.",
            ])
            old_width = variant_board.width
            old_height = variant_board.height
            variant_board.resize(old_width - 2, old_height - 2)
            assert variant_board.width == old_width - 2
            assert variant_board.height == old_height - 2
            assert variant_board.to_s(OutputSettings(use_visible_floors=True)
                                     ) == output

        def test_reconfigures_graph_edges_only_once(self, variant_board):
            with patch.object(
                BoardGraph, 'reconfigure_edges', return_value=None
            ) as mock_method:
                variant_board.resize(2, 2)
            assert mock_method.call_count == 1

    class describe_resize_and_center:

        def test_adds_columns_and_rows_when_enlarging(self, variant_board):
            output = "\n".join([
                "------------------------",
                "------------------------",
                "------#####-------------",
                "------#--@#-------------",
                "------#$--#-------------",
                "----###--$##------------",
                "----#--$-$-#------------",
                "--###-#-##-#---######---",
                "--#---#-##-#####--..#---",
                "--#-$--$----------..#---",
                "--#####-###-#@##--..#---",
                "------#-----#########---",
                "------#######-----------",
                "------------------------",
                "------------------------",
                "------------------------",
            ])
            old_width = variant_board.width
            old_height = variant_board.height
            variant_board.resize_and_center(old_width + 5, old_height + 5)
            assert variant_board.width == old_width + 5
            assert variant_board.height == old_height + 5
            assert variant_board.to_s(OutputSettings(use_visible_floors=True)
                                     ) == output

        def test_removes_right_columns_and_bottom_rows_when_compacting(
            self, variant_board
        ):
            output = "\n".join([
                "----#####--------",
                "----#--@#--------",
                "----#$--#--------",
                "--###--$##-------",
                "--#--$-$-#-------",
                "###-#-##-#---####",
                "#---#-##-#####--.",
                "#-$--$----------.",
                "#####-###-#@##--.",
            ])
            old_width = variant_board.width
            old_height = variant_board.height
            variant_board.resize(old_width - 2, old_height - 2)
            assert variant_board.width == old_width - 2
            assert variant_board.height == old_height - 2
            assert variant_board.to_s(OutputSettings(use_visible_floors=True)
                                     ) == output

        def test_reconfigures_graph_edges_only_once(self, variant_board):
            with patch.object(
                BoardGraph, 'reconfigure_edges', return_value=None
            ) as mock_method:
                variant_board.resize(2, 2)
            assert mock_method.call_count == 1

    class describe_trim:

        def test_removes_empty_outer_rows_and_columns(self, variant_board):
            output = variant_board.to_s(OutputSettings(use_visible_floors=True))
            old_width = variant_board.width
            old_height = variant_board.height

            variant_board.resize_and_center(old_width + 5, old_height + 5)
            variant_board.trim()

            assert variant_board.width == old_width
            assert variant_board.height == old_height
            assert variant_board.to_s(OutputSettings(use_visible_floors=True)
                                     ) == output

        def test_reconfigures_graph_edges_only_once(self, variant_board):
            with patch.object(
                BoardGraph, 'reconfigure_edges', return_value=None
            ) as mock_method:
                variant_board.resize(2, 2)
            assert mock_method.call_count == 1

    class describe_reverse_rows:

        def test_mirrors_board_up_down(self, variant_board):
            output = "\n".join([
                "----#######--------",
                "----#-----#########",
                "#####-###-#@##--..#",
                "#-$--$----------..#",
                "#---#-##-#####--..#",
                "###-#-##-#---######",
                "--#--$-$-#---------",
                "--###--$##---------",
                "----#$--#----------",
                "----#--@#----------",
                "----#####----------",
            ])
            variant_board.reverse_rows()
            assert variant_board.to_s(OutputSettings(use_visible_floors=True)
                                     ) == output

    class describe_reverse_columns:

        def test_mirrors_board_left_rightt(self, variant_board):
            output = "\n".join([
                "----------#####----",
                "----------#@--#----",
                "----------#--$#----",
                "---------##$--###--",
                "---------#-$-$--#--",
                "######---#-##-#-###",
                "#..--#####-##-#---#",
                "#..----------$--$-#",
                "#..--##@#-###-#####",
                "#########-----#----",
                "--------#######----",
            ])
            variant_board.reverse_columns()
            assert variant_board.to_s(OutputSettings(use_visible_floors=True)
                                     ) == output
