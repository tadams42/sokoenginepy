from sokoenginepy.common import Direction
from sokoenginepy.tessellation import (BoardGraph, GraphType, SokobanBoard,
                                       index_1d)


class DescribeBoardGraph:

    class describe__has_edge:

        def it_returs_true_if_edge_in_given_direction_exists(
            self, sokoban_tessellation
        ):
            board_graph = BoardGraph(4, GraphType.DIRECTED)
            board_graph.reconfigure_edges(2, 2, sokoban_tessellation)
            assert board_graph.has_edge(0, 1, Direction.RIGHT)

    class describe__reconfigure_edges:

        def it_reconfigures_all_edges_in_board(self, sokoban_tessellation):
            board_graph = BoardGraph(4, GraphType.DIRECTED)
            board_graph.reconfigure_edges(2, 2, sokoban_tessellation)
            assert board_graph.edges_count() == 8
            assert board_graph.has_edge(0, 1, Direction.RIGHT)
            assert board_graph.has_edge(1, 0, Direction.LEFT)
            assert board_graph.has_edge(0, 2, Direction.DOWN)
            assert board_graph.has_edge(2, 0, Direction.UP)
            assert board_graph.has_edge(2, 3, Direction.RIGHT)
            assert board_graph.has_edge(3, 2, Direction.LEFT)
            assert board_graph.has_edge(1, 3, Direction.DOWN)
            assert board_graph.has_edge(3, 1, Direction.UP)

        def it_doesnt_create_duplicate_direction_edges_in_multidigraph(
            self, trioban_tessellation
        ):
            board_graph = BoardGraph(4, GraphType.DIRECTED_MULTI)
            board_graph.reconfigure_edges(2, 2, trioban_tessellation)
            assert board_graph.out_edges_count(0, 1) == 2
            assert board_graph.out_edges_count(1, 0) == 2

    class describe__out_edge_weight:

        def it_returns_max_weigth_for_wall_cell_target(self, board_graph):
            board_graph[1].is_wall = True
            assert board_graph.out_edge_weight(1) == BoardGraph.MAX_EDGE_WEIGHT

        def it_returns_max_weigth_for_pusher_cell_target(self, board_graph):
            board_graph[1].has_pusher = True
            assert board_graph.out_edge_weight(1) == BoardGraph.MAX_EDGE_WEIGHT

        def it_returns_max_weigth_for_box_cell_target(self, board_graph):
            board_graph[1].has_box = True
            assert board_graph.out_edge_weight(1) == BoardGraph.MAX_EDGE_WEIGHT

        def it_returns_one_for_other_cells(self, board_graph):
            board_graph[1].clear()
            assert board_graph.out_edge_weight(1) == 1
            board_graph[1].has_goal = True
            assert board_graph.out_edge_weight(1) == 1

    class describe__reachables:
        board_str = "\n".join([
            # 123456
            "#######",  # 0
            "#.$# @#",  # 1
            "#######",  # 2
            "#     #",  # 3
            "#######",  # 4
        ])
        board_graph = SokobanBoard(board_str=board_str)._graph

        def it_calculates_all_positions_reachable_from_root(self):
            root = index_1d(5, 1, 7)
            assert self.board_graph.reachables(root
                                              ) == [root, index_1d(4, 1, 7)]

        def it_skips_explicitly_excluded_positions(self):
            root = index_1d(5, 1, 7)
            assert self.board_graph.reachables(
                root, excluded_positions=[root]
            ) == [index_1d(4, 1, 7)]
            root = index_1d(5, 1, 7)
            assert self.board_graph.reachables(
                root, excluded_positions=[index_1d(4, 1, 7)]
            ) == [root]
