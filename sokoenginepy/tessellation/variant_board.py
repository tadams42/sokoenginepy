from abc import ABC, abstractmethod
from collections.abc import Container
from functools import wraps

import networkx as nx

from ..board import BoardCell, parse_board_string
from ..common import (EqualityComparable, PrettyPrintable, RleCharacters,
                      Variant, is_blank, rle_encode)
from ..input_output import OutputSettings
from .factories import tessellation_factory
from .graph import BoardGraph
from .tessellated import Tessellated
from .tessellation import index_1d


def _normalize_index_errors(method):
    """Normalizes NetworkX index out of range errors into IndexError."""

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
    """Base board class for variant specific implementations.

    Internally it is stored as directed graph structure.

    Implements concerns of

        - board cell access/editing
        - string (de)serialization
        - resizing
        - board-space searching

    All positions are int indexes of graph vertices. To convert 2D coordinate
    into vertice index, use :func:`.index_1d`

    Args:
        board_width (int): number of columns
        board_height (int): number of rows
        variant (Variant): game variant
        board_str (string): textual representation of board
    """

    def __init__(
        self, board_width=0, board_height=0, variant=Variant.SOKOBAN,
        board_str=""
    ):
        super().__init__(variant)
        self._graph = None
        self._width = 0
        self._height = 0
        self._tessellation = tessellation_factory(variant)
        self._resizer = self._resizer_class(self)

        if not is_blank(board_str):
            self._reinit_with_string(board_str)
        else:
            self._reinit(board_width, board_height)

    @property
    @abstractmethod
    def _resizer_class(self):
        """
        subclass of VariantBoardResizer
        """
        pass

    def _reinit(self, width, height, reconfigure_edges=True):
        self._graph = BoardGraph(width * height, self.tessellation.graph_type)

        self._width = width
        self._height = height

        if reconfigure_edges:
            self._graph.reconfigure_edges(
                self.width, self.height, self.tessellation
            )

    def _reinit_with_string(self, board_str, reconfigure_edges=True):
        if not is_blank(board_str):
            board_rows = self._parse_string(board_str)
            width = len(board_rows[0]) if len(board_rows) > 0 else 0
            height = len(board_rows)
            self._reinit(width, height, reconfigure_edges)
            for y, row in enumerate(board_rows):
                for x, character in enumerate(row):
                    self._graph[index_1d(x, y, self._width)
                               ] = BoardCell(character)

    @property
    def _representation_attributes(self):
        return {
            'tessellation': self.variant,
            'width': self.width,
            'height': self.height,
            'board': self.to_s,
        }

    def __eq__(self, other):
        if (self.variant == other.variant and self.width == other.width and self.height == other.height):
            for vertice in range(0, self.size):
                if self[vertice] != other[vertice]:
                    return False
            return True
        else:
            return False

    @abstractmethod
    def _parse_string(self, board_str):
        """Override this in subclass to handle tessellation speciffic strings.

        Should return list of strings where each string represents all BoardCell
        in single line of game board.
        """
        return parse_board_string(board_str)

    @_normalize_index_errors
    def __getitem__(self, position):
        return self._graph[position]

    @_normalize_index_errors
    def __setitem__(self, position, board_cell):
        self._graph[position] = board_cell

    def __contains__(self, position):
        return position in self._graph

    @abstractmethod
    def to_s(self, output_settings=OutputSettings()):
        """Override this in subclass to handle tessellation speciffic strings."""
        rows = []
        for y in range(0, self.height):
            row = "".join(
                cell.to_s(output_settings.use_visible_floors)
                for cell in (
                    self[index_1d(x, y, self.width)]
                    for x in range(0, self.width)
                )
            )
            # Intentionally rstripping only if not using visible floors
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

    @_normalize_index_errors
    def neighbor(self, from_position, direction):
        """
        Returns:
            int: neighbor position in ``direction``
        """
        return self._graph.neighbor(from_position, direction)

    @_normalize_index_errors
    def wall_neighbors(self, from_position):
        """
        Returns:
            list: of neighbor positions that are walls
        """
        return self._graph.wall_neighbors(from_position)

    @_normalize_index_errors
    def all_neighbors(self, from_position):
        """
        Returns:
            list: of neighbor positions
        """
        return self._graph.all_neighbors(from_position)

    def clear(self):
        """Empties all board cells."""
        for vertice in range(0, self.size):
            self[vertice].clear()

    def mark_play_area(self):
        """
        Returns:
            list: of positions that are playable (reachable by any box or pusher)
        """
        piece_positions = []
        for vertice in range(0, self.size):
            if self[vertice].has_box or self[vertice].has_pusher:
                self[vertice].is_in_playable_area = True
                piece_positions.append(vertice)
            else:
                self[vertice].is_in_playable_area = False

        def is_obstacle(vertice):
            return self[vertice].is_wall

        for piece_position in piece_positions:
            reachables = self._graph.reachables(
                root=piece_position, is_obstacle_callable=is_obstacle
            )

            for reachable_vertice in reachables:
                self[reachable_vertice].is_in_playable_area = True

    @_normalize_index_errors
    def positions_reachable_by_pusher(
        self, pusher_position, excluded_positions=None
    ):
        """
        Returns:
            list: of positions that are reachable by pusher standing on ``position``
        """

        def is_obstacle(position):
            return not self[position].can_put_pusher_or_box

        return self._graph.reachables(
            root=pusher_position,
            is_obstacle_callable=is_obstacle,
            excluded_positions=excluded_positions
        )

    @_normalize_index_errors
    def normalized_pusher_position(
        self, pusher_position, excluded_positions=None
    ):
        """
        Returns:
            int: Top-left position reachable by pusher
        """
        reachables = self.positions_reachable_by_pusher(
            pusher_position=pusher_position,
            excluded_positions=excluded_positions
        )
        if reachables:
            return min(reachables)
        else:
            return pusher_position

    @_normalize_index_errors
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
        """
        Returns:
            list: of positions through which pusher must pass when jumping
        """
        if start_position not in self:
            raise IndexError('Board index out of range')
        return self._graph.shortest_path(start_position, end_position)

    def find_move_path(self, start_position, end_position):
        """
        Returns:
            list: of positions through which pusher must pass when moving without pushing boxes
        """
        if start_position not in self:
            raise IndexError('Board index out of range')

        path = self._graph.dijkstra_path(start_position, end_position)

        retv = path[:1]
        for position in path[1:]:
            if self[position].can_put_pusher_or_box:
                retv.append(position)
            else:
                break
        if retv != path:
            return []
        return path

    def cell_orientation(self, position):
        """
        Returns:
            CellOrientation: game variant specific parameter
        """
        return self.tessellation.cell_orientation(
            position, self._width, self._height
        )

    @_normalize_index_errors
    def position_path_to_direction_path(self, position_path):
        """
        Returns:
            list: of :class:`.Direction`
        """
        return self._graph.position_path_to_direction_path(position_path)

    def add_row_top(self):
        self._resizer.add_row_top(reconfigure_edges=True)

    def add_row_bottom(self):
        self._resizer.add_row_bottom(reconfigure_edges=True)

    def add_column_left(self):
        self._resizer.add_column_left(reconfigure_edges=True)

    def add_column_right(self):
        self._resizer.add_column_right(reconfigure_edges=True)

    def remove_row_top(self):
        self._resizer.remove_row_top(reconfigure_edges=True)

    def remove_row_bottom(self):
        self._resizer.remove_row_bottom(reconfigure_edges=True)

    def remove_column_left(self):
        self._resizer.remove_column_left(reconfigure_edges=True)

    def remove_column_right(self):
        self._resizer.remove_column_right(reconfigure_edges=True)

    def trim_left(self):
        self._resizer.trim_left(reconfigure_edges=True)

    def trim_right(self):
        self._resizer.trim_right(reconfigure_edges=True)

    def trim_top(self):
        self._resizer.trim_top(reconfigure_edges=True)

    def trim_bottom(self):
        self._resizer.trim_bottom(reconfigure_edges=True)

    def reverse_rows(self):
        self._resizer.reverse_rows(reconfigure_edges=True)

    def reverse_columns(self):
        self._resizer.reverse_columns(reconfigure_edges=True)

    def resize(self, new_width, new_height):
        old_width = self.width
        old_height = self.height

        if new_height != old_height:
            if new_height > old_height:
                amount = new_height - old_height
                for i in range(0, amount):
                    self._resizer.add_row_bottom(reconfigure_edges=False)
            else:
                amount = old_height - new_height
                for i in range(0, amount):
                    self._resizer.remove_row_bottom(reconfigure_edges=False)

        if new_width != old_width:
            if new_width > old_width:
                amount = new_width - old_width
                for i in range(0, amount):
                    self._resizer.add_column_right(reconfigure_edges=False)
            else:
                amount = old_width - new_width
                for i in range(0, amount):
                    self._resizer.remove_column_right(reconfigure_edges=False)

        if old_width != self.width or old_height != self.height:
            self._graph.reconfigure_edges(
                self.width, self.height, self.tessellation
            )

    def resize_and_center(self, new_width, new_height):
        left = right = top = bottom = 0

        if new_width > self.width:
            left = int((new_width - self.width) / 2)
            right = new_width - self.width - left

        if new_height > self.height:
            top = int((new_height - self.height) / 2)
            bottom = new_height - self.height - top

        if (left, right, top, bottom) != (0, 0, 0, 0):
            for i in range(0, left):
                self._resizer.add_column_left(reconfigure_edges=False)
            for i in range(0, top):
                self._resizer.add_row_top(reconfigure_edges=False)

            self.resize(self.width + right, self.height + bottom)

    def trim(self):
        old_width = self.width
        old_height = self.height

        self._resizer.trim_top(reconfigure_edges=False)
        self._resizer.trim_bottom(reconfigure_edges=False)
        self._resizer.trim_left(reconfigure_edges=False)
        self._resizer.trim_right(reconfigure_edges=False)

        if old_width != self.width or old_height != old_height:
            self._graph.reconfigure_edges(
                self.width, self.height, self.tessellation
            )


class VariantBoardResizer(ABC):
    """
    Implements board graph transformations related to adding/removing board
    rows and columnns.
    """

    def __init__(self, variant_board):
        self.board = variant_board

    def add_row_top(self, reconfigure_edges):
        old_body = self.board._graph
        old_height = self.board.height

        self.board._reinit(
            self.board.width,
            self.board.height + 1,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, old_height):
                self.board[index_1d(x, y + 1, self.board.width)] =\
                    old_body[index_1d(x, y, self.board.width)]

    def add_row_bottom(self, reconfigure_edges):
        old_body = self.board._graph
        old_height = self.board.height

        self.board._reinit(
            self.board.width,
            self.board.height + 1,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, old_height):
                self.board[index_1d(x, y, self.board.width)] =\
                    old_body[index_1d(x, y, self.board.width)]

    def add_column_left(self, reconfigure_edges):
        old_body = self.board._graph
        old_width = self.board.width

        self.board._reinit(
            self.board.width + 1,
            self.board.height,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, old_width):
            for y in range(0, self.board.height):
                self.board[index_1d(x + 1, y, self.board.width)] =\
                    old_body[index_1d(x, y, old_width)]

    def add_column_right(self, reconfigure_edges):
        old_body = self.board._graph
        old_width = self.board.width

        self.board._reinit(
            self.board.width + 1,
            self.board.height,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, old_width):
            for y in range(0, self.board.height):
                self.board[index_1d(x, y, self.board.width)] =\
                    old_body[index_1d(x, y, old_width)]

    def remove_row_top(self, reconfigure_edges):
        old_body = self.board._graph

        self.board._reinit(
            self.board.width,
            self.board.height - 1,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[index_1d(x, y, self.board.width)] =\
                    old_body[index_1d(x, y + 1, self.board.width)]

    def remove_row_bottom(self, reconfigure_edges):
        old_body = self.board._graph

        self.board._reinit(
            self.board.width,
            self.board.height - 1,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[index_1d(x, y, self.board.width)] =\
                    old_body[index_1d(x, y, self.board.width)]

    def remove_column_left(self, reconfigure_edges):
        old_body = self.board._graph
        old_width = self.board.width

        self.board._reinit(
            self.board.width - 1,
            self.board.height,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[index_1d(x, y, self.board.width)] =\
                    old_body[index_1d(x + 1, y, old_width)]

    def remove_column_right(self, reconfigure_edges):
        old_body = self.board._graph
        old_width = self.board.width

        self.board._reinit(
            self.board.width - 1,
            self.board.height,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[index_1d(x, y, self.board.width)] =\
                    old_body[index_1d(x, y, old_width)]

    def trim_left(self, reconfigure_edges):
        amount = self.board.width
        for y in range(0, self.board.height):
            border_found = False
            for x in range(0, self.board.width):
                border_found = self.board[index_1d(x, y, self.board.width)
                                         ].is_border_element
                if border_found:
                    if x < amount:
                        amount = x
                    break

        for i in range(0, amount):
            self.remove_column_left(reconfigure_edges=False)

        if reconfigure_edges:
            self.board._graph.reconfigure_edges(
                self.board.width, self.board.height, self.board.tessellation
            )

    def trim_right(self, reconfigure_edges):
        self.reverse_columns(reconfigure_edges=False)
        self.trim_left(reconfigure_edges=False)
        self.reverse_columns(reconfigure_edges=False)

        if reconfigure_edges:
            self.board._graph.reconfigure_edges(
                self.board.width, self.board.height, self.board.tessellation
            )

    def trim_top(self, reconfigure_edges):
        amount = self.board.height
        for x in range(0, self.board.width):
            border_found = False
            for y in range(0, self.board.height):
                border_found = self.board[index_1d(x, y, self.board.width)
                                         ].is_border_element
                if border_found:
                    if y < amount:
                        amount = y
                    break

        for i in range(0, amount):
            self.remove_row_top(reconfigure_edges=False)

        if reconfigure_edges:
            self.board._graph.reconfigure_edges(
                self.board.width, self.board.height, self.board.tessellation
            )

    def trim_bottom(self, reconfigure_edges):
        self.reverse_rows(reconfigure_edges=False)
        self.trim_top(reconfigure_edges=False)
        self.reverse_rows(reconfigure_edges=False)

        if reconfigure_edges:
            self.board._graph.reconfigure_edges(
                self.board.width, self.board.height, self.board.tessellation
            )

    def reverse_rows(self, reconfigure_edges):
        old_body = self.board._graph

        self.board._reinit(
            self.board.width, self.board.height, reconfigure_edges=False
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[index_1d(x, y, self.board.width)] = \
                    old_body[index_1d(x, self.board.height - y - 1, self.board.width)]

        if reconfigure_edges:
            self.board._graph.reconfigure_edges(
                self.board.width, self.board.height, self.board.tessellation
            )

    def reverse_columns(self, reconfigure_edges):
        old_body = self.board._graph

        self.board._reinit(
            self.board.width, self.board.height, reconfigure_edges=False
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[index_1d(x, y, self.board.width)] = \
                    old_body[index_1d(self.board.width - x - 1, y, self.board.width)]

        if reconfigure_edges:
            self.board._graph.reconfigure_edges(
                self.board.width, self.board.height, self.board.tessellation
            )
