import re
from functools import reduce
from operator import add, or_
from typing import Final, List, Optional, Set

from .rle import Rle
from .utilities import contains_only_digits_and_spaces, is_blank


class Snapshot:
    """
    Recording of pusher movement with accompanying metadata.
    """

    # Characters used in textual representation of game snapshot. Not all game variants
    # use all characters. Also, for different game variants, same character may have
    # different meaning (represent different direction of movement).

    l: Final[str] = "l"
    u: Final[str] = "u"
    r: Final[str] = "r"
    d: Final[str] = "d"
    L: Final[str] = "L"
    U: Final[str] = "U"
    R: Final[str] = "R"
    D: Final[str] = "D"
    w: Final[str] = "w"
    W: Final[str] = "W"
    e: Final[str] = "e"
    E: Final[str] = "E"
    n: Final[str] = "n"
    N: Final[str] = "N"
    s: Final[str] = "s"
    S: Final[str] = "S"

    JUMP_BEGIN: Final[str] = "["
    JUMP_END: Final[str] = "]"
    PUSHER_CHANGE_BEGIN: Final[str] = "{"
    PUSHER_CHANGE_END: Final[str] = "}"
    CURRENT_POSITION_CH: Final[str] = "*"

    @classmethod
    def is_pusher_step(cls, character: str) -> bool:
        return character in _MOVEMENT_CHARACTERS

    @classmethod
    def is_snapshot(cls, line: str) -> bool:
        """
        True if ``line`` contains only:

        - movement characters
        - other snapshot characters (ie. jump markers)
        - Rle characters
        - spaces and newlines
        """
        return (
            not is_blank(line)
            and not contains_only_digits_and_spaces(line)
            and all(
                True if _RE_SNAPSHOT_STRING.match(l) else False
                for l in line.splitlines()
            )
        )

    @classmethod
    def cleaned_moves(cls, line: str) -> str:
        if not cls.is_snapshot(line):
            raise ValueError("Illegal characters found in snapshot string")

        return Rle.decode(line)

    def __init__(
        self,
        id: int = 0,
        moves: str = "",
        title: str = "",
        duration: Optional[str] = None,
        solver: str = "",
        created_at: str = "",
        updated_at: str = "",
        notes: Optional[List[str]] = None,
    ):
        self.id = id
        self._moves = moves
        self.title = title
        self.duration = duration
        self.solver = solver
        self.notes: List[str] = notes or []
        self.created_at = created_at
        self.updated_at = updated_at

        self._pushes_count: Optional[int] = None
        self._moves_count: Optional[int] = None
        self._is_reverse: Optional[int] = None

    @property
    def moves(self):
        return self._moves

    @moves.setter
    def moves(self, rv):
        self._moves = rv
        self._pushes_count = None
        self._moves_count = None
        self._is_reverse = None

    @property
    def pushes_count(self) -> int:
        if self._pushes_count is None:
            self._pushes_count = reduce(
                add,
                [
                    1 if (self.is_pusher_step(chr) and chr.isupper()) else 0
                    for chr in self.moves
                ],
                0,
            )

        return self._pushes_count

    @property
    def moves_count(self) -> int:
        """
        This is just an approximation. Since snapshot is not fully parsed, this method
        may also count pusher steps that are part of jumps and / or pusher selections.
        """
        if self._moves_count is None:
            self._moves_count = reduce(
                add,
                [
                    1 if (self.is_pusher_step(chr) and chr.islower()) else 0
                    for chr in self.moves
                ],
                0,
            )
        return self._moves_count

    @property
    def is_reverse(self) -> bool:
        return reduce(
            or_,
            [chr == self.JUMP_BEGIN or chr == self.JUMP_END for chr in self.moves],
            False,
        )


_MOVEMENT_CHARACTERS: Set[str] = {
    Snapshot.l,
    Snapshot.u,
    Snapshot.r,
    Snapshot.d,
    Snapshot.L,
    Snapshot.U,
    Snapshot.R,
    Snapshot.D,
    Snapshot.W,
    Snapshot.W,
    Snapshot.e,
    Snapshot.E,
    Snapshot.n,
    Snapshot.N,
    Snapshot.s,
    Snapshot.S,
}
_CHARACTERS: Set[str] = _MOVEMENT_CHARACTERS.union(
    {
        Snapshot.JUMP_BEGIN,
        Snapshot.JUMP_END,
        Snapshot.PUSHER_CHANGE_BEGIN,
        Snapshot.PUSHER_CHANGE_END,
        Snapshot.CURRENT_POSITION_CH,
    }
)
_RE_SNAPSHOT_STRING = re.compile(
    r"^([0-9\s"
    + re.escape("".join(_CHARACTERS))
    + re.escape("".join(Rle.DELIMITERS))
    + "])*$"
)
