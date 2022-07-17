from __future__ import annotations

import textwrap
from functools import reduce
from operator import add
from typing import Final, List, Optional

from ..common import (
    CellOrientation,
    Characters,
    Tessellation,
    TessellationImpl,
    is_blank,
)
from .hexoban_io import HexobanIo
from .octoban_io import OctobanIo
from .puzzle_parsing import PuzzleParser, PuzzlePrinter, PuzzleResizer
from .snapshot import Snapshot
from .sokoban_io import SokobanIo
from .trioban_io import TriobanIo


class Puzzle:
    """
    Base class for game puzzles.

    Game puzzle is representation of game board together with all of its meta data and
    snapshots. It implements:

    - parsing board data from text
    - editing board: setting individual cells, resizing, trimming, ...

    All positions used are 1D array indexes.

    To convert 2D board coordinates into 1D array indexes, use `.index_1d`. To convert
    1D array indexes into board 2D coordinates, use one of `.index_row`, `.index_x`
    `.index_column` and `.index_y`.

    Arguments:
        width: number of columns
        height: number of rows
        board: If not blank, it will be parsed and board will be created from it,
            ignoring ``width`` and ``height``.
    """

    WALL: Final[str] = Characters.WALL
    PUSHER: Final[str] = Characters.PUSHER
    PUSHER_ON_GOAL: Final[str] = Characters.PUSHER_ON_GOAL
    BOX: Final[str] = Characters.BOX
    BOX_ON_GOAL: Final[str] = Characters.BOX_ON_GOAL
    GOAL: Final[str] = Characters.GOAL
    FLOOR: Final[str] = Characters.FLOOR
    VISIBLE_FLOOR: Final[str] = Characters.VISIBLE_FLOOR

    def __init__(
        self,
        tessellation: Tessellation,
        width: int = 0,
        height: int = 0,
        board: Optional[str] = None,
    ):
        if width < 0:
            raise ValueError(f"Board width {width} is invalid value!")

        if height < 0:
            raise ValueError(f"Board height {height} is invalid value!")

        self.title = ""
        self.author = ""
        self.boxorder = ""
        self.goalorder = ""
        self.notes = ""
        self.snapshots: List[Snapshot] = []

        self._pushers_count: Optional[int] = None
        self._boxes_count: Optional[int] = None
        self._goals_count: Optional[int] = None

        self._tessellation: Tessellation = tessellation
        self._tessellation_obj_val: Optional[TessellationImpl] = None

        self._width: int
        self._height: int
        self._was_parsed: bool
        self._original_board: str
        # not str but list of single character strings. str is immutable and we need to
        # be able to modify individual board cells.
        self._parsed_board: List[str]

        if is_blank(board) or board is None:
            self._width = width
            self._height = height
            if self._width < 0 or self._height < 0:
                raise ValueError("Board dimensions can't be less than zero!")
            self._was_parsed = True
            self._original_board = ""
            self._parsed_board = width * height * [self.VISIBLE_FLOOR]

        else:
            if not Characters.is_board(board):
                raise ValueError("Invalid characters in board string!")
            self._width = 0
            self._height = 0
            self._was_parsed = False
            self._original_board = board
            self._parsed_board = []

    @property
    def tessellation(self) -> Tessellation:
        return self._tessellation

    @property
    def has_sokoban_plus(self) -> bool:
        return not is_blank(self.boxorder) or not is_blank(self.goalorder)

    @property
    def _tessellation_obj(self):
        if self._tessellation_obj_val is None:
            self._tessellation_obj_val = TessellationImpl.instance(self._tessellation)

        return self._tessellation_obj_val

    def cell_orientation(self, pos: int) -> CellOrientation:
        self._reparse_if_not_parsed()
        return self._tessellation_obj.cell_orientation(pos, self.width, self.height)

    def __getitem__(self, position: int) -> str:
        if position < 0:
            raise IndexError(f"Position {position} is invalid value!")

        self._reparse_if_not_parsed()
        return self._parsed_board[position]

    def __setitem__(self, position: int, c: str):
        if position < 0:
            raise IndexError(f"Position {position} is invalid value!")

        if not Characters.is_puzzle_element(c):
            raise ValueError(f"'{c}' is not a board character!")

        self._reparse_if_not_parsed()
        self._parsed_board[position] = c

    def __contains__(self, position: int):
        self._reparse_if_not_parsed()
        return position < len(self._parsed_board)

    def __str__(self):
        return self.to_board_str(use_visible_floor=False)

    def __repr__(self):
        board = textwrap.indent(
            ",\n".join(
                [
                    f"'{l}'"
                    for l in self.to_board_str(use_visible_floor=True).split("\n")
                ]
            ),
            "    ",
        )
        klass = self.__class__.__name__
        tess = self._tessellation

        return f"{klass}({tess}, board='\\n'.join([\n{board}\n]))"

    def to_board_str(self, use_visible_floor=False, rle_encode=False) -> str:
        """Formatted output of parsed and validated board."""
        self._reparse_if_not_parsed()
        return self._printer.print(
            self._parsed_board, self.width, self.height, use_visible_floor, rle_encode
        )

    @property
    def board(self) -> str:
        """Original, unparsed board."""
        return self._original_board

    @board.setter
    def board(self, rv: str):
        if not Characters.is_board(rv):
            raise ValueError("Invalid characters in board string!")
        self._original_board = rv
        self._was_parsed = False
        self._pushers_count = None
        self._boxes_count = None
        self._goals_count = None

    @property
    def internal_board(self) -> str:
        """Internal, parsed board. For debugging purposes."""
        self._reparse_if_not_parsed()
        return "".join(self._parsed_board)

    @property
    def width(self) -> int:
        self._reparse_if_not_parsed()
        return self._width

    @property
    def height(self) -> int:
        self._reparse_if_not_parsed()
        return self._height

    @property
    def size(self) -> int:
        return self.width * self.height

    @property
    def pushers_count(self) -> int:
        if self._pushers_count is None:
            self._pushers_count = reduce(
                add, [1 if Characters.is_pusher(c) else 0 for c in self.board], 0
            )
        return self._pushers_count

    @property
    def boxes_count(self) -> int:
        if self._boxes_count is None:
            self._boxes_count = reduce(
                add, [1 if Characters.is_box(c) else 0 for c in self.board], 0
            )

        return self._boxes_count

    @property
    def goals_count(self) -> int:
        if self._goals_count is None:
            self._goals_count = reduce(
                add, [1 if Characters.is_goal(c) else 0 for c in self.board], 0
            )
        return self._goals_count

    def add_row_top(self):
        self._reparse_if_not_parsed()
        self._parsed_board, self._width, self._height = self._resizer.add_row_top(
            self._parsed_board, self.width, self.height
        )

    def add_row_bottom(self):
        self._reparse_if_not_parsed()
        (
            self._parsed_board,
            self._width,
            self._height,
        ) = self._resizer.add_row_bottom(self._parsed_board, self.width, self.height)

    def add_column_left(self):
        self._reparse_if_not_parsed()
        (
            self._parsed_board,
            self._width,
            self._height,
        ) = self._resizer.add_column_left(self._parsed_board, self.width, self.height)

    def add_column_right(self):
        self._reparse_if_not_parsed()
        (
            self._parsed_board,
            self._width,
            self._height,
        ) = self._resizer.add_column_right(self._parsed_board, self.width, self.height)

    def remove_row_top(self):
        self._reparse_if_not_parsed()
        (
            self._parsed_board,
            self._width,
            self._height,
        ) = self._resizer.remove_row_top(self._parsed_board, self.width, self.height)

    def remove_row_bottom(self):
        self._reparse_if_not_parsed()
        (
            self._parsed_board,
            self._width,
            self._height,
        ) = self._resizer.remove_row_bottom(self._parsed_board, self.width, self.height)

    def remove_column_left(self):
        self._reparse_if_not_parsed()
        (
            self._parsed_board,
            self._width,
            self._height,
        ) = self._resizer.remove_column_left(
            self._parsed_board, self.width, self.height
        )

    def remove_column_right(self):
        self._reparse_if_not_parsed()
        (
            self._parsed_board,
            self._width,
            self._height,
        ) = self._resizer.remove_column_right(
            self._parsed_board, self.width, self.height
        )

    def trim_left(self):
        self._reparse_if_not_parsed()
        self._parsed_board, self._width, self._height = self._resizer.trim_left(
            self._parsed_board, self.width, self.height
        )

    def trim_right(self):
        self._reparse_if_not_parsed()
        self._parsed_board, self._width, self._height = self._resizer.trim_right(
            self._parsed_board, self.width, self.height
        )

    def trim_top(self):
        self._reparse_if_not_parsed()
        self._parsed_board, self._width, self._height = self._resizer.trim_top(
            self._parsed_board, self.width, self.height
        )

    def trim_bottom(self):
        self._reparse_if_not_parsed()
        self._parsed_board, self._width, self._height = self._resizer.trim_bottom(
            self._parsed_board, self.width, self.height
        )

    def reverse_rows(self):
        self._reparse_if_not_parsed()
        (
            self._parsed_board,
            self._width,
            self._height,
        ) = self._resizer.reverse_rows(self._parsed_board, self.width, self.height)

    def reverse_columns(self):
        self._reparse_if_not_parsed()
        (
            self._parsed_board,
            self._width,
            self._height,
        ) = self._resizer.reverse_columns(self._parsed_board, self.width, self.height)

    def resize(self, new_width: int, new_height: int):
        """
        In-place resizing of board.

        Adds or removes rows and columns.
        """
        if new_width < 0:
            raise ValueError(f"Board width {new_width} is invalid value!")
        if new_height < 0:
            raise ValueError(f"Board height {new_height} is invalid value!")

        self._reparse_if_not_parsed()
        old_width = self.width
        old_height = self.height

        if new_height != old_height:
            if new_height > old_height:
                amount = new_height - old_height
                for _ in range(0, amount):
                    self.add_row_bottom()
            else:
                amount = old_height - new_height
                for _ in range(0, amount):
                    self.remove_row_bottom()

        if new_width != old_width:
            if new_width > old_width:
                amount = new_width - old_width
                for _ in range(0, amount):
                    self.add_column_right()
            else:
                amount = old_width - new_width
                for _ in range(0, amount):
                    self.remove_column_right()

    def resize_and_center(self, new_width: int, new_height: int):
        """
        In-place resizing of board.

        Adds or removes rows and columns keeping existing board centered inside of new
        one.
        """
        if new_width < 0:
            raise ValueError(f"Board width {new_width} is invalid value!")
        if new_height < 0:
            raise ValueError(f"Board height {new_height} is invalid value!")

        self._reparse_if_not_parsed()
        left = right = top = bottom = 0

        if new_width > self.width:
            left = int((new_width - self.width) / 2)
            right = new_width - self.width - left

        if new_height > self.height:
            top = int((new_height - self.height) / 2)
            bottom = new_height - self.height - top

        if (left, right, top, bottom) != (0, 0, 0, 0):
            for _ in range(0, left):
                self.add_column_left()
            for _ in range(0, top):
                self.add_row_top()

            if (right, bottom) != (0, 0):
                self.resize(self.width + right, self.height + bottom)

    def trim(self):
        """
        In-place resizing of board.

        Removes outer, blank rows and columns.
        """
        self.trim_top()
        self.trim_bottom()
        self.trim_left()
        self.trim_right()

    def _reparse(self):
        if not is_blank(self._original_board):
            board_rows = self._parser.parse(self._original_board)
            self._height = len(board_rows)
            self._width = len(board_rows[0]) if self._height else 0
            self._parsed_board = sum((list(_) for _ in board_rows), [])
            for idx, val in enumerate(self._parsed_board):
                if val == self.FLOOR:
                    self._parsed_board[idx] = self.VISIBLE_FLOOR

        self._was_parsed = True

    def _reparse_if_not_parsed(self):
        if not self._was_parsed:
            self._reparse()

    @property
    def _resizer(self) -> PuzzleResizer:
        if self._tessellation == Tessellation.SOKOBAN:
            return SokobanIo.resizer()
        if self._tessellation == Tessellation.TRIOBAN:
            return TriobanIo.resizer()
        if self._tessellation == Tessellation.HEXOBAN:
            return HexobanIo.resizer()
        if self._tessellation == Tessellation.OCTOBAN:
            return OctobanIo.resizer()
        raise ValueError(f"Unknown tessellation {self._tessellation}")

    @property
    def _parser(self) -> PuzzleParser:
        if self._tessellation == Tessellation.SOKOBAN:
            return SokobanIo.parser()
        if self._tessellation == Tessellation.TRIOBAN:
            return TriobanIo.parser()
        if self._tessellation == Tessellation.HEXOBAN:
            return HexobanIo.parser()
        if self._tessellation == Tessellation.OCTOBAN:
            return OctobanIo.parser()
        raise ValueError(f"Unknown tessellation {self._tessellation}")

    @property
    def _printer(self) -> PuzzlePrinter:
        if self._tessellation == Tessellation.SOKOBAN:
            return SokobanIo.printer()
        if self._tessellation == Tessellation.TRIOBAN:
            return TriobanIo.printer()
        if self._tessellation == Tessellation.HEXOBAN:
            return HexobanIo.printer()
        if self._tessellation == Tessellation.OCTOBAN:
            return OctobanIo.printer()
        raise ValueError(f"Unknown tessellation {self._tessellation}")
