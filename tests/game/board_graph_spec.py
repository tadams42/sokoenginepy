import textwrap
from itertools import permutations
from typing import List

import pytest

from sokoenginepy.game import (
    BoardCell,
    BoardGraph,
    Config,
    Direction,
    Edge,
    Tessellation,
    index_1d,
)
from sokoenginepy.io import Puzzle, SokobanPuzzle, TriobanPuzzle


@pytest.fixture
def puzzle():
    data = """
            #####
            #   #
            #$  #
          ###  $##
          #  $ $ #
        ### # ## #   ######
        #   # ## #####  ..#
        # $  $          ..#
        ##### ### #@##  ..#
            #     #########
            #######
    """
    data = textwrap.dedent(data)
    return SokobanPuzzle(board=data)


@pytest.fixture
def solved_puzzle():
    data = """
            #####
            #  @#
            #   #
          ###   ##
          #      #
        ### # ## #   ######
        #   # ## #####  **#
        #               **#
        ##### ### #@##  **#
            #     #########
            #######
    """
    data = textwrap.dedent(data)
    return SokobanPuzzle(board=data)


@pytest.fixture
def board_graph(puzzle):
    return BoardGraph(puzzle)


@pytest.fixture
def positions_path(puzzle):
    return [
        index_1d(7, 1, puzzle.width),
        index_1d(6, 1, puzzle.width),
        index_1d(6, 2, puzzle.width),
        index_1d(6, 3, puzzle.width),
        index_1d(6, 4, puzzle.width),
        index_1d(5, 4, puzzle.width),
    ]


@pytest.fixture
def directions_path():
    return [
        Direction.LEFT,
        Direction.DOWN,
        Direction.DOWN,
        Direction.DOWN,
        Direction.LEFT,
    ]


def _sorted(edges: List[Edge]):
    return sorted(edges, key=lambda e: (e.u, e.v, e.direction.value))


class DescribeBoardGraph:
    class describe_init:
        def it_configures_all_edges_in_board(self):
            graph = BoardGraph(SokobanPuzzle(width=2, height=2))

            assert graph.edges_count == 8

            assert _sorted(graph.out_edges(0)) == _sorted(
                [
                    Edge(u=0, v=1, direction=Direction.RIGHT),
                    Edge(u=0, v=2, direction=Direction.DOWN),
                ]
            )
            assert _sorted(graph.out_edges(1)) == _sorted(
                [
                    Edge(u=1, v=0, direction=Direction.LEFT),
                    Edge(u=1, v=3, direction=Direction.DOWN),
                ]
            )
            assert _sorted(graph.out_edges(2)) == _sorted(
                [
                    Edge(u=2, v=3, direction=Direction.RIGHT),
                    Edge(u=2, v=0, direction=Direction.UP),
                ]
            )
            assert _sorted(graph.out_edges(3)) == _sorted(
                [
                    Edge(u=3, v=2, direction=Direction.LEFT),
                    Edge(u=3, v=1, direction=Direction.UP),
                ]
            )

            with pytest.raises(IndexError):
                graph.out_edges(4)

        def it_configures_trioban_edges_without_duplicates(self):
            graph = BoardGraph(TriobanPuzzle(width=2, height=2))

            assert _sorted(graph.out_edges(0)) == _sorted(
                [
                    Edge(u=0, v=1, direction=Direction.RIGHT),
                    Edge(u=0, v=1, direction=Direction.SOUTH_EAST),
                ]
            )

            assert _sorted(graph.out_edges(1)) == _sorted(
                [
                    Edge(u=1, v=0, direction=Direction.LEFT),
                    Edge(u=1, v=0, direction=Direction.NORTH_WEST),
                    Edge(u=1, v=3, direction=Direction.SOUTH_EAST),
                    Edge(u=1, v=3, direction=Direction.SOUTH_WEST),
                ]
            )

            assert _sorted(graph.out_edges(2)) == _sorted(
                [
                    Edge(u=2, v=3, direction=Direction.RIGHT),
                    Edge(u=2, v=3, direction=Direction.NORTH_EAST),
                ]
            )

            assert _sorted(graph.out_edges(3)) == _sorted(
                [
                    Edge(u=3, v=2, direction=Direction.LEFT),
                    Edge(u=3, v=2, direction=Direction.SOUTH_WEST),
                    Edge(u=3, v=1, direction=Direction.NORTH_EAST),
                    Edge(u=3, v=1, direction=Direction.NORTH_WEST),
                ]
            )

            assert graph.edges_count == 12

        def it_raises_if_width_or_height_is_too_large(self):
            puzzle = SokobanPuzzle(Config.MAX_WIDTH + 1, 42)
            with pytest.raises(ValueError):
                BoardGraph(puzzle)

            puzzle = SokobanPuzzle(42, Config.MAX_HEIGHT + 1)
            with pytest.raises(ValueError):
                BoardGraph(puzzle)

            puzzle = SokobanPuzzle(Config.MAX_WIDTH + 1, Config.MAX_HEIGHT)
            with pytest.raises(ValueError):
                BoardGraph(puzzle)

    class describe_getitem:
        def it_returns_board_cell_on_position(self, board_graph):
            assert isinstance(board_graph[0], BoardCell)

        def it_raises_if_trying_to_get_invalid_position(self, board_graph):
            with pytest.raises(IndexError):
                board_graph[42000]

            with pytest.raises(IndexError):
                board_graph[-1]

    class describe_setitem:
        def it_sets_board_cell_on_position(self, board_graph):
            assert board_graph[0].is_empty_floor
            board_graph[0] = BoardCell(Puzzle.PUSHER)
            assert board_graph[0].has_pusher

        def it_sets_character_on_position(self, board_graph):
            assert board_graph[0].is_empty_floor
            board_graph[0] = Puzzle.PUSHER
            assert board_graph[0].has_pusher

        def it_doesnt_preserve_secondary_cell_flags_on_modified_cell(self, board_graph):
            board_graph[0].is_in_playable_area = True
            board_graph[0] = Puzzle.PUSHER
            assert not board_graph[0].is_in_playable_area

            board_graph[0].is_in_playable_area = True
            board_graph[0] = BoardCell(Puzzle.PUSHER)
            assert not board_graph[0].is_in_playable_area

        def it_raises_if_trying_to_set_invalid_cell_value(self, board_graph):
            illegal_cells = ["", None]
            for _ in illegal_cells:
                with pytest.raises(ValueError):
                    board_graph[0] = _

        def it_raises_if_trying_to_get_invalid_position(self, board_graph):
            with pytest.raises(IndexError):
                board_graph[42000] = " "

            with pytest.raises(IndexError):
                board_graph[-1] = " "

    class describe_contains:
        def it_detects_if_position_is_in_graph(self, board_graph):
            assert 0 in board_graph

        def it_doesnt_rise_if_checking_invalid_position_value(self, board_graph):
            assert 42000 not in board_graph
            assert -1 not in board_graph

    def it_provides_underlying_tessellation(self, board_graph):
        assert board_graph.tessellation == Tessellation.SOKOBAN

    def it_provides_number_of_graph_edges(self, board_graph):
        assert board_graph.edges_count == 776

    def it_provides_graph_size(self, puzzle, board_graph):
        assert board_graph.size == puzzle.width * puzzle.height

    def it_provides_width_of_underlying_board(self, puzzle, board_graph):
        assert board_graph.board_width == puzzle.width

    def it_provides_height_of_underlying_board(self, puzzle, board_graph):
        assert board_graph.board_height == puzzle.height

    class describe_neighbor:
        def it_returns_neighbor_position_in_given_direction(self, board_graph):
            assert board_graph.neighbor(0, Direction.RIGHT) == 1

        def it_returns_no_pos_if_direction_leads_off_board(self, board_graph):
            assert board_graph.neighbor(0, Direction.UP) == Config.NO_POS

        def it_raises_if_starting_position_is_off_board(self, board_graph):
            with pytest.raises(IndexError):
                board_graph.neighbor(42000, Direction.UP)

            with pytest.raises(IndexError):
                board_graph.neighbor(-1, Direction.UP)

    class describe_wall_neighbors:
        def it_returns_positions_of_walls_for_given_vertice(self):
            board_str = textwrap.dedent(
                """
                #######
                #.$# @#
                #######
                """
            )
            board_graph = BoardGraph(SokobanPuzzle(board=board_str))
            wall_neighbors = board_graph.wall_neighbors(0)

            assert index_1d(0, 1, 7) in wall_neighbors
            assert index_1d(1, 0, 7) in wall_neighbors

        def it_raises_if_starting_position_is_off_board(self, board_graph):
            with pytest.raises(IndexError):
                board_graph.wall_neighbors(42000)
            with pytest.raises(IndexError):
                board_graph.wall_neighbors(-1)

    class describe_all_neighbors:
        def it_returns_positions_of_all_neighbor_positions_for_given_vertice(
            self, board_graph
        ):
            all_neighbors = board_graph.all_neighbors(0)
            assert index_1d(0, 1, board_graph.board_width) in all_neighbors
            assert index_1d(1, 1, board_graph.board_width) not in all_neighbors
            assert index_1d(1, 0, board_graph.board_width) in all_neighbors

        def it_raises_if_starting_position_is_off_board(self, board_graph):
            with pytest.raises(IndexError):
                board_graph.all_neighbors(42000)
            with pytest.raises(IndexError):
                board_graph.all_neighbors(-1)

    class describe_shortest_path:
        def it_raises_if_any_of_positions_are_of_board(self, board_graph):
            with pytest.raises(IndexError):
                board_graph.shortest_path(1, 42000)
            with pytest.raises(IndexError):
                board_graph.shortest_path(42000, 1)
            with pytest.raises(IndexError):
                board_graph.shortest_path(1, -1)
            with pytest.raises(IndexError):
                board_graph.shortest_path(-1, 1)

    class describe_dijkstra_path:
        def it_raises_if_any_of_positions_are_of_board(self, board_graph):
            with pytest.raises(IndexError):
                board_graph.dijkstra_path(1, 42000)
            with pytest.raises(IndexError):
                board_graph.dijkstra_path(42000, 1)
            with pytest.raises(IndexError):
                board_graph.dijkstra_path(1, -1)
            with pytest.raises(IndexError):
                board_graph.dijkstra_path(-1, 1)

    class describe_find_jump_path:
        def it_returns_sequence_of_positions_defining_shortest_path_for_pusher_jump(
            self, board_graph
        ):
            start_position = index_1d(11, 8, board_graph.board_width)
            end_position = index_1d(8, 5, board_graph.board_width)
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

        def it_raises_if_any_of_positions_are_of_board(self, board_graph):
            with pytest.raises(IndexError):
                board_graph.find_jump_path(1, 42000)
            with pytest.raises(IndexError):
                board_graph.find_jump_path(42000, 1)
            with pytest.raises(IndexError):
                board_graph.find_jump_path(1, -1)
            with pytest.raises(IndexError):
                board_graph.find_jump_path(-1, 1)

    class describe_find_move_path:
        def it_returns_sequence_of_positions_defining_shortest_path_for_pusher_movement_without_pushing_boxes(
            self, board_graph
        ):
            start_position = index_1d(11, 8, board_graph.board_width)
            end_position = index_1d(8, 5, board_graph.board_width)
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

        def it_raises_if_any_of_positions_are_of_board(self, board_graph):
            with pytest.raises(IndexError):
                board_graph.find_move_path(1, 42000)
            with pytest.raises(IndexError):
                board_graph.find_move_path(42000, 1)
            with pytest.raises(IndexError):
                board_graph.find_move_path(1, -1)
            with pytest.raises(IndexError):
                board_graph.find_move_path(-1, 1)

        def it_returns_empty_sequence_if_movement_is_blocked(self, board_graph):
            assert (
                board_graph.find_move_path(index_1d(11, 8, board_graph.board_width), 0)
                == []
            )

    class describe_positions_path_to_directions_path:
        def it_converts_path(self, board_graph, positions_path, directions_path):
            calculated_directions_path = board_graph.positions_path_to_directions_path(
                positions_path
            )
            assert calculated_directions_path == directions_path

        def it_raises_if_any_of_positions_are_of_board(self, board_graph):
            with pytest.raises(IndexError):
                board_graph.positions_path_to_directions_path([42000])
            with pytest.raises(IndexError):
                board_graph.positions_path_to_directions_path([1, 42000])
            with pytest.raises(IndexError):
                board_graph.positions_path_to_directions_path([42000, 1])
            with pytest.raises(IndexError):
                board_graph.positions_path_to_directions_path([-1])
            with pytest.raises(IndexError):
                board_graph.positions_path_to_directions_path([1, -1])
            with pytest.raises(IndexError):
                board_graph.positions_path_to_directions_path([-1, 1])

        def it_returns_empty_path_if_source_path_is_to_short(self, board_graph):
            assert board_graph.positions_path_to_directions_path([]) == []
            assert board_graph.positions_path_to_directions_path([1]) == []

    class describe_mark_play_area:
        def it_calculates_playable_area_of_board_marking_all_playable_cells(self):
            board_str = textwrap.dedent(
                """
                #######
                #.$# @#
                #######
                #     #
                #######
                """
            )
            board_graph = BoardGraph(SokobanPuzzle(board=board_str))

            expected_playable_cells = [
                index_1d(1, 1, 7),
                index_1d(2, 1, 7),
                index_1d(4, 1, 7),
                index_1d(5, 1, 7),
            ]

            board_graph.mark_play_area()
            for pos in range(board_graph.size):
                if pos in expected_playable_cells:
                    assert board_graph[pos].is_in_playable_area
                else:
                    assert not board_graph[pos].is_in_playable_area

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
        board_graph = BoardGraph(SokobanPuzzle(board=board_str))

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

        def it_raises_if_start_position_is_off_board(self, board_graph):
            with pytest.raises(IndexError):
                board_graph.positions_reachable_by_pusher(42000)
            with pytest.raises(IndexError):
                board_graph.positions_reachable_by_pusher(-1)

        def it_ignores_off_board_positions_in_excluded_positions(self):
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
                -1,
                42000,
            ]
            assert (
                self.board_graph.positions_reachable_by_pusher(
                    pusher_position=index_1d(5, 1, 7), excluded_positions=excluded
                )
                == expected
            )

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
        board_graph = BoardGraph(SokobanPuzzle(board=board_str))

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

        def it_raises_if_start_position_is_off_board(self):
            with pytest.raises(IndexError):
                self.board_graph.normalized_pusher_position(42000)
            with pytest.raises(IndexError):
                self.board_graph.normalized_pusher_position(-1)

        def it_ignores_off_board_positions_in_excluded_positions(self):
            assert self.board_graph.normalized_pusher_position(
                pusher_position=index_1d(4, 1, 7),
                excluded_positions=[index_1d(1, 1, 7), -1, 42000],
            ) == index_1d(3, 1, 7)

    class describe_path_destination:
        def it_calculates_destination_position_from_source_and_directions_path(
            self, board_graph
        ):
            directions_path = [Direction.UP, Direction.RIGHT]
            start_position = index_1d(11, 8, board_graph.board_width)
            assert board_graph.path_destination(
                start_position, directions_path
            ) == index_1d(12, 7, board_graph.board_width)

        def it_silently_stops_search_on_first_off_board_position(self, board_graph):
            directions_path = [Direction.DOWN, Direction.DOWN, Direction.DOWN]
            start_position = index_1d(11, 8, board_graph.board_width)
            assert board_graph.path_destination(
                start_position, directions_path
            ) == index_1d(11, 10, board_graph.board_width)

        def it_silently_stops_search_on_illegal_direction(self, board_graph):
            directions_path = [Direction.DOWN, Direction.NORTH_WEST]
            start_position = index_1d(11, 8, board_graph.board_width)
            assert board_graph.path_destination(
                start_position, directions_path
            ) == index_1d(11, 9, board_graph.board_width)

        def it_raises_if_start_position_is_illegal_value(self, board_graph):
            with pytest.raises(IndexError):
                board_graph.path_destination(42000, [])

            with pytest.raises(IndexError):
                board_graph.path_destination(-1, [])

    # class describe__reachables:
    #     board = """
    #         #######
    #         #.$# @#
    #         #######
    #         #     #
    #         #######
    #     """
    #     board_graph = BoardGraph(SokobanPuzzle(board=board))

    #     def it_calculates_all_positions_reachable_from_root(self):
    #         root = index_1d(5, 1, 7)
    #         assert self.board_graph._reachables(root) == [root, index_1d(4, 1, 7)]

    #     def it_skips_explicitly_excluded_positions(self):
    #         root = index_1d(5, 1, 7)
    #         assert self.board_graph._reachables(root, excluded_positions=[root]) == [
    #             index_1d(4, 1, 7)
    #         ]
    #         root = index_1d(5, 1, 7)
    #         assert self.board_graph._reachables(
    #             root, excluded_positions=[index_1d(4, 1, 7)]
    #         ) == [root]
