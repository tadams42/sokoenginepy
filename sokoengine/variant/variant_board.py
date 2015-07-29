from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Container
from functools import wraps
import networkx as nx

from ..core import (
    PrettyPrintable, EqualityComparable, Variant, INDEX,
    Tessellated, Direction, IllegalDirectionError
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


class VariantBoard(
    PrettyPrintable, EqualityComparable, Container, Tessellated, ABC
):
    """
    Base board class for variant specific implementations.
    Internally it is stored as directed graph structure.

    Implements concerns of
        - board cell access/editing
        - string (de)serialization
        - resizing
        - board-space searching

    All positions are int indexes of graph vertices. To convert 2D coordinate
    into vertice index, use INDEX method
    """

    _MAX_EDGE_WEIGHT = len(Direction) + 1

    def __init__(
        self, board_width=0, board_height=0,
        variant = Variant.SOKOBAN,
        board_str = ""
    ):
        super().__init__(variant)

        if not is_blank(board_str):
            board_rows = self._parse_string(board_str)
            width = len(board_rows[0]) if len(board_rows) > 0 else 0
            height = len(board_rows)
            self._reinit(width, height)
            for y, row in enumerate(board_rows):
                for x, chr in enumerate(row):
                    self[INDEX(x, y, self.width)] = BoardCell(chr)
        else:
            self._reinit(board_width, board_height)

    def _reinit(self, width, height, reconfigure_edges=True):
        self._graph = self.tessellation.graph_type()

        if width <= 0 or height <= 0:
            self._width = 0
            self._height = 0
        else:
            self._width = width
            self._height = height

        for vertice in range(0, self.size):
            self._graph.add_node(vertice, cell=BoardCell())

        if reconfigure_edges:
            self._reconfigure_edges()

    def _representation_attributes(self):
        return {
            'tessellation': self.variant,
            'width': self.width,
            'height': self.height,
            'board': self.to_s,
        }

    def __eq__(self, other):
        if (
            self.variant == other.variant and
            self.width == other.width and
            self.height == other.height
        ):
            for vertice in range(0, self.size):
                if self[vertice] != other[vertice]:
                    return False
            return True
        else:
            return False

    @abstractmethod
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

    @abstractmethod
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
            row = row.rstrip()
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

    def _has_edge(self, source_vertice, target_vertice, direction):
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

    def _reconfigure_edges(self):
        """
        Uses tessellation object to create all edges in graph.
        """
        self._graph.remove_edges_from(self._graph.edges())
        for source_vertice in self._graph.nodes_iter():
            for direction in self.tessellation.legal_directions:
                neighbor_vertice = self.tessellation.neighbor_position(
                    source_vertice, direction,
                    board_width=self._width, board_height=self._height
                )
                if neighbor_vertice is not None:
                    self._graph.add_edge(
                        source_vertice, neighbor_vertice, direction=direction
                    )

    def _out_edge_weight(self, edge):
        """
        Calculates weight of single edge dependng on contents of its vertices.
        """
        target_vertice = edge[1]
        target_cell = self._graph.node[target_vertice]['cell']

        weight = 1
        if (target_cell.is_wall or target_cell.has_box or
                target_cell.has_pusher):
            weight = type(self)._MAX_EDGE_WEIGHT

        return weight

    def _calculate_edge_weights(self):
        """
        Calculates and sets weights to all edges in board graph.
        """
        for edge in self._graph.edges_iter(data=True):
            edge[2]['weight'] = self._out_edge_weight(edge)

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

        if root in excluded_positions:
            return [pos for pos in reachables if pos != root]
        else:
            return list(reachables)

    @normalize_index_errors
    def neighbor(self, from_position, direction):
        for out_edge in self._graph.out_edges_iter(from_position, data=True):
            # edge: (source, target, data_dict)
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
        """
        Empties all board cells.
        """
        for node in self._graph.nodes_iter():
            self._graph.node[node]['cell'].clear()

    def mark_play_area(self):
        piece_positions = []
        for vertice in self._graph.nodes_iter():
            if self[vertice].has_box or self[vertice].has_pusher:
                self[vertice].is_in_playable_area = True
                piece_positions.append(vertice)
            else:
                self[vertice].is_in_playable_area = False

        def is_obstacle(vertice):
            return self[vertice].is_wall

        for piece_position in piece_positions:
            reachables = self._reachables(
                root=piece_position, is_obstacle_callable=is_obstacle
            )

            for reachable_vertice in reachables:
                self[reachable_vertice].is_in_playable_area = True

    @normalize_index_errors
    def positions_reachable_by_pusher(
        self, pusher_position, excluded_positions=[]
    ):
        def is_obstacle(position):
            return not self[position].can_put_pusher_or_box
        return self._reachables(
            root=pusher_position,
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
    def path_destination(self, start_position, direction_path):
        if start_position not in self:
            raise IndexError('Board index out of range')

        retv = start_position
        for direction in direction_path:
            next_target = self.neighbor(retv, direction)
            if next_target:
                retv = next_target
            else:
                break
        return retv

    def find_jump_path(self, start_position, end_position):
        if start_position not in self:
            raise IndexError('Board index out of range')
        try:
            return nx.shortest_path(self._graph, start_position, end_position, 1)
        except nx.NetworkXNoPath:
            return []

    def find_move_path(self, start_position, end_position):
        if start_position not in self:
            raise IndexError('Board index out of range')

        self._calculate_edge_weights()
        try:
            path = nx.dijkstra_path(self._graph, start_position, end_position)
            retv = path[:1]
            for position in path[1:]:
                if self[position].can_put_pusher_or_box:
                    retv.append(position)
                else:
                    break
            if retv != path:
                return[]
            return path
        except nx.NetworkXNoPath:
            return []

    def cell_orientation(self, position):
        return self.tessellation.cell_orientation(
            position, self._width, self._height
        )

    @normalize_index_errors
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

    @classmethod
    def _debug_animate_board_graph_reachables(cls, output_gif_path="/tmp/reachables.gif"):
        import numpy as np
        from moviepy.editor import ImageSequenceClip
        from functools import partial
        from ..core import INDEX, X, Y, Variant
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
                 variant=Variant.SOKOBAN)

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
        resizer = self.tessellation.board_resizer_type(self)
        resizer.add_row_top(reconfigure_edges=True)

    def add_row_bottom(self):
        resizer = self.tessellation.board_resizer_type(self)
        resizer.add_row_bottom(reconfigure_edges=True)

    def add_column_left(self):
        resizer = self.tessellation.board_resizer_type(self)
        resizer.add_column_left(reconfigure_edges=True)

    def add_column_right(self):
        resizer = self.tessellation.board_resizer_type(self)
        resizer.add_column_right(reconfigure_edges=True)

    def remove_row_top(self):
        resizer = self.tessellation.board_resizer_type(self)
        resizer.remove_row_top(reconfigure_edges=True)

    def remove_row_bottom(self):
        resizer = self.tessellation.board_resizer_type(self)
        resizer.remove_row_bottom(reconfigure_edges=True)

    def remove_column_left(self):
        resizer = self.tessellation.board_resizer_type(self)
        resizer.remove_column_left(reconfigure_edges=True)

    def remove_column_right(self):
        resizer = self.tessellation.board_resizer_type(self)
        resizer.remove_column_right(reconfigure_edges=True)

    def trim_left(self):
        resizer = self.tessellation.board_resizer_type(self)
        resizer.trim_left(reconfigure_edges=True)

    def trim_right(self):
        resizer = self.tessellation.board_resizer_type(self)
        resizer.trim_right(reconfigure_edges=True)

    def trim_top(self):
        resizer = self.tessellation.board_resizer_type(self)
        resizer.trim_top(reconfigure_edges=True)

    def trim_bottom(self):
        resizer = self.tessellation.board_resizer_type(self)
        resizer.trim_bottom(reconfigure_edges=True)

    def reverse_rows(self):
        resizer = self.tessellation.board_resizer_type(self)
        resizer.reverse_rows(reconfigure_edges=True)

    def reverse_columns(self):
        resizer = self.tessellation.board_resizer_type(self)
        resizer.reverse_columns(reconfigure_edges=True)

    def resize(self, new_width, new_height):
        old_width = self.width
        old_height = self.height

        resizer = self.tessellation.board_resizer_type(self)
        if new_height != old_height:
            if new_height > old_height:
                amount = new_height - old_height
                for i in range(0, amount):
                    resizer.add_row_bottom(reconfigure_edges=False)
            else:
                amount = old_height - new_height
                for i in range(0, amount):
                    resizer.remove_row_bottom(reconfigure_edges=False)

        if new_width != old_width:
            if new_width > old_width:
                amount = new_width - old_width
                for i in range(0, amount):
                    resizer.add_column_right(reconfigure_edges=False)
            else:
                amount = old_width - new_width
                for i in range(0, amount):
                    resizer.remove_column_right(reconfigure_edges=False)

        if old_width != self.width or old_height != self.height:
            self._reconfigure_edges()

    def resize_and_center(self, new_width, new_height):
        left = right = top = bottom = 0

        if new_width > self.width:
            left = int((new_width - self.width) / 2)
            right = new_width - self.width - left

        if new_height > self.height:
            top = int((new_height - self.height) / 2)
            bottom = new_height - self.height - top

        if (left, right, top, bottom) != (0, 0, 0, 0):
            resizer = self.tessellation.board_resizer_type(self)
            for i in range(0, left):
                resizer.add_column_left(reconfigure_edges=False)
            for i in range(0, top):
                resizer.add_row_top(reconfigure_edges=False)

            self.resize(self.width + right, self.height + bottom)

    def trim(self):
        old_width = self.width
        old_height = self.height

        resizer = self.tessellation.board_resizer_type(self)
        resizer.trim_top(reconfigure_edges=False)
        resizer.trim_bottom(reconfigure_edges=False)
        resizer.trim_left(reconfigure_edges=False)
        resizer.trim_right(reconfigure_edges=False)

        if old_width != self.width or old_height != old_height:
            self._reconfigure_edges()


class VariantBoardResizer(ABC):

    def __init__(self, variant_board):
        self.board = variant_board

    def add_row_top(self, reconfigure_edges):
        old_body = self.board._graph
        old_height = self.board.height

        self.board._reinit(
            self.board.width, self.board.height + 1,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, old_height):
                self.board[INDEX(x, y + 1, self.board.width)] =\
                    old_body.node[INDEX(x, y, self.board.width)]['cell']

    def add_row_bottom(self, reconfigure_edges):
        old_body = self.board._graph
        old_height = self.board.height

        self.board._reinit(
            self.board.width, self.board.height + 1,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, old_height):
                self.board[INDEX(x, y, self.board.width)] =\
                    old_body.node[INDEX(x, y, self.board.width)]['cell']

    def add_column_left(self, reconfigure_edges):
        old_body = self.board._graph
        old_width = self.board.width

        self.board._reinit(
            self.board.width + 1, self.board.height,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, old_width):
            for y in range(0, self.board.height):
                self.board[INDEX(x + 1, y, self.board.width)] =\
                    old_body.node[INDEX(x, y, old_width)]['cell']

    def add_column_right(self, reconfigure_edges):
        old_body = self.board._graph
        old_width = self.board.width

        self.board._reinit(
            self.board.width + 1, self.board.height,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, old_width):
            for y in range(0, self.board.height):
                self.board[INDEX(x, y, self.board.width)] =\
                    old_body.node[INDEX(x, y, old_width)]['cell']

    def remove_row_top(self, reconfigure_edges):
        old_body = self.board._graph

        self.board._reinit(
            self.board.width, self.board.height - 1,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[INDEX(x, y, self.board.width)] =\
                    old_body.node[INDEX(x, y + 1, self.board.width)]['cell']

    def remove_row_bottom(self, reconfigure_edges):
        old_body = self.board._graph

        self.board._reinit(
            self.board.width, self.board.height - 1,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[INDEX(x, y, self.board.width)] =\
                    old_body.node[INDEX(x, y, self.board.width)]['cell']

    def remove_column_left(self, reconfigure_edges):
        old_body = self.board._graph
        old_width = self.board.width

        self.board._reinit(
            self.board.width - 1, self.board.height,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[INDEX(x, y, self.board.width)] =\
                    old_body.node[INDEX(x + 1, y, old_width)]['cell']

    def remove_column_right(self, reconfigure_edges):
        old_body = self.board._graph
        old_width = self.board.width

        self.board._reinit(
            self.board.width - 1, self.board.height,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[INDEX(x, y, self.board.width)] =\
                    old_body.node[INDEX(x, y, old_width)]['cell']

    def trim_left(self, reconfigure_edges):
        amount = self.board.width
        for y in range(0, self.board.height):
            border_found = False
            for x in range(0, self.board.width):
                border_found = self.board[
                    INDEX(x, y, self.board.width)
                ].is_border_element
                if border_found:
                    if x < amount:
                        amount = x
                    break

        for i in range(0, amount):
            self.remove_column_left(reconfigure_edges=False)

        if reconfigure_edges:
            self.board._reconfigure_edges()

    def trim_right(self, reconfigure_edges):
        self.reverse_columns(reconfigure_edges=False)
        self.trim_left(reconfigure_edges=False)
        self.reverse_columns(reconfigure_edges=False)

        if reconfigure_edges:
            self.board._reconfigure_edges()

    def trim_top(self, reconfigure_edges):
        amount = self.board.height
        for x in range(0, self.board.width):
            border_found = False
            for y in range(0, self.board.height):
                border_found = self.board[
                    INDEX(x, y, self.board.width)
                ].is_border_element
                if border_found:
                    if y < amount:
                        amount = y
                    break

        for i in range(0, amount):
            self.remove_row_top(reconfigure_edges=False)

        if reconfigure_edges:
            self.board._reconfigure_edges()

    def trim_bottom(self, reconfigure_edges):
        self.reverse_rows(reconfigure_edges=False)
        self.trim_top(reconfigure_edges=False)
        self.reverse_rows(reconfigure_edges=False)

        if reconfigure_edges:
            self.board._reconfigure_edges()

    def reverse_rows(self, reconfigure_edges):
        old_body = self.board._graph

        self.board._reinit(
            self.board.width, self.board.height,
            reconfigure_edges=False
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[INDEX(x, y, self.board.width)] = \
                    old_body.node[INDEX(x, self.board.height - y - 1, self.board.width)]['cell']

        if reconfigure_edges:
            self.board._reconfigure_edges()

    def reverse_columns(self, reconfigure_edges):
        old_body = self.board._graph

        self.board._reinit(
            self.board.width, self.board.height,
            reconfigure_edges=False
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[INDEX(x, y, self.board.width)] = \
                    old_body.node[INDEX(self.board.width - x - 1, y, self.board.width)]['cell']

        if reconfigure_edges:
            self.board._reconfigure_edges()
