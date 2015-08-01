from sokoenginepy import (
    Variant, BoardConversionError, Direction, index_1d, IllegalDirectionError
)
from sokoenginepy.variant import BoardGraph, GraphType, SokobanBoard
from hamcrest import assert_that, equal_to


class DescribeBoardGraph(object):
    class describe__has_edge(object):
        def test_true_if_edge_in_given_direction_exists(
            self, sokoban_tessellation
        ):
            board_graph = BoardGraph(4, GraphType.DIRECTED)
            board_graph.reconfigure_edges(2, 2, sokoban_tessellation)
            assert_that(
                board_graph.has_edge(0, 1, Direction.RIGHT),
                equal_to(True)
            )

    class describe__reconfigure_edges(object):
        def test_reconfigures_all_edges_in_board(
            self, sokoban_tessellation
        ):
            board_graph = BoardGraph(4, GraphType.DIRECTED)
            board_graph.reconfigure_edges(2, 2, sokoban_tessellation)

            assert_that(board_graph.edges_count(), equal_to(8))
            assert_that(
                board_graph.has_edge(0, 1, Direction.RIGHT), equal_to(True)
            )
            assert_that(
                board_graph.has_edge(1, 0, Direction.LEFT), equal_to(True)
            )
            assert_that(
                board_graph.has_edge(0, 2, Direction.DOWN), equal_to(True)
            )
            assert_that(
                board_graph.has_edge(2, 0, Direction.UP), equal_to(True)
            )
            assert_that(
                board_graph.has_edge(2, 3, Direction.RIGHT), equal_to(True)
            )
            assert_that(
                board_graph.has_edge(3, 2, Direction.LEFT), equal_to(True)
            )
            assert_that(
                board_graph.has_edge(1, 3, Direction.DOWN), equal_to(True)
            )
            assert_that(
                board_graph.has_edge(3, 1, Direction.UP), equal_to(True)
            )

        def test_doesnt_create_duplicate_direction_edges_in_multidigraph(
            self, trioban_tessellation
        ):
            board_graph = BoardGraph(4, GraphType.DIRECTED_MULTI)
            board_graph.reconfigure_edges(2, 2, trioban_tessellation)

            assert_that(len(board_graph._graph[0][1]), equal_to(2))
            assert_that(len(board_graph._graph[1][0]), equal_to(2))

    class describe__out_edge_weight(object):
        def test_returns_max_weigth_for_wall_cell_target(self, board_graph):
            board_graph[1].is_wall = True
            assert_that(
                board_graph.out_edge_weight([0, 1]),
                equal_to(BoardGraph.MAX_EDGE_WEIGHT)
            )

        def test_returns_max_weigth_for_pusher_cell_target(self, board_graph):
            board_graph[1].has_pusher = True
            assert_that(
                board_graph.out_edge_weight([0, 1]),
                equal_to(BoardGraph.MAX_EDGE_WEIGHT)
            )

        def test_returns_max_weigth_for_box_cell_target(self, board_graph):
            board_graph[1].has_box = True
            assert_that(
                board_graph.out_edge_weight([0, 1]),
                equal_to(BoardGraph.MAX_EDGE_WEIGHT)
            )

        def test_returns_one_for_other_cells(self, board_graph):
            board_graph[1].clear()
            assert_that(board_graph.out_edge_weight([0, 1]), equal_to(1))
            board_graph[1].has_goal = True
            assert_that(board_graph.out_edge_weight([0, 1]), equal_to(1))

    class describe__reachables(object):
        board_str = "\n".join([
            # 123456
            "#######",  # 0
            "#.$# @#",  # 1
            "#######",  # 2
            "#     #",  # 3
            "#######",  # 4
        ])
        board_graph = SokobanBoard(board_str=board_str)._graph

        def test_calculates_all_positions_reachable_from_root(self):
            root = index_1d(5, 1, 7)
            assert_that(
                self.board_graph.reachables(root),
                equal_to([
                    root, index_1d(4, 1, 7)
                ])
            )

        def test_skips_explicitly_excluded_positions(self):
            root = index_1d(5, 1, 7)
            assert_that(
                self.board_graph.reachables(root, excluded_positions=[root]),
                equal_to([index_1d(4, 1, 7)])
            )

            root = index_1d(5, 1, 7)
            assert_that(
                self.board_graph.reachables(root, excluded_positions=[index_1d(4, 1, 7)]),
                equal_to([root])
            )
