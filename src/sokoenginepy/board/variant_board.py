import re
import textwrap
from abc import ABCMeta, abstractmethod
from collections.abc import Container
from functools import reduce

from .. import tessellation, utilities
from .board_cell import BoardCell, BoardCellCharacters, BoardConversionError
from .graph import BoardGraph

_RE_BOARD_STRING = re.compile(
    r"^([0-9\s" + re.escape("".join(c for c in BoardCellCharacters)) +
    re.escape("".join(c for c in utilities.RleCharacters)) + "])*$"
)


class VariantBoard(Container, metaclass=ABCMeta):
    """Base board class for variant specific implementations.

    Internally it is stored as directed graph structure.

    Implements concerns of

        - board cell access/editing
        - string (de)serialization
        - resizing
        - board-space searching

    All positions are int indexes of graph vertices. To convert 2D coordinate
    into vertex index, use :func:`.index_1d`

    Args:
        tessellation_or_description (Tessellation): game tessellation or string
            describing it
        board_width (int): number of columns
        board_height (int): number of rows
        board_str (string): textual representation of board
    """

    @classmethod
    def instance_from(
        cls, tessellation_or_description='sokoban',
        board_width=0, board_height=0, board_str=None
    ):
        #pylint: disable=unused-variable
        from .hexoban_board import HexobanBoard
        from .octoban_board import OctobanBoard
        from .sokoban_board import SokobanBoard
        from .trioban_board import TriobanBoard

        tessellation_instance = tessellation.Tessellation.instance_from(
            tessellation_or_description
        )

        for klass in VariantBoard.__subclasses__():
            if tessellation_instance.name.lower() in klass.__name__.lower():
                return klass(
                    board_width=board_width, board_height=board_height,
                    board_str=board_str
                )

        raise tessellation.UnknownTessellationError(tessellation)

    @classmethod
    def is_board_string(cls, line):
        """
        Checks if line contains only characters legal in textual representation
        of boards.

        Note:
            Doesn't check if it actually contains legal board, it only checks
            that there are no illegal characters. To find out if line is actual
            board representation, it must be converted to actual game board.
        """
        return (
            not utilities.contains_only_digits_and_spaces(line) and reduce(
                lambda x, y: x and y, [
                    True if _RE_BOARD_STRING.match(l) else False
                    for l in line.splitlines()
                ], True
            )
        )

    @classmethod
    def parse_board_string(cls, line):
        """Tries to parse board from string.

        Returns:
            list: list of board strings, each representing single board line
        """
        if utilities.is_blank(line):
            return []
        if not cls.is_board_string(line):
            raise BoardConversionError(
                "Illegal characters found in board string"
            )

        line = utilities.rle_decode(line)
        return utilities.normalize_width(line.split('\n'))

    def __init__(
        self, tessellation_or_description, board_width=0, board_height=0,
        board_str=None
    ):
        super().__init__()
        self._tessellation_instance = tessellation.Tessellation.instance_from(
            tessellation_or_description
        )
        self._graph = None
        self._width = 0
        self._height = 0
        self._resizer = self._resizer_class(self)

        if not utilities.is_blank(board_str):
            self._reinit_with_string(board_str)
        else:
            self._reinit(board_width, board_height)

    @property
    def tessellation(self):
        return self._tessellation_instance.value

    @property
    @abstractmethod
    def _resizer_class(self):
        """
        subclass of VariantBoardResizer
        """
        pass

    def _reconfigure_edges(self):
        """Recreate all edges using :attr:`.tessellation`."""
        self._graph.remove_all_edges()
        for source_vertex in range(self.size):
            for direction in self.tessellation.legal_directions:
                neighbor_vertex = self.tessellation.neighbor_position(
                    source_vertex, direction, self.width, self.height
                )
                if neighbor_vertex is not None:
                    self._graph.add_edge(
                        source_vertex, neighbor_vertex, direction
                    )

    def _reinit(self, width, height, reconfigure_edges=True):
        self._graph = BoardGraph(width * height, self.tessellation.graph_type)

        self._width = width
        self._height = height

        if reconfigure_edges:
            self._reconfigure_edges()

    def _reinit_with_string(self, board_str, reconfigure_edges=True):
        if not utilities.is_blank(board_str):
            board_rows = self._parse_string(board_str)
            height = len(board_rows)
            width = len(board_rows[0]) if height > 0 else 0
            self._reinit(width, height, reconfigure_edges)
            for y, row in enumerate(board_rows):
                for x, character in enumerate(row):
                    self._graph[utilities.index_1d(x, y, self._width)
                               ] = BoardCell(character)

    def __eq__(self, rv):
        if (self.tessellation == rv.tessellation and self.width == rv.width and
                self.height == rv.height):
            for vertex in range(0, self.size):
                if self[vertex] != rv[vertex]:
                    return False
            return True
        else:
            return False

    def __ne__(self, rv):
        return not self == rv

    @abstractmethod
    def _parse_string(self, board_str):
        """Override this in subclass to handle tessellation speciffic strings.

        Should return list of strings where each string represents all BoardCell
        in single line of game board.
        """
        return self.parse_board_string(board_str)

    def __getitem__(self, position):
        return self._graph[position]

    def __setitem__(self, position, board_cell):
        if isinstance(board_cell, BoardCell):
            self._graph[position] = board_cell
        else:
            self._graph[position] = BoardCell(board_cell)

    def __contains__(self, position):
        return position in self._graph

    def to_str(self, use_visible_floor=False, rle_encode=False):
        rows = []
        for y in range(0, self.height):
            row = "".join(
                cell.to_str(use_visible_floor=use_visible_floor)
                for cell in (
                    self[utilities.index_1d(x, y, self.width)]
                    for x in range(0, self.width)
                )
            )
            if rle_encode:
                row = utilities.rle_encode(row)
            rows.append(row)

        if rle_encode:
            return utilities.RleCharacters.RLE_ROW_SEPARATOR.join(rows)
        else:
            return "\n".join(rows)

    def __str__(self):
        return self.to_str(use_visible_floor=False, rle_encode=False)

    def __repr__(self):
        board_str = textwrap.indent(
            ',\n'.join(["'{0}'".format(l) for l in str(self).split('\n')]),
            '    '
        )
        return "{klass}(board_str='\\n'.join([\n{board_str}\n]))".format(
            klass=self.__class__.__name__, board_str=board_str
        )

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def size(self):
        return self._width * self._height

    def neighbor(self, from_position, direction):
        """
        Calculates neighbor vertex index in ``direction``

        Returns:
            int: neighbor position in ``direction`` or None if neighbor
            position in ``direction`` would lead of board

        Raises:
            IndexError: if ``from_position`` is out of board position
        """
        return self._graph.neighbor(from_position, direction)

    def wall_neighbors(self, from_position):
        """
        Returns:
            list: of neighbor positions that are walls
        """
        return self._graph.wall_neighbors(from_position)

    def all_neighbors(self, from_position):
        """
        Returns:
            list: of neighbor positions
        """
        return self._graph.all_neighbors(from_position)

    def clear(self):
        """Empties all board cells."""
        for vertex in range(0, self.size):
            self[vertex].clear()

    def mark_play_area(self):
        """
        Marks all BoardCell that are playable (reachable by any box or pusher).
        """
        self._graph.mark_play_area()

    def positions_reachable_by_pusher(
        self, pusher_position, excluded_positions=None
    ):
        """
        Returns:
            list: of positions that are reachable by pusher standing on
            ``position``
        """
        return self._graph.positions_reachable_by_pusher(
            pusher_position, excluded_positions
        )

    def normalized_pusher_position(
        self, pusher_position, excluded_positions=None
    ):
        """
        Returns:
            int: Top-left position reachable by pusher
        """
        return self._graph.normalized_pusher_position(
            pusher_position, excluded_positions
        )

    def path_destination(self, start_position, directions_path):
        return self._graph.path_destination(start_position, directions_path)

    def find_jump_path(self, start_position, end_position):
        """
        Returns:
            list: of positions through which pusher must pass when jumping
        """
        return self._graph.find_jump_path(start_position, end_position)

    def find_move_path(self, start_position, end_position):
        """
        Returns:
            list: of positions through which pusher must pass when moving
            without pushing boxes
        """
        return self._graph.find_move_path(start_position, end_position)

    def cell_orientation(self, position):
        """
        Returns:
            CellOrientation: game variant specific parameter
        """
        return self.tessellation.cell_orientation(
            position, self._width, self._height
        )

    def positions_path_to_directions_path(self, positions_path):
        """
        Converts path expressed as vertices' indexes to one expressed as
        :class:`.Direction`

        Args:
            positions_path (list): list of integer positions

        Returns:
            list: of :class:`.Direction` instances
        """
        return self._graph.positions_path_to_directions_path(positions_path)

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
                for _ in range(0, amount):
                    self._resizer.add_row_bottom(reconfigure_edges=False)
            else:
                amount = old_height - new_height
                for _ in range(0, amount):
                    self._resizer.remove_row_bottom(reconfigure_edges=False)

        if new_width != old_width:
            if new_width > old_width:
                amount = new_width - old_width
                for _ in range(0, amount):
                    self._resizer.add_column_right(reconfigure_edges=False)
            else:
                amount = old_width - new_width
                for _ in range(0, amount):
                    self._resizer.remove_column_right(reconfigure_edges=False)

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
            for _ in range(0, left):
                self._resizer.add_column_left(reconfigure_edges=False)
            for _ in range(0, top):
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
            self._reconfigure_edges()


class VariantBoardResizer(metaclass=ABCMeta):
    """
    Implements board graph transformations related to adding/removing board
    rows and columnns.
    """

    #pylint: disable=protected-access
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
                self.board[utilities.index_1d(x, y + 1, self.board.width)] =\
                    old_body[utilities.index_1d(x, y, self.board.width)]

    def add_row_bottom(self, reconfigure_edges):
        old_body = self.board._graph
        old_height = self.board.height

        self.board._reinit(
            self.board.width, self.board.height + 1,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, old_height):
                self.board[utilities.index_1d(x, y, self.board.width)] =\
                    old_body[utilities.index_1d(x, y, self.board.width)]

    def add_column_left(self, reconfigure_edges):
        old_body = self.board._graph
        old_width = self.board.width

        self.board._reinit(
            self.board.width + 1, self.board.height,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, old_width):
            for y in range(0, self.board.height):
                self.board[utilities.index_1d(x + 1, y, self.board.width)] =\
                    old_body[utilities.index_1d(x, y, old_width)]

    def add_column_right(self, reconfigure_edges):
        old_body = self.board._graph
        old_width = self.board.width

        self.board._reinit(
            self.board.width + 1, self.board.height,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, old_width):
            for y in range(0, self.board.height):
                self.board[utilities.index_1d(x, y, self.board.width)] =\
                    old_body[utilities.index_1d(x, y, old_width)]

    def remove_row_top(self, reconfigure_edges):
        old_body = self.board._graph

        self.board._reinit(
            self.board.width, self.board.height - 1,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[utilities.index_1d(x, y, self.board.width)] =\
                    old_body[utilities.index_1d(x, y + 1, self.board.width)]

    def remove_row_bottom(self, reconfigure_edges):
        old_body = self.board._graph

        self.board._reinit(
            self.board.width, self.board.height - 1,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[utilities.index_1d(x, y, self.board.width)] =\
                    old_body[utilities.index_1d(x, y, self.board.width)]

    def remove_column_left(self, reconfigure_edges):
        old_body = self.board._graph
        old_width = self.board.width

        self.board._reinit(
            self.board.width - 1, self.board.height,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[utilities.index_1d(x, y, self.board.width)] =\
                    old_body[utilities.index_1d(x + 1, y, old_width)]

    def remove_column_right(self, reconfigure_edges):
        old_body = self.board._graph
        old_width = self.board.width

        self.board._reinit(
            self.board.width - 1, self.board.height,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[utilities.index_1d(x, y, self.board.width)] =\
                    old_body[utilities.index_1d(x, y, old_width)]

    def trim_left(self, reconfigure_edges):
        amount = self.board.width
        for y in range(0, self.board.height):
            border_found = False
            for x in range(0, self.board.width):
                border_found = self.board[utilities.index_1d(
                    x, y, self.board.width
                )].is_border_element
                if border_found:
                    if x < amount:
                        amount = x
                    break

        for _ in range(0, amount):
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
                border_found = self.board[utilities.index_1d(
                    x, y, self.board.width
                )].is_border_element
                if border_found:
                    if y < amount:
                        amount = y
                    break

        for _ in range(0, amount):
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
            self.board.width, self.board.height, reconfigure_edges=False
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[utilities.index_1d(x, y, self.board.width)] = \
                    old_body[utilities.index_1d(
                        x, self.board.height - y - 1, self.board.width
                    )]

        if reconfigure_edges:
            self.board._reconfigure_edges()

    def reverse_columns(self, reconfigure_edges):
        old_body = self.board._graph

        self.board._reinit(
            self.board.width, self.board.height, reconfigure_edges=False
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[utilities.index_1d(x, y, self.board.width)] = \
                    old_body[utilities.index_1d(
                        self.board.width - x - 1, y, self.board.width
                    )]

        if reconfigure_edges:
            self.board._reconfigure_edges()
