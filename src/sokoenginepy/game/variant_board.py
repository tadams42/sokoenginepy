from __future__ import annotations

import textwrap
from abc import ABCMeta, abstractmethod
from collections.abc import Container
from typing import List, Optional, Type

from ..io import Puzzle, Rle, is_blank
from .board_cell import BoardCell
from .board_graph import BoardCellOrStr, BoardGraph, Directions, Positions
from .cell_orientation import CellOrientation
from .direction import Direction
from .tessellation import AnyTessellation, Tessellation, TessellationOrDescription
from .utilities import index_1d


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

    To convert 1D vertex index into 2D coordinates, use combinations of :func:`.ROW` and
    :func:`.COLUMN` functions.
    """

    @classmethod
    def instance_from(
        cls,
        tessellation_or_description: TessellationOrDescription = "sokoban",
        board_width: int = 0,
        board_height: int = 0,
        board_str: Optional[str] = None,
    ) -> VariantBoard:
        """
        Factory method. Produces instance of one of the subclasses.
        """

        from .hexoban_board import HexobanBoard
        from .octoban_board import OctobanBoard
        from .sokoban_board import SokobanBoard
        from .trioban_board import TriobanBoard

        tessellation_instance = Tessellation.instance_from(tessellation_or_description)

        for klass in [HexobanBoard, OctobanBoard, SokobanBoard, TriobanBoard]:
            if (
                tessellation_instance.__class__.__name__.replace(
                    "Tessellation", ""
                ).lower()
                in klass.__name__.lower()
            ):
                return klass(
                    board_width=board_width,
                    board_height=board_height,
                    board_str=board_str,
                )

        raise ValueError(tessellation_or_description)

    def __init__(
        self,
        tessellation_or_description: TessellationOrDescription,
        board_width: int = 0,
        board_height: int = 0,
        board_str: Optional[str] = None,
    ):
        """
        Arguments:
            board_width: number of columns
            board_height: number of rows
            board_str: If not blank, it will be parsed and board will be created from
                it, ignoring ``board_width`` and ``board_height``.
        """
        super().__init__()
        self._tessellation = Tessellation.instance_from(tessellation_or_description)
        self._graph = BoardGraph(
            board_width, board_height, self._tessellation.graph_type
        )
        self._resizer = self._resizer_class(self)

        if not is_blank(board_str):
            self._reinit_with_string(board_str)
        else:
            self._reinit(board_width, board_height, reconfigure_edges=True)

    @property
    def tessellation(self) -> AnyTessellation:
        return self._tessellation

    @property
    @abstractmethod
    def _resizer_class(self) -> Type[VariantBoardResizer]:
        pass

    @property
    def graph(self) -> BoardGraph:
        return self._graph

    def __eq__(self, rv):
        if (
            self.tessellation == rv.tessellation
            and self.width == rv.width
            and self.height == rv.height
        ):
            for vertex in range(0, self.size):
                if self[vertex] != rv[vertex]:
                    return False
            return True
        else:
            return False

    def __ne__(self, rv):
        return not self == rv

    @abstractmethod
    def _parse_string(self, board_str: Optional[str]) -> List[str]:
        """
        Override this in subclass to handle tessellation speciffic strings.

        Should return list of strings where each string represents all BoardCell in
        single row of game board.
        """
        return self._cleaned_board_lines(board_str)

    def __getitem__(self, position: int) -> BoardCell:
        return self.graph[position]

    def __setitem__(self, position: int, board_cell: BoardCellOrStr):
        self.graph[position] = board_cell

    def __contains__(self, position: int):
        return position in self.graph

    def to_str(self, use_visible_floor=False) -> str:
        rows = []
        for y in range(0, self.height):
            row = "".join(
                cell.to_str(use_visible_floor=use_visible_floor)
                for cell in (
                    self[index_1d(x, y, self.width)] for x in range(0, self.width)
                )
            )
            rows.append(row)

        return "\n".join(rows)

    def __str__(self):
        return self.to_str(use_visible_floor=False)

    def __repr__(self):
        return "{klass}(board_str='\\n'.join([\n{board_str}\n]))".format(
            klass=self.__class__.__name__,
            board_str=textwrap.indent(
                ",\n".join(["'{0}'".format(l) for l in str(self).split("\n")]), "    "
            ),
        )

    @property
    def width(self) -> int:
        return self.graph.board_width

    @property
    def height(self) -> int:
        return self.graph.board_height

    @property
    def size(self) -> int:
        return self.graph.board_width * self.graph.board_height

    def neighbor(self, src: int, direction: Direction) -> Optional[int]:
        """
        Calculates neighbor vertex index in ``direction``

        Returns:
            neighbor position in ``direction`` or None if neighbor position in
            ``direction`` would lead of board

        Raises:
            IndexError: if ``from_position`` is out of board position
        """
        return self.graph.neighbor(src, direction)

    def wall_neighbors(self, src: int) -> List[int]:
        return self.graph.wall_neighbors(src)

    def all_neighbors(self, src: int) -> List[int]:
        return self.graph.all_neighbors(src)

    def clear(self):
        """Empties all board cells."""
        for vertex in range(0, self.size):
            self[vertex].clear()

    def mark_play_area(self):
        """
        Marks all BoardCell that are playable (reachable by any box or pusher).
        """
        self.graph.mark_play_area()

    def positions_reachable_by_pusher(
        self, pusher_position: int, excluded_positions: Optional[Positions] = None
    ) -> List[int]:
        """
        Returns:
            list of positions that are reachable by pusher standing on ``position``
        """
        return self.graph.positions_reachable_by_pusher(
            pusher_position, excluded_positions
        )

    def normalized_pusher_position(
        self, pusher_position: int, excluded_positions: Optional[Positions] = None
    ) -> int:
        """
        Returns:
            Top-left position reachable by pusher
        """
        return self.graph.normalized_pusher_position(
            pusher_position, excluded_positions
        )

    def path_destination(self, src: int, directions: List[Direction]):
        return self.graph.path_destination(src, directions)

    def find_jump_path(self, src: int, dst: int) -> List[int]:
        """
        Returns:
            list of positions through which pusher must pass when jumping
        """
        return self.graph.find_jump_path(src, dst)

    def find_move_path(self, src: int, dst: int) -> List[int]:
        """
        Returns:
            list of positions through which pusher must pass when moving without
            pushing boxes
        """
        return self.graph.find_move_path(src, dst)

    def cell_orientation(self, position: int) -> CellOrientation:
        return self.tessellation.cell_orientation(position, self.width, self.height)

    def positions_path_to_directions_path(self, positions: Positions) -> Directions:
        """
        Converts path expressed as vertices' indexes to one expressed as
        :class:`.Direction`
        """
        return self.graph.positions_path_to_directions_path(positions)

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

    def resize(self, new_width: int, new_height: int):
        """
        In-place resizing of board.

        Adds or removes rows and columns.
        """
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
            self.graph.reconfigure_edges(self.tessellation)

    def resize_and_center(self, new_width: int, new_height: int):
        """
        In-place resizing of board.

        Adds or removes rows and columns keeping existing board centered inside of new
        one.
        """
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

            if (right, bottom) != (0, 0):
                self.resize(self.width + right, self.height + bottom)
            else:
                self.graph.reconfigure_edges(self.tessellation)

    def trim(self):
        """
        In-place resizing of board.

        Removes blank rows and columns.
        """
        old_width = self.width
        old_height = self.height

        self._resizer.trim_top(reconfigure_edges=False)
        self._resizer.trim_bottom(reconfigure_edges=False)
        self._resizer.trim_left(reconfigure_edges=False)
        self._resizer.trim_right(reconfigure_edges=False)

        if old_width != self.width or old_height != old_height:
            self.graph.reconfigure_edges(self.tessellation)

    @classmethod
    def _cleaned_board_lines(cls, board: Optional[str]) -> List[str]:
        """
        Converts line into width-normalized, decoded list of board lines suitable for
        conversion into proper board object.
        """
        if is_blank(board):
            return []

        if not Puzzle.is_board(board):
            raise ValueError("Illegal characters found in board string")

        return cls._normalize_width(Rle.decode(board).split("\n"))

    @classmethod
    def _normalize_width(cls, string_list: List[str], fill_chr: str = " "):
        """
        Normalizes length of strings in ``string_list``.

        All strings are modified to be as long as the longest one in list. Missing
        characters in string are appended using ``fill_chr``.
        """
        width = cls._calculate_width(string_list)
        return [l + (fill_chr * (width - len(l))) for l in string_list]

    @classmethod
    def _calculate_width(cls, string_list: List[str]) -> int:
        """Width of list of strings as length of longest string in that list."""
        width = 0
        for line in string_list:
            if len(line) > width:
                width = len(line)
        return width

    def _reconfigure_edges(self):
        """Recreate all edges using :attr:`.tessellation`."""
        self.graph.reconfigure_edges(self.tessellation)

    def _reinit(self, width: int, height: int, reconfigure_edges=True):
        self._graph = BoardGraph(width, height, self.tessellation.graph_type)

        if reconfigure_edges:
            self.graph.reconfigure_edges(self.tessellation)

    def _reinit_with_string(self, board_str: Optional[str], reconfigure_edges=True):
        if not is_blank(board_str):
            board_rows = self._parse_string(board_str)
            height = len(board_rows)
            width = len(board_rows[0]) if height > 0 else 0
            self._reinit(width, height, reconfigure_edges)
            for y, row in enumerate(board_rows):
                for x, character in enumerate(row):
                    self.graph[index_1d(x, y, self.width)] = character


class VariantBoardResizer(metaclass=ABCMeta):
    """
    Implements board graph transformations related to adding/removing board rows and
    columns.
    """

    def __init__(self, variant_board: VariantBoard):
        self.board = variant_board

    def add_row_top(self, reconfigure_edges: bool):
        old_body = self.board.graph
        old_height = self.board.height

        self.board._reinit(
            self.board.width, self.board.height + 1, reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, old_height):
                self.board[index_1d(x, y + 1, self.board.width)] = str(
                    old_body[index_1d(x, y, self.board.width)]
                )

    def add_row_bottom(self, reconfigure_edges: bool):
        old_body = self.board.graph
        old_height = self.board.height

        self.board._reinit(
            self.board.width, self.board.height + 1, reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, old_height):
                self.board[index_1d(x, y, self.board.width)] = str(
                    old_body[index_1d(x, y, self.board.width)]
                )

    def add_column_left(self, reconfigure_edges: bool):
        old_body = self.board.graph
        old_width = self.board.width

        self.board._reinit(
            self.board.width + 1, self.board.height, reconfigure_edges=reconfigure_edges
        )

        for x in range(0, old_width):
            for y in range(0, self.board.height):
                self.board[index_1d(x + 1, y, self.board.width)] = str(
                    old_body[index_1d(x, y, old_width)]
                )

    def add_column_right(self, reconfigure_edges: bool):
        old_body = self.board.graph
        old_width = self.board.width

        self.board._reinit(
            self.board.width + 1, self.board.height, reconfigure_edges=reconfigure_edges
        )

        for x in range(0, old_width):
            for y in range(0, self.board.height):
                self.board[index_1d(x, y, self.board.width)] = str(
                    old_body[index_1d(x, y, old_width)]
                )

    def remove_row_top(self, reconfigure_edges: bool):
        old_body = self.board.graph

        self.board._reinit(
            self.board.width, self.board.height - 1, reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[index_1d(x, y, self.board.width)] = str(
                    old_body[index_1d(x, y + 1, self.board.width)]
                )

    def remove_row_bottom(self, reconfigure_edges: bool):
        old_body = self.board.graph

        self.board._reinit(
            self.board.width, self.board.height - 1, reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[index_1d(x, y, self.board.width)] = str(
                    old_body[index_1d(x, y, self.board.width)]
                )

    def remove_column_left(self, reconfigure_edges: bool):
        old_body = self.board.graph
        old_width = self.board.width

        self.board._reinit(
            self.board.width - 1, self.board.height, reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[index_1d(x, y, self.board.width)] = str(
                    old_body[index_1d(x + 1, y, old_width)]
                )

    def remove_column_right(self, reconfigure_edges: bool):
        old_body = self.board.graph
        old_width = self.board.width

        self.board._reinit(
            self.board.width - 1, self.board.height, reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[index_1d(x, y, self.board.width)] = str(
                    old_body[index_1d(x, y, old_width)]
                )

    def trim_left(self, reconfigure_edges: bool):
        amount = self.board.width
        for y in range(0, self.board.height):
            border_found = False
            for x in range(0, self.board.width):
                border_found = self.board[
                    index_1d(x, y, self.board.width)
                ].is_border_element
                if border_found and x < amount:
                    amount = x
                    break

        for _ in range(0, amount):
            self.remove_column_left(reconfigure_edges=False)

        if reconfigure_edges:
            self.board.graph.reconfigure_edges(self.board.tessellation)

    def trim_right(self, reconfigure_edges: bool):
        self.reverse_columns(reconfigure_edges=False)
        self.trim_left(reconfigure_edges=False)
        self.reverse_columns(reconfigure_edges=False)

        if reconfigure_edges:
            self.board.graph.reconfigure_edges(self.board.tessellation)

    def trim_top(self, reconfigure_edges: bool):
        amount = self.board.height
        for x in range(0, self.board.width):
            border_found = False
            for y in range(0, self.board.height):
                border_found = self.board[
                    index_1d(x, y, self.board.width)
                ].is_border_element
                if border_found:
                    if y < amount:
                        amount = y
                    break

        for _ in range(0, amount):
            self.remove_row_top(reconfigure_edges=False)

        if reconfigure_edges:
            self.board.graph.reconfigure_edges(self.board.tessellation)

    def trim_bottom(self, reconfigure_edges: bool):
        self.reverse_rows(reconfigure_edges=False)
        self.trim_top(reconfigure_edges=False)
        self.reverse_rows(reconfigure_edges=False)

        if reconfigure_edges:
            self.board.graph.reconfigure_edges(self.board.tessellation)

    def reverse_rows(self, reconfigure_edges: bool):
        old_body = self.board.graph

        self.board._reinit(self.board.width, self.board.height, reconfigure_edges=False)

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[index_1d(x, y, self.board.width)] = str(
                    old_body[index_1d(x, self.board.height - y - 1, self.board.width)]
                )

        if reconfigure_edges:
            self.board.graph.reconfigure_edges(self.board.tessellation)

    def reverse_columns(self, reconfigure_edges: bool):
        old_body = self.board.graph

        self.board._reinit(self.board.width, self.board.height, reconfigure_edges=False)

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[index_1d(x, y, self.board.width)] = str(
                    old_body[index_1d(self.board.width - x - 1, y, self.board.width)]
                )

        if reconfigure_edges:
            self.board.graph.reconfigure_edges(self.board.tessellation)
