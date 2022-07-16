from __future__ import annotations

import enum
import re
import textwrap
from functools import reduce
from operator import add
from typing import TYPE_CHECKING, Final, List, Optional, Set

from .rle import Rle
from .snapshot import Snapshot
from .utilities import contains_only_digits_and_spaces, is_blank

if TYPE_CHECKING:
    from ..game import Tessellation
    from ..game.base_tessellation import BaseTessellation
    from .puzzle_parsing import PuzzleParser, PuzzlePrinter, PuzzleResizer


class CellOrientation(enum.Enum):
    """
    Dynamic board cell property that depends on cell position in some tessellations.
    ie. in Trioban, origin of coordinate system is triangle pointing upwards. This means
    that orientation of all other triangles depends on orientation of origin.
    """

    DEFAULT = 0
    TRIANGLE_DOWN = 1
    OCTAGON = 2


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

    WALL: Final[str] = "#"
    PUSHER: Final[str] = "@"
    PUSHER_ON_GOAL: Final[str] = "+"
    BOX: Final[str] = "$"
    BOX_ON_GOAL: Final[str] = "*"
    GOAL: Final[str] = "."
    FLOOR: Final[str] = " "
    VISIBLE_FLOOR: Final[str] = "-"
    ALT_PUSHER1: Final[str] = "p"
    ALT_PUSHER2: Final[str] = "m"
    ALT_PUSHER_ON_GOAL1: Final[str] = "P"
    ALT_PUSHER_ON_GOAL2: Final[str] = "M"
    ALT_BOX1: Final[str] = "b"
    ALT_BOX_ON_GOAL1: Final[str] = "B"
    ALT_GOAL1: Final[str] = "o"
    ALT_VISIBLE_FLOOR1: Final[str] = "_"

    @classmethod
    def is_pusher(cls, character: str) -> bool:
        return character in (
            cls.PUSHER,
            cls.ALT_PUSHER1,
            cls.ALT_PUSHER2,
            cls.PUSHER_ON_GOAL,
            cls.ALT_PUSHER_ON_GOAL1,
            cls.ALT_PUSHER_ON_GOAL2,
        )

    @classmethod
    def is_box(cls, character: str) -> bool:
        return character in (
            cls.BOX,
            cls.ALT_BOX1,
            cls.BOX_ON_GOAL,
            cls.ALT_BOX_ON_GOAL1,
        )

    @classmethod
    def is_goal(cls, character: str) -> bool:
        return character in (
            cls.GOAL,
            cls.ALT_GOAL1,
            cls.BOX_ON_GOAL,
            cls.ALT_BOX_ON_GOAL1,
            cls.PUSHER_ON_GOAL,
            cls.ALT_PUSHER_ON_GOAL1,
            cls.ALT_PUSHER_ON_GOAL2,
        )

    @classmethod
    def is_empty_floor(cls, character: str) -> bool:
        return character in (
            cls.FLOOR,
            cls.VISIBLE_FLOOR,
            cls.ALT_VISIBLE_FLOOR1,
        )

    @classmethod
    def is_wall(cls, character: str) -> bool:
        return character == cls.WALL

    @classmethod
    def is_border_element(cls, character: str) -> bool:
        return character in (
            cls.WALL,
            cls.BOX_ON_GOAL,
            cls.ALT_BOX_ON_GOAL1,
        )

    @classmethod
    def is_puzzle_element(cls, character: str) -> bool:
        return (
            cls.is_empty_floor(character)
            or cls.is_wall(character)
            or cls.is_pusher(character)
            or cls.is_box(character)
            or cls.is_goal(character)
        )

    @classmethod
    def is_board(cls, line: Optional[str]) -> bool:
        """
        Checks if line contains only characters legal in textual representation of
        boards.

        Note:
            Doesn't check if it actually contains legal board, it only checks that
            there are no illegal characters.
        """
        return not contains_only_digits_and_spaces(line) and reduce(
            lambda x, y: x and y,
            [True if _RE_BOARD_STRING.match(l) else False for l in line.splitlines()],
            True,
        )

    @classmethod
    def is_sokoban_plus(cls, line: str) -> bool:
        return contains_only_digits_and_spaces(line) and not is_blank(line)

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
        self._tessellation_obj_val: Optional[BaseTessellation] = None

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
            if not self.is_board(board):
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
        from ..game.base_tessellation import BaseTessellation

        if self._tessellation_obj_val is None:
            self._tessellation_obj_val = BaseTessellation.instance(self._tessellation)

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

        if not self.is_puzzle_element(c):
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
                    "'{0}'".format(l)
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
        if not self.is_board(rv):
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
                add, [1 if self.is_pusher(chr) else 0 for chr in self.board], 0
            )
        return self._pushers_count

    @property
    def boxes_count(self) -> int:
        if self._boxes_count is None:
            self._boxes_count = reduce(
                add, [1 if self.is_box(chr) else 0 for chr in self.board], 0
            )

        return self._boxes_count

    @property
    def goals_count(self) -> int:
        if self._goals_count is None:
            self._goals_count = reduce(
                add, [1 if self.is_goal(chr) else 0 for chr in self.board], 0
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
        from ..game import Tessellation
        from .hexoban import Hexoban
        from .octoban import Octoban
        from .sokoban import Sokoban
        from .trioban import Trioban

        if self._tessellation == Tessellation.SOKOBAN:
            return Sokoban.resizer()
        if self._tessellation == Tessellation.TRIOBAN:
            return Trioban.resizer()
        if self._tessellation == Tessellation.HEXOBAN:
            return Hexoban.resizer()
        if self._tessellation == Tessellation.OCTOBAN:
            return Octoban.resizer()
        raise ValueError(f"Unknown tessellation {self._tessellation}")

    @property
    def _parser(self) -> PuzzleParser:
        from ..game import Tessellation
        from .hexoban import Hexoban
        from .octoban import Octoban
        from .sokoban import Sokoban
        from .trioban import Trioban

        if self._tessellation == Tessellation.SOKOBAN:
            return Sokoban.parser()
        if self._tessellation == Tessellation.TRIOBAN:
            return Trioban.parser()
        if self._tessellation == Tessellation.HEXOBAN:
            return Hexoban.parser()
        if self._tessellation == Tessellation.OCTOBAN:
            return Octoban.parser()
        raise ValueError(f"Unknown tessellation {self._tessellation}")

    @property
    def _printer(self) -> PuzzlePrinter:
        from ..game import Tessellation
        from .hexoban import Hexoban
        from .octoban import Octoban
        from .sokoban import Sokoban
        from .trioban import Trioban

        if self._tessellation == Tessellation.SOKOBAN:
            return Sokoban.printer()
        if self._tessellation == Tessellation.TRIOBAN:
            return Trioban.printer()
        if self._tessellation == Tessellation.HEXOBAN:
            return Hexoban.printer()
        if self._tessellation == Tessellation.OCTOBAN:
            return Octoban.printer()
        raise ValueError(f"Unknown tessellation {self._tessellation}")


_CHARACTERS: Set[str] = {
    Puzzle.WALL,
    Puzzle.PUSHER,
    Puzzle.PUSHER_ON_GOAL,
    Puzzle.BOX,
    Puzzle.BOX_ON_GOAL,
    Puzzle.GOAL,
    Puzzle.FLOOR,
    Puzzle.VISIBLE_FLOOR,
    Puzzle.ALT_PUSHER1,
    Puzzle.ALT_PUSHER2,
    Puzzle.ALT_PUSHER_ON_GOAL1,
    Puzzle.ALT_PUSHER_ON_GOAL2,
    Puzzle.ALT_BOX1,
    Puzzle.ALT_BOX_ON_GOAL1,
    Puzzle.ALT_GOAL1,
    Puzzle.ALT_VISIBLE_FLOOR1,
}
_RE_BOARD_STRING = re.compile(
    r"^([0-9\s"
    + re.escape("".join(_CHARACTERS))
    + re.escape("".join({Rle.GROUP_START, Rle.GROUP_END, Rle.EOL}))
    + "])*$"
)
