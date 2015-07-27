from collections import deque
from collections.abc import Container
from functools import wraps
import networkx as nx

from ..core import (
    PrettyPrintable, EqualityComparable, TessellationType, INDEX,
    Tessellated, Direction
)
from ..game import BoardCell
from ..io import (
    OutputSettings, rle_encode, is_blank, parse_board_string, RleCharacters
)


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


class VariantBoard(PrettyPrintable, EqualityComparable, Container, Tessellated):
    """
    Base board class for variant specific implementations.
    Implements concerns of
        - board cell access/editing
        - string (de)serialization
        - resizing
        - board-space searching

    All positions are int indexes of graph vertices. To convert 2D coordinate
    into vertice index, use INDEX method
    """

    def __init__(
        self, board_width=0, board_height=0,
        tessellation_type = TessellationType.SOKOBAN,
        board_str = ""
    ):
        super().__init__(tessellation_type)

        if not is_blank(board_str):
            board_cells = self._parse_string(board_str)
            width = len(board_cells[0]) if len(board_cells) > 0 else 0
            height = len(board_cells)
            self._reinit(board_width=width, board_height=height)
            for y, row in enumerate(board_cells):
                for x, chr in enumerate(row):
                    self[INDEX(x, y, self.width)] = BoardCell(chr)
        else:
            self._reinit(width=board_width, height=board_height)

    def _reinit(self, width, height):
        self._graph = self._tessellation.graph_type()

        if width <= 0 or height <= 0:
            self._width = 0
            self._height = 0
            self._are_edges_configured = True
        else:
            self._width = width
            self._height = height
            self._are_edges_configured = False

            for vertice in range(0, self.size):
                self._graph.add_node(vertice, cell=BoardCell())

            self._configure_edges()

    def _representation_attributes(self):
        return {
            'tessellation': self.tessellation_type,
            'width': self.width,
            'height': self.height,
            'board': self.to_s,
        }

    def __eq__(self, other):
        if (
            self.tessellation_type == other.tessellation_type and
            self.width == other.width and
            self.height == other.height
        ):
            for vertice in range(0, self.size):
                if self[vertice] != other[vertice]:
                    return False
            return True
        else:
            return False

    def _parse_string(self, board_str):
        """
        Override this in subclass to handle tessellation speciffic strings
        Should return list of strings where each string represents all BoardCell
        in single line of game board.
        """
        return parse_board_string(board_str)

    @normalize_index_errors
    def __getitem__(self, position):
        return self._graph.node[position]['cell']

    @normalize_index_errors
    def __setitem__(self, position, board_cell):
        self._graph.node[position]['cell'] = board_cell

    def __contains__(self, position):
        return position in self._graph

    def _copy_graph_without_edges(self):
        retv = nx.create_empty_copy(self._graph, with_nodes=True)
        for vertice in self._graph.nodes_iter():
            retv.node[vertice]['cell'] = self._graph.node[vertice]['cell']
        return retv

    def to_s(self, output_settings = OutputSettings()):
        """
        Override this in subclass to handle tessellation speciffic strings
        """
        rows = []
        for y in range(0, self.height):
            row = "".join([
                cell.to_s(output_settings.use_visible_floors)
                for cell in [
                    self._graph.node[INDEX(x, y, self.width)]['cell']
                    for x in range(0, self.width)
                ]
            ])
            if output_settings.rle_encode:
                row = rle_encode(row)
            rows.append(row)

        if output_settings.rle_encode:
            return RleCharacters.RLE_ROW_SEPARATOR.value.join(rows)
        else:
            return "\n".join(rows)

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
            # edge: (source, target, data)
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
                if neighbor_vertice is not None:
                    # and not self._has_edge(source_vertice, neighbor_vertice, direction)
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
            for out_edge in self._graph.out_edges_iter(source_vertice, data=True):
                out_edge[2]['weight'] = self._out_edge_weight(out_edge)

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

    def _debug_draw_positions(self, positions):
        tmp = self._graph.copy()
        for vertice in positions:
            self[vertice] = BoardCell('@')
        print(self.to_s(OutputSettings(use_visible_floors=True)))
        self._graph = tmp

    def add_row_top(self):
        old_body = self._graph
        old_height = self.height

        self._reinit(self.width, self.height + 1)

        for x in range(0, self.width):
            for y in range(0, old_height):
                self._graph.node[INDEX(x, y + 1, self.width)]['cell'] =\
                    old_body.node[INDEX(x, y, self.width)]['cell']

    def add_row_bottom(self):
        old_body = self._graph
        old_height = self.height

        self._reinit(self.width, self.height + 1)

        for x in range(0, self.width):
            for y in range(0, old_height):
                self._graph.node[INDEX(x, y, self.width)]['cell'] =\
                    old_body.node[INDEX(x, y, self.width)]['cell']

    def add_column_left(self):
        old_body = self._graph
        old_width = self.width

        self._reinit(self.width + 1, self.height)

        for x in range(0, old_width):
            for y in range(0, self.height):
                self._graph.node[INDEX(x + 1, y, self.width)]['cell'] =\
                    old_body.node[INDEX(x, y, old_width)]['cell']

    def add_column_right(self):
        old_body = self._graph
        old_width = self.width

        self._reinit(self.width + 1, self.height)

        for x in range(0, old_width):
            for y in range(0, self.height):
                self._graph.node[INDEX(x, y, self.width)]['cell'] =\
                    old_body.node[INDEX(x, y, old_width)]['cell']

    def remove_row_top(self):
        old_body = self._graph

        self._reinit(self.width, self.height - 1)

        for x in range(0, self.width):
            for y in range(0, self.height):
                self._graph.node[INDEX(x, y, self.width)]['cell'] =\
                    old_body.node[INDEX(x, y + 1, self.width)]['cell']

    def remove_row_bottom(self):
        old_body = self._graph

        self._reinit(self.width, self.height - 1)

        for x in range(0, self.width):
            for y in range(0, self.height):
                self._graph.node[INDEX(x, y, self.width)]['cell'] =\
                    old_body.node[INDEX(x, y, self.width)]['cell']

    def remove_column_left(self):
        old_body = self._graph
        old_width = self.width

        self._reinit(self.width - 1, self.height)

        for x in range(0, self.width):
            for y in range(0, self.height):
                self._graph.node[INDEX(x, y, self.width)]['cell'] =\
                    old_body.node[INDEX(x + 1, y, old_width)]['cell']

    def remove_column_right(self):
        old_body = self._graph
        old_width = self.width

        self._reinit(self.width - 1, self.height)

        for x in range(0, self.width):
            for y in range(0, self.height):
                self._graph.node[INDEX(x, y, self.width)]['cell'] =\
                    old_body.node[INDEX(x, y, old_width)]['cell']

    def resize(self, new_width, new_height):
        if new_height != self.height:
            if new_height > self.height:
                amount = new_height - self.height
                for i in range(0, amount):
                    self.add_row_bottom()
            else:
                amount = self.height - new_height
                for i in range(0, amount):
                    self.remove_row_bottom()

        if new_width != self.width:
            if new_width > self.width:
                amount = new_width - self.width
                for i in range(0, amount):
                    self.add_column_right()
            else:
                amount = self.width - new_width
                for i in range(0, amount):
                    self.remove_column_right()

    def trim(self):
        self.trim_top()
        self.trim_bottom()
        self.trim_left()
        self.trim_right()

    def trim_left(self):
        amount = self.width
        for y in range(0, self.height):
            border_found = False
            for x in range(0, self.width):
                border_found = self[INDEX(x, y, self.width)].is_border_element
                if border_found:
                    if x < amount:
                        amount = x
                    break

        for i in range(0, amount):
            self.remove_column_left()

    def trim_right(self):
        self.reverse_columns()
        self.trim_left()
        self.reverse_columns()

    def trim_top(self):
        amount = self.height
        for x in range(0, self.width):
            border_found = False
            for y in range(0, self.height):
                border_found = self[INDEX(x, y, self.width)].is_border_element
                if border_found:
                    if y < amount:
                        amount = y
                    break

        for i in range(0, amount):
            self.remove_row_top()

    def trim_bottom(self):
        self.reverse_rows()
        self.trim_top()
        self.reverse_rows()

    def reverse_rows(self):
        old_body = self._graph

        self._reinit(self.width, self.height)

        for x in range(0, self.width):
            for y in range(0, self.height):
                self[INDEX(x, y, self.width)] = \
                    old_body.node[INDEX(x, self.height - y - 1, self.width)]['cell']

    def reverse_columns(self):
        old_body = self._graph

        self._reinit(self.width, self.height)

        for x in range(0, self.width):
            for y in range(0, self.height):
                self[INDEX(x, y, self.width)] = \
                    old_body.node[INDEX(self.width - x - 1, y, self.width)]['cell']
