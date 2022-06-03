from __future__ import annotations

import re
from functools import reduce
from operator import add
from typing import Final, List, Optional, Set

from .puzzle_types import PuzzleTypes
from .rle import Rle
from .snapshot import Snapshot
from .utilities import contains_only_digits_and_spaces, is_blank


class Puzzle:
    """
    Textual representation of game board with all its meta data and snapshots.
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

    def __init__(
        self,
        id: int = 0,
        board: str = "",
        puzzle_type: Optional[PuzzleTypes] = PuzzleTypes.SOKOBAN,
        title: str = "",
        author: str = "",
        boxorder: str = "",
        goalorder: str = "",
        notes: Optional[List[str]] = None,
        snapshots: Optional[List[Snapshot]] = None,
        created_at: str = "",
        updated_at: str = "",
    ):
        self.id: int = id
        self._board: str = board
        self.title = title
        self.author = author
        self.boxorder = boxorder
        self.goalorder = goalorder
        self.notes: List[str] = notes or []
        self.snapshots: List[Snapshot] = snapshots or []
        self.created_at = created_at
        self.updated_at = updated_at
        self.puzzle_type: PuzzleTypes = puzzle_type or PuzzleTypes.SOKOBAN

        self._pushers_count: Optional[int] = None
        self._boxes_count: Optional[int] = None
        self._goals_count: Optional[int] = None

    @classmethod
    def is_pusher(cls, character: str) -> bool:
        return (
            character == cls.PUSHER
            or character == cls.ALT_PUSHER1
            or character == cls.ALT_PUSHER2
            or character == cls.PUSHER_ON_GOAL
            or character == cls.ALT_PUSHER_ON_GOAL1
            or character == cls.ALT_PUSHER_ON_GOAL2
        )

    @classmethod
    def is_box(cls, character: str) -> bool:
        return (
            character == cls.BOX
            or character == cls.ALT_BOX1
            or character == cls.BOX_ON_GOAL
            or character == cls.ALT_BOX_ON_GOAL1
        )

    @classmethod
    def is_goal(cls, character: str) -> bool:
        return (
            character == cls.GOAL
            or character == cls.ALT_GOAL1
            or character == cls.BOX_ON_GOAL
            or character == cls.ALT_BOX_ON_GOAL1
            or character == cls.PUSHER_ON_GOAL
            or character == cls.ALT_PUSHER_ON_GOAL1
            or character == cls.ALT_PUSHER_ON_GOAL2
        )

    @classmethod
    def is_empty_floor(cls, character: str) -> bool:
        return (
            character == cls.FLOOR
            or character == cls.VISIBLE_FLOOR
            or character == cls.ALT_VISIBLE_FLOOR1
        )

    @classmethod
    def is_wall(cls, character: str) -> bool:
        return character == cls.WALL

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

    @property
    def board(self) -> str:
        return self._board

    @board.setter
    def board(self, rv: str):
        self._board = rv
        self._pushers_count = None
        self._boxes_count = None
        self._goals_count = None

    def clear(self):
        self.board = ""
        self.title = ""
        self.author = ""
        self.boxorder = ""
        self.goalorder = ""
        self.notes = []
        self.snapshots = []
        self.created_at = ""
        self.updated_at = ""

        self._pushers_count: Optional[int] = None
        self._boxes_count: Optional[int] = None
        self._goals_count: Optional[int] = None

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

    def reformatted(
        self,
        use_visible_floor: bool = False,
        break_long_lines_at: int = 80,
        rle_encode: bool = False,
    ) -> str:
        return self.board


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
    + re.escape("".join(Rle.DELIMITERS))
    + "])*$"
)
