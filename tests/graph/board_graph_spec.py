from itertools import permutations

import pytest

from sokoenginepy import (
    BoardCell,
    BoardGraph,
    Direction,
    GraphType,
    SokobanBoard,
    Tessellation,
)
from sokoenginepy.utilities import index_1d


class DescribeBoardGraph:
    class describe_init:
        def it_raises_on_invalid_argument_values(self, is_using_native):
            exc_cls = TypeError if is_using_native else ValueError
            with pytest.raises(exc_cls):
                BoardGraph(-42000, 1, GraphType.DIRECTED)
            with pytest.raises(exc_cls):
                BoardGraph(1, -42000, GraphType.DIRECTED)
            for _ in [None, "ZOMG"]:
                with pytest.raises(TypeError):
                    BoardGraph(_, 1, GraphType.DIRECTED)

    class describe_getitem:
        def it_returns_board_cell_on_position(self, board_graph):
            assert isinstance(board_graph[0], BoardCell)

        def it_raises_if_trying_to_get_invalid_position(
            self, is_using_native, board_graph
        ):
            with pytest.raises(IndexError):
                board_graph[42000]
            exc_cls = TypeError if is_using_native else KeyError
            for _ in [-42000, None, "", "ZOMG!", "42"]:
                with pytest.raises(exc_cls):
                    board_graph[_]

    class describe_setitem:
        def it_sets_board_cell_on_position(self, board_graph):
            board_graph[0].is_in_playable_area = True
            board_graph[0].is_deadlock = True
            board_graph[0].is_wall = True

            bc = BoardCell(BoardCell.PUSHER)
            bc.is_in_playable_area = False
            bc.is_deadlock = False

            board_graph[0] = bc

            assert not board_graph[0].is_wall
            assert board_graph[0].has_pusher
            assert not board_graph[0].is_in_playable_area
            assert not board_graph[0].is_deadlock

            board_graph[0] = BoardCell.PUSHER

            assert not board_graph[0].is_wall
            assert board_graph[0].has_pusher
            assert not board_graph[0].is_in_playable_area
            assert not board_graph[0].is_deadlock

        def it_raises_if_trying_to_set_invalid_cell_value(self, board_graph):
            with pytest.raises(ValueError):
                board_graph[0] = ""
            with pytest.raises(ValueError):
                board_graph[0] = "  "
            with pytest.raises(ValueError):
                board_graph[0] = None

        def it_raises_if_trying_to_set_invalid_position(
            self, is_using_native, board_graph, board_cell
        ):
            with pytest.raises(IndexError):
                board_graph[42000] = board_cell
            exc_cls = TypeError if is_using_native else KeyError
            for _ in [-42000, None, "", "ZOMG!", "42"]:
                with pytest.raises(exc_cls):
                    board_graph[_] = board_cell

    class describe_contains:
        def it_detects_if_position_is_in_graph(self, board_graph):
            assert 0 in board_graph

        def it_doesnt_rise_if_checking_invalid_position_value(self, board_graph):
            for _ in [42000, -42000, None, "", "ZOMG!", "42"]:
                assert _ not in board_graph

    class describe_vertices_count:
        def it_returns_number_of_graph_positions(
            self, board_graph, board_width, board_height
        ):
            assert board_graph.vertices_count == board_width * board_height

    class describe_edges_count:
        def it_returns_number_of_graph_edges(self, board_graph):
            assert board_graph.edges_count == 776

    class describe_has_edge:
        def it_checks_if_edge_in_given_direction_exists(self, board_graph):
            assert board_graph.has_edge(0, 1, Direction.RIGHT)
            assert not board_graph.has_edge(0, 1, Direction.LEFT)

        def it_doesnt_rise_if_checking_invalid_position_value(self, board_graph):
            for _ in [42000, -42000, None, "", "ZOMG!", "42"]:
                assert not board_graph.has_edge(_, 1, Direction.LEFT)
                assert not board_graph.has_edge(1, _, Direction.LEFT)

    class describe_out_edges_count:
        def it_returns_number_of_edges_going_from_source_to_target_position(
            self, board_graph
        ):
            assert board_graph.out_edges_count(0, 1) == 1

        def it_doesnt_rise_if_checking_invalid_position_value(self, board_graph):
            for _ in [42000, -42000, None, "", "ZOMG!", "42"]:
                assert board_graph.out_edges_count(_, 1) == 0
                assert board_graph.out_edges_count(1, _) == 0

    class describe_remove_all_edges:
        def it_removes_all_edges_from_graph(self, board_graph):
            board_graph.remove_all_edges()
            assert board_graph.edges_count == 0

    class describe_add_edge:
        def it_adds_edge_between_two_positions(self, board_graph):
            board_graph.remove_all_edges()
            board_graph.add_edge(0, 1, Direction.LEFT)
            assert board_graph.edges_count == 1
            assert board_graph.has_edge(0, 1, Direction.LEFT)

        def it_raises_if_any_of_positions_are_invalid_values(
            self, is_using_native, board_graph
        ):
            board_graph.remove_all_edges()

            with pytest.raises(IndexError):
                board_graph.add_edge(42000, 1, Direction.LEFT)
            with pytest.raises(IndexError):
                board_graph.add_edge(1, 42000, Direction.LEFT)

            exc_cls = TypeError if is_using_native else KeyError
            for k in [-42000, None, "", "ZOMG!", "42"]:
                with pytest.raises(exc_cls):
                    board_graph.add_edge(k, 1, Direction.LEFT)
                with pytest.raises(exc_cls):
                    board_graph.add_edge(1, k, Direction.LEFT)

        def it_allows_adding_duplicate_edges(self):
            board_graph = BoardGraph(2, 2, GraphType.DIRECTED)
            board_graph.add_edge(0, 1, Direction.LEFT)
            board_graph.add_edge(0, 1, Direction.LEFT)
            assert board_graph.edges_count == 1
            assert board_graph.has_edge(0, 1, Direction.LEFT)

            board_graph = BoardGraph(2, 2, GraphType.DIRECTED_MULTI)
            board_graph.add_edge(0, 1, Direction.LEFT)
            board_graph.add_edge(0, 1, Direction.LEFT)
            assert board_graph.edges_count == 2
            assert board_graph.has_edge(0, 1, Direction.LEFT)

    class describe_out_edge_weight:
        def it_returns_max_weight_for_wall_cell_target(
            self, is_using_native, board_graph
        ):
            board_graph[1].is_wall = True
            if not is_using_native:
                assert board_graph.out_edge_weight(1) > len(Direction)
            else:
                assert board_graph.out_edge_weight(1) > Direction.__len__()

        def it_returns_max_weight_for_pusher_cell_target(
            self, is_using_native, board_graph
        ):
            board_graph[1].has_pusher = True
            if not is_using_native:
                assert board_graph.out_edge_weight(1) > len(Direction)
            else:
                assert board_graph.out_edge_weight(1) > Direction.__len__()

        def it_returns_max_weight_for_box_cell_target(
            self, is_using_native, board_graph
        ):
            board_graph[1].has_box = True
            if not is_using_native:
                assert board_graph.out_edge_weight(1) > len(Direction)
            else:
                assert board_graph.out_edge_weight(1) > Direction.__len__()

        def it_returns_one_for_other_cells(self, board_graph):
            board_graph[1].clear()
            assert board_graph.out_edge_weight(1) == 1
            board_graph[1].has_goal = True
            assert board_graph.out_edge_weight(1) == 1

        def it_raises_if_position_is_invalid_value(self, is_using_native, board_graph):
            with pytest.raises(IndexError):
                board_graph.out_edge_weight(42000)
            exc_cls = TypeError if is_using_native else KeyError
            for _ in [-42000, None, "", "ZOMG!", "42"]:
                with pytest.raises(exc_cls):
                    board_graph.out_edge_weight(_)

    class describe_neighbor:
        def it_returns_neighbor_position_in_given_direction(self, board_graph):
            assert board_graph.neighbor(0, Direction.RIGHT) == 1

        def it_returns_none_for_off_board_direction(self, board_graph):
            assert board_graph.neighbor(0, Direction.UP) is None

        def it_raises_if_position_is_invalid_value(self, is_using_native, board_graph):
            with pytest.raises(IndexError):
                board_graph.neighbor(42000, Direction.UP)
            exc_cls = TypeError if is_using_native else KeyError
            for _ in [-42000, None, "", "ZOMG!", "42"]:
                with pytest.raises(exc_cls):
                    board_graph.neighbor(_, Direction.UP)

    class describe_wall_neighbors:
        def it_returns_positions_of_walls_for_given_vertice(self):
            board_str = "\n".join(
                [
                    # 123456
                    "#######",  # 0
                    "#.$# @#",  # 1
                    "#######",  # 2
                ]
            )
            board_graph = SokobanBoard(board_str=board_str).graph
            wall_neighbors = board_graph.wall_neighbors(0)
            assert index_1d(0, 1, 7) in wall_neighbors
            assert index_1d(1, 0, 7) in wall_neighbors

        def it_raises_if_position_is_invalid_value(self, is_using_native, board_graph):
            with pytest.raises(IndexError):
                board_graph.wall_neighbors(42000)
            exc_cls = TypeError if is_using_native else KeyError
            for _ in [-42000, None, "", "ZOMG!", "42"]:
                with pytest.raises(exc_cls):
                    board_graph.wall_neighbors(_)

    class describe_all_neighbors:
        def it_returns_positions_of_all_neghbor_positions_for_given_vertice(
            self, board_graph, board_width
        ):
            all_neighbors = board_graph.all_neighbors(0)
            assert index_1d(0, 1, board_width) in all_neighbors
            assert index_1d(1, 1, board_width) not in all_neighbors
            assert index_1d(1, 0, board_width) in all_neighbors

        def it_raises_if_position_is_invalid_value(self, is_using_native, board_graph):
            with pytest.raises(IndexError):
                board_graph.all_neighbors(42000)
            exc_cls = TypeError if is_using_native else KeyError
            for _ in [-42000, None, "", "ZOMG!", "42"]:
                with pytest.raises(exc_cls):
                    board_graph.all_neighbors(_)

    class describe_shortest_path:
        def it_raises_if_any_of_positions_are_invalid_values(
            self, is_using_native, board_graph
        ):
            with pytest.raises(IndexError):
                board_graph.shortest_path(1, 42000)
            with pytest.raises(IndexError):
                board_graph.shortest_path(42000, 1)
            exc_cls = TypeError if is_using_native else KeyError
            for _ in [-42000, None, "", "ZOMG!", "42"]:
                with pytest.raises(exc_cls):
                    board_graph.shortest_path(_, 1)
                with pytest.raises(exc_cls):
                    board_graph.shortest_path(1, _)

    class describe_dijkstra_path:
        def it_raises_if_any_of_positions_are_invalid_values(
            self, is_using_native, board_graph
        ):
            with pytest.raises(IndexError):
                board_graph.dijkstra_path(1, 42000)
            with pytest.raises(IndexError):
                board_graph.dijkstra_path(42000, 1)
            exc_cls = TypeError if is_using_native else KeyError
            for _ in [-42000, None, "", "ZOMG!", "42"]:
                with pytest.raises(exc_cls):
                    board_graph.dijkstra_path(_, 1)
                with pytest.raises(exc_cls):
                    board_graph.dijkstra_path(1, _)

    class describe_find_jump_path:
        def it_returns_sequence_of_positions_defining_shortest_path_for_pusher_jump(
            self, board_graph, board_width
        ):
            start_position = index_1d(11, 8, board_width)
            end_position = index_1d(8, 5, board_width)
            expected = board_graph.positions_path_to_directions_path(
                board_graph.find_jump_path(start_position, end_position)
            )

            assert tuple(expected) in permutations(
                [
                    Direction.UP,
                    Direction.UP,
                    Direction.UP,
                    Direction.LEFT,
                    Direction.LEFT,
                    Direction.LEFT,
                ]
            )

        def it_raises_if_any_of_positions_are_invalid_values(
            self, is_using_native, board_graph
        ):
            with pytest.raises(IndexError):
                board_graph.find_jump_path(1, 42000)
            with pytest.raises(IndexError):
                board_graph.find_jump_path(42000, 1)
            exc_cls = TypeError if is_using_native else KeyError
            for _ in [-42000, None, "", "ZOMG!", "42"]:
                with pytest.raises(exc_cls):
                    board_graph.find_jump_path(_, 1)
                with pytest.raises(exc_cls):
                    board_graph.find_jump_path(1, _)

    class describe_find_move_path:
        def it_returns_sequence_of_positions_defining_shortest_path_for_pusher_movement_without_pushing_boxes(
            self, board_graph, board_width
        ):
            start_position = index_1d(11, 8, board_width)
            end_position = index_1d(8, 5, board_width)
            expected = board_graph.positions_path_to_directions_path(
                board_graph.find_move_path(start_position, end_position)
            )

            assert tuple(expected) in permutations(
                [
                    Direction.LEFT,
                    Direction.LEFT,
                    Direction.LEFT,
                    Direction.UP,
                    Direction.UP,
                    Direction.UP,
                ]
            )

        def it_raises_if_any_of_positions_are_invalid_values(
            self, is_using_native, board_graph
        ):
            with pytest.raises(IndexError):
                board_graph.find_move_path(1, 42000)
            with pytest.raises(IndexError):
                board_graph.find_move_path(42000, 1)
            exc_cls = TypeError if is_using_native else KeyError
            for _ in [-42000, None, "", "ZOMG!", "42"]:
                with pytest.raises(exc_cls):
                    board_graph.find_move_path(_, 1)
                with pytest.raises(exc_cls):
                    board_graph.find_move_path(1, _)

        def it_returns_empty_sequence_if_movement_is_blocked(
            self, board_graph, board_width
        ):
            assert board_graph.find_move_path(index_1d(11, 8, board_width), 0) == []

    class describe_positions_path_to_directions_path:
        def it_converts_path(self, board_graph, positions_path, directions_path):
            calculated_directions_path = board_graph.positions_path_to_directions_path(
                positions_path
            )
            assert calculated_directions_path == directions_path

        def it_raises_if_any_of_positions_are_invalid_values(
            self, is_using_native, board_graph
        ):
            with pytest.raises(IndexError):
                board_graph.positions_path_to_directions_path([42000])
            with pytest.raises(IndexError):
                board_graph.positions_path_to_directions_path([1, 42000])
            with pytest.raises(IndexError):
                board_graph.positions_path_to_directions_path([42000, 1])

            exc_cls = TypeError if is_using_native else KeyError
            for _ in [-42000, None, "", "ZOMG!", "42"]:
                with pytest.raises(exc_cls):
                    board_graph.positions_path_to_directions_path([_])
                with pytest.raises(exc_cls):
                    board_graph.positions_path_to_directions_path([1, _])
                with pytest.raises(exc_cls):
                    board_graph.positions_path_to_directions_path([_, 1])

        def it_returns_empty_path_if_source_path_is_to_short(self, board_graph):
            assert board_graph.positions_path_to_directions_path([]) == []
            assert board_graph.positions_path_to_directions_path([1]) == []

    class describe_mark_play_area:
        board_str = "\n".join(
            [
                # 123456
                "#######",  # 0
                "#.$# @#",  # 1
                "#######",  # 2
                "#     #",  # 3
                "#######",  # 4
            ]
        )
        board_graph = SokobanBoard(board_str=board_str).graph

        expected_playable_cells = [
            index_1d(1, 1, 7),
            index_1d(2, 1, 7),
            index_1d(4, 1, 7),
            index_1d(5, 1, 7),
        ]

        def it_calculates_playable_area_of_board_marking_all_playable_cells(self):
            self.board_graph.mark_play_area()
            for pos in range(self.board_graph.vertices_count):
                if pos in self.expected_playable_cells:
                    assert self.board_graph[pos].is_in_playable_area
                else:
                    assert not self.board_graph[pos].is_in_playable_area

    class describe_positions_reachable_by_pusher:
        board_str = "\n".join(
            [
                # 123456
                "#######",  # 0
                "#.$  @#",  # 1
                "# # ###",  # 2
                "#   #  ",  # 3
                "#####  ",  # 4
            ]
        )
        board_graph = SokobanBoard(board_str=board_str).graph

        def it_returns_list_of_positions_reachable_by_pusher_movement_only(self):
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
            assert (
                self.board_graph.positions_reachable_by_pusher(
                    pusher_position=index_1d(5, 1, 7)
                )
                == expected
            )

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
            assert (
                self.board_graph.positions_reachable_by_pusher(
                    pusher_position=index_1d(4, 1, 7)
                )
                == expected
            )

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
            assert (
                self.board_graph.positions_reachable_by_pusher(
                    pusher_position=index_1d(5, 1, 7), excluded_positions=excluded
                )
                == expected
            )

        def it_raises_if_start_position_is_illegal_value(
            self, is_using_native, board_graph
        ):
            with pytest.raises(IndexError):
                board_graph.positions_reachable_by_pusher(42000)
            exc_cls = TypeError if is_using_native else KeyError
            for _ in [-42000, None, "", "ZOMG!", "42"]:
                with pytest.raises(exc_cls):
                    board_graph.positions_reachable_by_pusher(_)

    class describe_normalized_pusher_position:
        board_str = "\n".join(
            [
                # 123456
                "#######",  # 0
                "#.$  @#",  # 1
                "# # ###",  # 2
                "#   #  ",  # 3
                "#####  ",  # 4
            ]
        )
        board_graph = SokobanBoard(board_str=board_str).graph

        def it_returns_top_left_position_of_pusher_in_his_reachable_area(self):
            assert self.board_graph.normalized_pusher_position(
                pusher_position=index_1d(5, 1, 7)
            ) == index_1d(1, 1, 7)

        def it_doesnt_require_that_start_position_actually_contain_pusher(self):
            assert self.board_graph.normalized_pusher_position(
                pusher_position=index_1d(4, 1, 7)
            ) == index_1d(1, 1, 7)

        def it_can_exclude_some_positions(self):
            assert self.board_graph.normalized_pusher_position(
                pusher_position=index_1d(4, 1, 7),
                excluded_positions=[index_1d(1, 1, 7)],
            ) == index_1d(3, 1, 7)

        def it_raises_if_start_position_is_illegal_value(self, is_using_native):
            with pytest.raises(IndexError):
                self.board_graph.normalized_pusher_position(42000)
            exc_cls = TypeError if is_using_native else KeyError
            for _ in [-42000, None, "", "ZOMG!", "42"]:
                with pytest.raises(exc_cls):
                    self.board_graph.normalized_pusher_position(_)

    class describe_path_destination:
        def it_calculates_destination_position_from_source_and_directions_path(
            self, board_graph, board_width
        ):
            directions_path = [Direction.UP, Direction.RIGHT]
            start_position = index_1d(11, 8, board_width)
            assert board_graph.path_destination(
                start_position, directions_path
            ) == index_1d(12, 7, board_width)

        def it_silently_stops_search_on_first_off_board_position(
            self, board_graph, board_width
        ):
            directions_path = [Direction.DOWN, Direction.DOWN, Direction.DOWN]
            start_position = index_1d(11, 8, board_width)
            assert board_graph.path_destination(
                start_position, directions_path
            ) == index_1d(11, 10, board_width)

        def it_silently_stops_search_on_illegal_direction(
            self, board_graph, board_width
        ):
            directions_path = [Direction.DOWN, Direction.NORTH_WEST]
            start_position = index_1d(11, 8, board_width)
            assert board_graph.path_destination(
                start_position, directions_path
            ) == index_1d(11, 9, board_width)

        def it_raises_if_start_position_is_illegal_value(
            self, is_using_native, board_graph
        ):
            with pytest.raises(IndexError):
                board_graph.path_destination(42000, [])
            exc_cls = TypeError if is_using_native else KeyError
            for _ in [-42000, None, "", "ZOMG!", "42"]:
                with pytest.raises(exc_cls):
                    board_graph.path_destination(_, [])

    # class describe__reachables:
    #     board_str = "\n".join(
    #         [
    #             # 123456
    #             "#######",  # 0
    #             "#.$# @#",  # 1
    #             "#######",  # 2
    #             "#     #",  # 3
    #             "#######",  # 4
    #         ]
    #     )
    #     board_graph = SokobanBoard(board_str=board_str).graph

    #     def it_calculates_all_positions_reachable_from_root(self):
    #         if not hasattr(self.board_graph, "_reachables"):
    #             return

    #         root = index_1d(5, 1, 7)
    #         assert self.board_graph._reachables(root) == [root, index_1d(4, 1, 7)]

    #     def it_skips_explicitly_excluded_positions(self):
    #         if not hasattr(self.board_graph, "_reachables"):
    #             return

    #         root = index_1d(5, 1, 7)
    #         assert self.board_graph._reachables(root, excluded_positions=[root]) == [
    #             index_1d(4, 1, 7)
    #         ]
    #         root = index_1d(5, 1, 7)
    #         assert self.board_graph._reachables(
    #             root, excluded_positions=[index_1d(4, 1, 7)]
    #         ) == [root]

    class describe_reconfigure_edges:
        def it_reconfigures_all_edges_in_board(self):
            graph = BoardGraph(2, 2, GraphType.DIRECTED)
            graph.reconfigure_edges(Tessellation.SOKOBAN.value)

            assert graph.edges_count == 8
            assert graph.has_edge(0, 1, Direction.RIGHT)
            assert graph.has_edge(1, 0, Direction.LEFT)
            assert graph.has_edge(0, 2, Direction.DOWN)
            assert graph.has_edge(2, 0, Direction.UP)
            assert graph.has_edge(2, 3, Direction.RIGHT)
            assert graph.has_edge(3, 2, Direction.LEFT)
            assert graph.has_edge(1, 3, Direction.DOWN)
            assert graph.has_edge(3, 1, Direction.UP)

        def it_doesnt_create_duplicate_direction_edges_in_multidigraph(self):
            graph = BoardGraph(2, 2, GraphType.DIRECTED_MULTI)
            graph.reconfigure_edges(Tessellation.TRIOBAN.value)
            assert graph.out_edges_count(0, 1) == 2
            assert graph.out_edges_count(1, 0) == 2
