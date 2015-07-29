import pytest
from sokoengine import (
    Variant, BoardConversionError, Direction, INDEX, IllegalDirectionError
)
from sokoengine.variant import SokobanBoard, VariantBoard, TriobanBoard
from hamcrest import assert_that, equal_to, greater_than, is_, none


class DescribeVariantBoard(object):
    class describe_init(object):
        def test_creates_board_of_specified_size_and_tessellation(self):
            b = TriobanBoard(4, 2)
            assert_that(b.width, equal_to(4))
            assert_that(b.height, equal_to(2))
            assert_that(b.variant, equal_to(Variant.TRIOBAN))

        def test_ignores_specified_size_if_string_given_and_parses_string_instead(
            self, board_str, board_str_width, board_str_height
        ):
            b = SokobanBoard(4, 2, board_str=board_str)
            assert_that(b.width, equal_to(board_str_width))
            assert_that(b.height, equal_to(board_str_height))
            assert_that(b.to_s(), equal_to(board_str))

        def test_raises_on_illegal_board_string(self):
            with pytest.raises(BoardConversionError):
                SokobanBoard(board_str="ZOOMG!")

    class describe__reinit(object):
        def test_reinitializes_graph_vertices(self, variant_board):
            variant_board._reinit(width=2, height=3)
            assert_that(
                len(variant_board._graph.nodes()),
                equal_to(2 * 3)
            )

            for position in range(0, variant_board.size):
                assert_that(variant_board[position].is_empty_floor, equal_to(True))

        def test_reinitializes_width_and_height(self, variant_board):
            variant_board._reinit(width=4, height=5)
            assert_that(variant_board.width, equal_to(4))
            assert_that(variant_board.height, equal_to(5))

        def test_optionally_recreates_all_adges(self, variant_board):
            variant_board._reinit(width=4, height=5, reconfigure_edges=False)
            assert_that(len(variant_board._graph.edges()), equal_to(0))
            variant_board._reinit(width=4, height=5)
            assert_that(len(variant_board._graph.edges()), greater_than(0))

    class describe__has_edge(object):
        def test_true_if_edge_in_given_direction_exists(self, variant_board):
            assert_that(
                variant_board._has_edge(0, 1, Direction.RIGHT),
                equal_to(True)
            )

    class describe__reconfigure_edges(object):
        def test_reconfigures_all_edges_in_board(self):
            variant_board = SokobanBoard(2, 2)
            assert_that(variant_board._graph.number_of_edges(), equal_to(8))
            assert_that(
                variant_board._has_edge(0, 1, Direction.RIGHT), equal_to(True)
            )
            assert_that(
                variant_board._has_edge(1, 0, Direction.LEFT), equal_to(True)
            )
            assert_that(
                variant_board._has_edge(0, 2, Direction.DOWN), equal_to(True)
            )
            assert_that(
                variant_board._has_edge(2, 0, Direction.UP), equal_to(True)
            )
            assert_that(
                variant_board._has_edge(2, 3, Direction.RIGHT), equal_to(True)
            )
            assert_that(
                variant_board._has_edge(3, 2, Direction.LEFT), equal_to(True)
            )
            assert_that(
                variant_board._has_edge(1, 3, Direction.DOWN), equal_to(True)
            )
            assert_that(
                variant_board._has_edge(3, 1, Direction.UP), equal_to(True)
            )

        def test_doesnt_create_duplicate_direction_edges_in_multidigraph(self):
            # Trioban is only tessellation that requires multidigraph
            variant_board = TriobanBoard(2, 2)
            assert_that(len(variant_board._graph[0][1]), equal_to(2))
            assert_that(len(variant_board._graph[1][0]), equal_to(2))

            variant_board._reconfigure_edges()
            assert_that(len(variant_board._graph[0][1]), equal_to(2))
            assert_that(len(variant_board._graph[1][0]), equal_to(2))

    class describe__out_edge_weight(object):
        def test_returns_max_weigth_for_wall_cell_target(self, variant_board):
            variant_board[1].is_wall = True
            assert_that(
                variant_board._out_edge_weight([0, 1]),
                equal_to(VariantBoard._MAX_EDGE_WEIGHT)
            )

        def test_returns_max_weigth_for_pusher_cell_target(self, variant_board):
            variant_board[1].has_pusher = True
            assert_that(
                variant_board._out_edge_weight([0, 1]),
                equal_to(VariantBoard._MAX_EDGE_WEIGHT)
            )

        def test_returns_max_weigth_for_box_cell_target(self, variant_board):
            variant_board[1].has_box = True
            assert_that(
                variant_board._out_edge_weight([0, 1]),
                equal_to(VariantBoard._MAX_EDGE_WEIGHT)
            )

        def test_returns_one_for_other_cells(self, variant_board):
            variant_board[1].clear()
            assert_that(variant_board._out_edge_weight([0, 1]), equal_to(1))
            variant_board[1].has_goal = True
            assert_that(variant_board._out_edge_weight([0, 1]), equal_to(1))

    class describe__reachables(object):
        board_str = "\n".join([
            # 123456
            "#######",  # 0
            "#.$# @#",  # 1
            "#######",  # 2
            "#     #",  # 3
            "#######",  # 4
        ])
        variant_board = SokobanBoard(board_str=board_str)

        def test_calculates_all_positions_reachable_from_root(self):
            root = INDEX(5, 1, 7)
            assert_that(
                self.variant_board._reachables(root),
                equal_to([
                    root, INDEX(4, 1, 7)
                ])
            )

        def test_skips_explicitly_excluded_positions(self):
            root = INDEX(5, 1, 7)
            assert_that(
                self.variant_board._reachables(root, excluded_positions=[root]),
                equal_to([INDEX(4, 1, 7)])
            )

            root = INDEX(5, 1, 7)
            assert_that(
                self.variant_board._reachables(root, excluded_positions=[INDEX(4, 1, 7)]),
                equal_to([root])
            )

    class describe_neighbor(object):
        def test_returns_neighbor_position_in_given_direction(self, variant_board):
            assert_that(variant_board.neighbor(0, Direction.RIGHT), equal_to(1))

        def test_returns_none_for_of_board_target_position(self, variant_board):
            assert_that(
                variant_board.neighbor(0, Direction.UP),
                is_(none())
            )

        def test_raises_for_of_board_source_position(self, variant_board):
            with pytest.raises(IndexError):
                variant_board.neighbor(42000, Direction.UP)

        def test_returns_none_for_illegal_direction(self, variant_board):
            assert_that(
                variant_board.neighbor(0, Direction.NORTH_WEST),
                is_(none())
            )

    class describe_clear(object):
        def test_clears_board_cells_in_all_nodes(self, variant_board):
            variant_board.clear()
            for pos in range(0, variant_board.size):
                assert_that(variant_board[pos].is_empty_floor, equal_to(True))

        def test_doesnt_change_board_dimensions(self, variant_board):
            old_width = variant_board.width
            old_height = variant_board.height
            variant_board.clear()
            assert_that(variant_board.width, equal_to(old_width))
            assert_that(variant_board.height, equal_to(old_height))

    class describe_mark_play_area(object):
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
            INDEX(1, 1, 7),
            INDEX(2, 1, 7),
            INDEX(4, 1, 7),
            INDEX(5, 1, 7),
        ]

        def test_calculates_playable_area_of_board_marking_all_playable_cells(self):
            self.variant_board.mark_play_area()
            for pos in range(0, self.variant_board.size):
                if pos in self.expected_playable_cells:
                    assert_that(
                        self.variant_board[pos].is_in_playable_area, equal_to(True)
                    )
                else:
                    assert_that(
                        self.variant_board[pos].is_in_playable_area, equal_to(False)
                    )

    class describe_positions_reachable_by_pusher(object):
        board_str = "\n".join([
            # 123456
            "#######",  # 0
            "#.$  @#",  # 1
            "# # ###",  # 2
            "#   #  ",  # 3
            "#####  ",  # 4
        ])
        variant_board = SokobanBoard(board_str=board_str)

        def test_returns_list_of_positions_reachable_by_pusher_movement_only(self):
            expected = [
                INDEX(5, 1, 7),
                INDEX(4, 1, 7),
                INDEX(3, 1, 7),
                INDEX(3, 2, 7),
                INDEX(3, 3, 7),
                INDEX(2, 3, 7),
                INDEX(1, 3, 7),
                INDEX(1, 2, 7),
                INDEX(1, 1, 7),
            ]
            assert_that(
                self.variant_board.positions_reachable_by_pusher(
                    pusher_position=INDEX(5, 1, 7)
                ),
                equal_to(expected)
            )

        def test_doesnt_require_that_start_position_actually_contain_pusher(self):
            expected = [
                INDEX(4, 1, 7),
                INDEX(3, 1, 7),
                INDEX(3, 2, 7),
                INDEX(3, 3, 7),
                INDEX(2, 3, 7),
                INDEX(1, 3, 7),
                INDEX(1, 2, 7),
                INDEX(1, 1, 7),
            ]
            assert_that(
                self.variant_board.positions_reachable_by_pusher(
                    pusher_position=INDEX(4, 1, 7)
                ),
                equal_to(expected)
            )

        def test_can_exclude_some_positions(self):
            expected = [
                INDEX(5, 1, 7),
                INDEX(4, 1, 7),
                INDEX(3, 1, 7),
                INDEX(3, 2, 7),
            ]
            excluded = [
                INDEX(3, 3, 7),
                INDEX(2, 3, 7),
                INDEX(1, 3, 7),
                INDEX(1, 2, 7),
                INDEX(1, 1, 7),
            ]
            assert_that(
                self.variant_board.positions_reachable_by_pusher(
                    pusher_position=INDEX(5, 1, 7),
                    excluded_positions=excluded
                ),
                equal_to(expected)
            )

        def test_raises_if_start_position_is_of_board(self):
            with pytest.raises(IndexError):
                self.variant_board.positions_reachable_by_pusher(42000)

    class describe_normalized_pusher_position(object):
        board_str = "\n".join([
            # 123456
            "#######",  # 0
            "#.$  @#",  # 1
            "# # ###",  # 2
            "#   #  ",  # 3
            "#####  ",  # 4
        ])
        variant_board = SokobanBoard(board_str=board_str)

        def test_returns_top_left_position_of_pusher_in_his_reachable_area(self):
            assert_that(
                self.variant_board.normalized_pusher_position(
                    pusher_position=INDEX(5, 1, 7)
                ),
                equal_to(INDEX(1, 1, 7))
            )

        def test_doesnt_require_that_start_position_actually_contain_pusher(self):
            assert_that(
                self.variant_board.normalized_pusher_position(
                    pusher_position=INDEX(4, 1, 7)
                ),
                equal_to(INDEX(1, 1, 7))
            )

        def test_can_exclude_some_positions(self):
            assert_that(
                self.variant_board.normalized_pusher_position(
                    pusher_position=INDEX(4, 1, 7),
                    excluded_positions=[INDEX(1, 1, 7)]
                ),
                equal_to(INDEX(3, 1, 7))
            )

        def test_raises_if_start_position_is_of_board(self):
            with pytest.raises(IndexError):
                self.variant_board.normalized_pusher_position(42000)

    class describe_path_destination(object):
        def test_calculates_destination_position_from_source_and_direction_path(
            self, variant_board
        ):
            direction_path = [
                Direction.UP, Direction.RIGHT
            ]
            start_position = INDEX(11, 8, variant_board.width)
            assert_that(
                variant_board.path_destination(start_position, direction_path),
                equal_to(INDEX(12, 7, variant_board.width))
            )

        def test_silently_stops_search_on_first_of_board_position(
            self, variant_board
        ):
            direction_path = [
                Direction.DOWN, Direction.DOWN, Direction.DOWN
            ]
            start_position = INDEX(11, 8, variant_board.width)
            assert_that(
                variant_board.path_destination(start_position, direction_path),
                equal_to(INDEX(11, 10, variant_board.width))
            )

        def test_silently_stops_search_on_illegal_direction(self, variant_board):
            direction_path = [
                Direction.DOWN, Direction.NORTH_WEST
            ]
            start_position = INDEX(11, 8, variant_board.width)
            assert_that(
                variant_board.path_destination(start_position, direction_path),
                equal_to(INDEX(11, 9, variant_board.width))
            )

        def test_raises_if_start_position_is_of_board(self, variant_board):
            with pytest.raises(IndexError):
                variant_board.path_destination(42000, []),

    class describe_find_jump_path(object):
        def test_returns_sequence_of_positions_defining_shortest_path_for_pusher_jump(
            self, variant_board
        ):
            start_position = INDEX(11, 8, variant_board.width)
            end_position = INDEX(8, 5, variant_board.width)
            expected = variant_board.position_path_to_direction_path(
                variant_board.find_jump_path(start_position, end_position)
            )
            assert_that(
                expected['path'], equal_to([
                    Direction.UP, Direction.UP, Direction.UP,
                    Direction.LEFT, Direction.LEFT, Direction.LEFT,
                ])
            )

        def test_raises_if_start_position_is_of_board(self, variant_board):
            with pytest.raises(IndexError):
                variant_board.find_jump_path(42000, 42)

        def test_returns_empty_sequence_if_jumping_of_board(self, variant_board):
            assert_that(
                variant_board.find_jump_path(42, 42000), equal_to([])
            )

    class describe_find_move_path(object):
        def test_returns_sequence_of_positions_defining_shortest_path_for_pusher_movement_without_pushing_boxes(
            self, variant_board
        ):
            start_position = INDEX(11, 8, variant_board.width)
            end_position = INDEX(8, 5, variant_board.width)
            expected = variant_board.position_path_to_direction_path(
                variant_board.find_move_path(start_position, end_position)
            )
            assert_that(
                expected['path'], equal_to([
                    Direction.UP,
                    Direction.LEFT, Direction.LEFT, Direction.LEFT,
                    Direction.UP, Direction.UP,
                ])
            )

        def test_raises_if_start_position_is_of_board(self, variant_board):
            with pytest.raises(IndexError):
                variant_board.find_move_path(42000, 42)

        def test_returns_empty_sequence_if_moving_of_board(self, variant_board):
            assert_that(
                variant_board.find_move_path(42, 42000), equal_to([])
            )

        def test_returns_empty_sequence_if_movement_is_blocked(self, variant_board):
            assert_that(
                variant_board.find_move_path(
                    INDEX(11, 8, variant_board.width), 0
                ), equal_to([])
            )
