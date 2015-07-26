from collections import deque
from collections.abc import Container
from functools import wraps
import networkx as nx

from ..core import Tessellated, Direction
from ..game import BoardCell


def normalize_index_errors(method):
    """
    Normalizes NetworkX index out of range errors into IndexError
    """
    @wraps(method)
    def method_wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except IndexError:
            raise IndexError('Board index out of range')
        except KeyError:
            raise IndexError('Board index out of range')
        except nx.NetworkXError:
            raise IndexError('Board index out of range')
    return method_wrapper


class BoardGraph(Container, Tessellated):
    """
    Implements board graph representation, vertice/edge management and board
    space searching. Works for any tessellation.

    All positions are int indexes of graph vertices. To convert 2D coordinate
    into vertice index, use INDEX method
    """

    def __init__(self, board_width, board_height, tessellation_type):
        super().__init__(tessellation_type)
        self._graph = self._tessellation.graph_type()
        self._width = board_width
        self._height = board_height
        self._are_edges_configured = False

        for vertice in range(0, self.size):
            self._graph.add_node(vertice, cell=BoardCell())
        self._configure_edges()

    @normalize_index_errors
    def __getitem__(self, position):
        return self._graph.node[position]['cell']

    @normalize_index_errors
    def __setitem__(self, position, board_cell):
        self._graph.node[position]['cell'] = board_cell

    def __contains__(self, position):
        """
        Checks if position is on board
        """
        return position in self._graph

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def size(self):
        return self._width * self._height

    def _has_edge(self, source_vertice, dest_vertice, direction):
        """
        Checks if there is edge between source_vertice and dest_vertice in given
        direction
        """
        retv = False

        for out_edge in self._graph.out_edges_iter(source_vertice, data=True):
            retv = retv or (
                out_edge[1] == dest_vertice and
                out_edge[2]['direction'] == direction
            )

        return retv

    def _configure_edges(self):
        """
        Uses tessellation object to create all edges in graph.
        """
        if self._are_edges_configured:
            return

        for source_vertice in self._graph.nodes_iter():
            for direction in self._tessellation.legal_directions:
                neighbor_vertice = self._tessellation.neighbor_position(
                    source_vertice, direction,
                    board_width=self._width, board_height=self._height
                )
                if (
                    neighbor_vertice is not None and
                    not self._has_edge(source_vertice, neighbor_vertice, direction)
                ):
                    self._graph.add_edge(
                        source_vertice, neighbor_vertice, direction=direction
                    )

        self._are_edges_configured = True

    def _out_edge_weight(self, edge):
        """
        Calculates weight of single edge dependng on contents of its vertices.
        """
        target_vertice = edge[1]
        target_cell = self._graph.node[target_vertice]['cell']

        weight = 1
        if (target_cell.is_deadlock or target_cell.is_wall or
                target_cell.has_box or target_cell.has_pusher):
            weight = len(Direction) + 1

        return weight

    def _calculate_edge_weights(self):
        """
        Calculates and sets weights to all edges in board graph.
        """
        self._configure_edges()
        for source_vertice in self._graph.nodes_iter():
            for out_edge in self._graph.out_edges_iter(source_vertice):
                weight = self._out_edge_weight(out_edge)

                target_vertice = out_edge[1]
                if self._graph.is_multigraph():
                    for edge_key in self._graph[source_vertice][target_vertice].keys():
                        self._graph[source_vertice][target_vertice][edge_key]['weight'] = weight
                else:
                    self._graph[source_vertice][target_vertice]['weight'] = weight

    @normalize_index_errors
    def _reachables(
        self, root, excluded_positions=[], is_obstacle_callable=None,
        add_animation_frame_hook=None
    ):
        """
        Returns list of all positions reachable from root

        excluded_positions - these positions will be marked as unreachable
            without calculating their status
        is_obstacle_callable - callable that checks if given position on graph
            is obstacle
        add_animation_frame_hook - if not None, this callable will be caled
            after each step oof search. Usefull for visualization of algorithm
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

        return reachables

    @normalize_index_errors
    def neighbor(self, from_position, direction):
        for out_edge in self._graph.out_edges_iter(from_position, data=True):
            if out_edge[2]['direction'] == direction:
                return out_edge[1]
        return None

    @normalize_index_errors
    def wall_neighbors(self, from_position):
        return [
            n for n in self._graph.neighbors_iter(from_position)
            if self[n].is_wall
        ]

    @normalize_index_errors
    def all_neighbors(self, from_position):
        return self._graph.neighbors(from_position)

    def clear(self):
        for node in self._graph.nodes_iter():
            self._graph.node[node]['cell'].clear()

    def mark_play_area(self):
        for node in self._graph.nodes_iter():
            self._graph.node[node]['cell'].is_in_playable_area = False

        def is_obstacle(vertice):
            return (
                self._graph.node[vertice]['cell'].is_wall or
                self._graph.node[vertice]['cell'].is_in_playable_area
            )

        marked = []
        for vertice in self._graph.nodes_iter():
            cell = self._graph.node[vertice]['cell']
            should_analyze = not cell.is_in_playable_area and cell.has_piece

            if should_analyze:
                reachables = self._reachables(
                    root=vertice, excluded_positions=marked,
                    is_obstacle_callable=is_obstacle
                )
                for reachable_vertice in reachables:
                    reachable_cell = self._graph.node[reachable_vertice]['cell']
                    if reachable_cell.has_piece or reachable_vertice == vertice:
                        reachable_cell.is_in_playable_area = True
                        marked.append(reachable_vertice)

    @normalize_index_errors
    def positions_reachable_by_pusher(
        self, pusher_position, excluded_positions=[]
    ):
        def is_obstacle(position):
            return self._graph[position]['cell'].can_put_pusher_or_box
        return self._reachables(
            pusher_position,
            is_obstacle_callable=is_obstacle,
            excluded_positions=excluded_positions
        )

    @normalize_index_errors
    def normalized_pusher_position(self, pusher_position, excluded_positions=[]):
        reachables = self.positions_reachable_by_pusher(
            pusher_position=pusher_position,
            excluded_positions=excluded_positions
        )
        if reachables:
            return min(reachables)
        else:
            return pusher_position

    @normalize_index_errors
    def path_destination(self, start_position, path):
        retv = start_position
        for direction in path:
            next_target = self.neighbor(retv, direction)
            if next_target:
                retv = next_target
            else:
                break
        return retv

    def find_jump_path(self, start_position, end_position):
        if start_position not in self or end_position not in self:
            raise IndexError('Board index out of range')
        try:
            return nx.shortest_path(self._graph, start_position, end_position, 1)
        except nx.NetworkXNoPath:
            return []

    def find_move_path(self, start_position, end_position):
        if start_position not in self or end_position not in self:
            raise IndexError('Board index out of range')

        self._calculate_edge_weights()
        try:
            return nx.dijkstra_path(self._graph, start_position, end_position)
        except nx.NetworkXNoPath:
            return []

    def cell_orientation(self, cell_position):
        if not cell_position in self:
            raise IndexError('Board index out of range')
        return self._tessellation.cell_orientation(
            cell_position, self._width, self._height
        )

    @normalize_index_errors
    def position_path_to_direction_path(self, position_path):
        retv = []
        src_vertice_index = 0
        for dest_vertice in position_path[1:]:
            src_vertice = position_path[src_vertice_index]
            src_vertice_index += 1

            for out_edge in self._graph.out_edges_iter(src_vertice, data=True):
                if out_edge[1] == dest_vertice:
                    retv.append(out_edge[2]['direction'])

        return {
            'source_position': position_path[0] if position_path else None,
            'path': retv
        }

    @classmethod
    def _debug_animate_board_graph_reachables(cls, output_gif_path="/tmp/reachables.gif"):
        import numpy as np
        from moviepy.editor import ImageSequenceClip
        from functools import partial
        from ..core import INDEX, X, Y, TessellationType
        from ..io import parse_board_string

        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        GRAY = (128, 128, 128)
        RED = (255, 0, 0)
        GREEN = (0, 255, 0)

        animation_frames = []

        board_str = "\n".join([
            # 123456789012345678
            "    #####",            # 0
            "    #   #",            # 1
            "    #$  #",            # 2
            "  ###  $##",           # 3
            "  #  $ $ #",           # 4
            "### # ## #   ######",  # 5
            "#   # ## #####  ..#",  # 6
            "# $  $          ..#",  # 7
            "##### ### #@##  ..#",  # 8
            "    #     #########",  # 9
            "    #######",          # 10
        ])
        board_cells = parse_board_string(board_str)
        width = len(board_cells[0])
        height = len(board_cells)
        root = INDEX(11, 8, width)
        bg = cls(board_width=width, board_height=height,
                 tessellation_type=TessellationType.SOKOBAN)

        for y, row in enumerate(board_cells):
            for x, chr in enumerate(row):
                bg[INDEX(x, y, bg.width)] = BoardCell(chr)

        def add_animation_frame(
            current_position, reachables, to_inspect, excluded, frames, width, height
        ):
            row_data = width * [WHITE]
            matrix = np.array(height * [row_data])

            for i in reachables:
                x, y = X(i, width), Y(i, width)
                matrix[y, x] = GREEN

            for i in to_inspect:
                x, y = X(i, width), Y(i, width)
                matrix[y, x] = GRAY

            for i in excluded:
                x, y = X(i, width), Y(i, width)
                matrix[y, x] = BLACK

            x, y = X(current_position, width), Y(current_position, width)
            matrix[y, x] = RED

            frames.append(matrix)

        bg._reachables(
            root,
            add_animation_frame_hook=partial(
                add_animation_frame,
                width=width, height=height, frames=animation_frames
            )
        )

        animation = ImageSequenceClip(animation_frames, fps=2)
        animation.write_gif(output_gif_path)
