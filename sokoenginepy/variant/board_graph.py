from enum import Enum
import networkx as nx
from collections import deque

from ..game import BoardCell
from ..core import Direction


class GraphType(Enum):
    DIRECTED = 0
    DIRECTED_MULTI = 1


class BoardGraph(object):
    MAX_EDGE_WEIGHT = len(Direction) + 1

    def __init__(self, number_of_vertices, graph_type):
        assert graph_type in GraphType

        if graph_type == GraphType.DIRECTED:
            self._graph = nx.DiGraph()
        else:
            self._graph = nx.MultiDiGraph()

        for vertice in range(0, number_of_vertices):
            self._graph.add_node(vertice, cell=BoardCell())

    def __getitem__(self, position):
        return self._graph.node[position]['cell']

    def __setitem__(self, position, board_cell):
        self._graph.node[position]['cell'] = board_cell

    def __contains__(self, position):
        return position in self._graph

    def vertices_count(self):
        return self._graph.number_of_nodes()

    def edges_count(self):
        return self._graph.number_of_edges()

    def has_edge(self, source_vertice, target_vertice, direction):
        """
        Checks if there is edge between source_vertice and target_vertice in given
        direction
        """
        retv = False

        for out_edge in self._graph.out_edges_iter(source_vertice, data=True):
            # edge: (source, target, data_dict)
            retv = retv or (
                out_edge[1] == target_vertice and
                out_edge[2]['direction'] == direction
            )

        return retv

    def reconfigure_edges(self, width, height, tessellation):
        """
        Uses tessellation object to create all edges in graph.
        """
        self._graph.remove_edges_from(self._graph.edges())
        for source_vertice in self._graph.nodes_iter():
            for direction in tessellation.legal_directions:
                neighbor_vertice = tessellation.neighbor_position(
                    source_vertice, direction,
                    board_width=width, board_height=height
                )
                if neighbor_vertice is not None:
                    self._graph.add_edge(
                        source_vertice, neighbor_vertice, direction=direction
                    )

    def out_edge_weight(self, edge):
        """
        Calculates weight of single edge dependng on contents of its vertices.
        """
        target_vertice = edge[1]
        target_cell = self._graph.node[target_vertice]['cell']

        weight = 1
        if (target_cell.is_wall or target_cell.has_box or
                target_cell.has_pusher):
            weight = type(self).MAX_EDGE_WEIGHT

        return weight

    def calculate_edge_weights(self):
        """
        Calculates and sets weights to all edges in board graph.
        """
        for edge in self._graph.edges_iter(data=True):
            edge[2]['weight'] = self.out_edge_weight(edge)

    def reachables(
        self, root, excluded_positions=[], is_obstacle_callable=None,
        add_animation_frame_hook=None
    ):
        """
        Returns list of all positions reachable from root

        excluded_positions - these positions will be marked as unreachable
            without calculating their status
        is_obstacle_callable - callable that checks if given position on graph
            is obstacle
        add_animation_frame_hook - if not None, this callable will be called
            after each step oof search. Useful for visualization of algorithm
            and debugging
        """
        visited = len(self._graph) * [False]
        visited[root] = True
        reachables = deque()
        to_inspect = deque([root])

        if is_obstacle_callable is None:
            is_obstacle_callable = (
                lambda x: not self._graph.node[x]['cell'].can_put_pusher_or_box
            )

        while len(to_inspect) > 0:
            current_position = to_inspect.popleft()

            if (current_position == root or
                    current_position not in excluded_positions):
                reachables.append(current_position)

            for neighbor in self._graph.neighbors(current_position):
                if not visited[neighbor]:
                    if not is_obstacle_callable(neighbor):
                        to_inspect.append(neighbor)
                    visited[neighbor] = True

            if add_animation_frame_hook is not None:
                add_animation_frame_hook(
                    current_position=current_position,
                    reachables=reachables,
                    to_inspect=to_inspect,
                    excluded=excluded_positions
                )

        if root in excluded_positions:
            return [pos for pos in reachables if pos != root]
        else:
            return list(reachables)

    def neighbor(self, from_position, direction):
        for out_edge in self._graph.out_edges_iter(from_position, data=True):
            # edge: (source, target, data_dict)
            if out_edge[2]['direction'] == direction:
                return out_edge[1]
        return None

    def wall_neighbors(self, from_position):
        return [
            n for n in self._graph.neighbors_iter(from_position)
            if self[n].is_wall
        ]

    def all_neighbors(self, from_position):
        return self._graph.neighbors(from_position)

    def shortest_path(self, start_position, end_position):
        try:
            return nx.shortest_path(self._graph, start_position, end_position, 1)
        except nx.NetworkXNoPath:
            return []

    def dijkstra_path(self, start_position, end_position):
        self.calculate_edge_weights()
        try:
            return nx.dijkstra_path(self._graph, start_position, end_position)
        except nx.NetworkXNoPath:
            return []

    def position_path_to_direction_path(self, position_path):
        retv = []
        src_vertice_index = 0
        for target_vertice in position_path[1:]:
            src_vertice = position_path[src_vertice_index]
            src_vertice_index += 1

            for out_edge in self._graph.out_edges_iter(src_vertice, data=True):
                if out_edge[1] == target_vertice:
                    retv.append(out_edge[2]['direction'])

        return {
            'source_position': position_path[0] if position_path else None,
            'path': retv
        }

    # @classmethod
    # def _debug_animate_board_graph_reachables(cls, output_gif_path="/tmp/reachables.gif"):
    #     import numpy as np
    #     from moviepy.editor import ImageSequenceClip
    #     from functools import partial
    #     from ..core import index_1d, X, Y, Tessellation
    #     from ..io import parse_board_string

    #     WHITE = (255, 255, 255)
    #     BLACK = (0, 0, 0)
    #     GRAY = (128, 128, 128)
    #     RED = (255, 0, 0)
    #     GREEN = (0, 255, 0)

    #     animation_frames = []

    #     board_str = "\n".join([
    #         # 123456789012345678
    #         "    #####",            # 0
    #         "    #   #",            # 1
    #         "    #$  #",            # 2
    #         "  ###  $##",           # 3
    #         "  #  $ $ #",           # 4
    #         "### # ## #   ######",  # 5
    #         "#   # ## #####  ..#",  # 6
    #         "# $  $          ..#",  # 7
    #         "##### ### #@##  ..#",  # 8
    #         "    #     #########",  # 9
    #         "    #######",          # 10
    #     ])
    #     board_cells = parse_board_string(board_str)
    #     width = 19
    #     height = 11
    #     root = index_1d(11, 8, width)
    #     bg = BoardGraph(width * height, GraphType.DIRECTED)
    #     bg.reconfigure_edges(width, height, Tessellation.factory('sokoban'))

    #     for y, row in enumerate(board_cells):
    #         for x, chr in enumerate(row):
    #             bg[index_1d(x, y, width)] = BoardCell(chr)

    #     def add_animation_frame(
    #         current_position, reachables, to_inspect, excluded, frames, width, height
    #     ):
    #         row_data = width * [WHITE]
    #         matrix = np.array(height * [row_data])

    #         for i in reachables:
    #             x, y = X(i, width), Y(i, width)
    #             matrix[y, x] = GREEN

    #         for i in to_inspect:
    #             x, y = X(i, width), Y(i, width)
    #             matrix[y, x] = GRAY

    #         for i in excluded:
    #             x, y = X(i, width), Y(i, width)
    #             matrix[y, x] = BLACK

    #         x, y = X(current_position, width), Y(current_position, width)
    #         matrix[y, x] = RED

    #         frames.append(matrix)

    #     bg.reachables(
    #         root,
    #         add_animation_frame_hook=partial(
    #             add_animation_frame,
    #             width=width, height=height, frames=animation_frames
    #         )
    #     )

    #     animation = ImageSequenceClip(animation_frames, fps=2)
    #     animation.write_gif(output_gif_path)
