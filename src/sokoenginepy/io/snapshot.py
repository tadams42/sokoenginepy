from __future__ import annotations

from typing import TYPE_CHECKING, Final, List, Optional

from .rle import Rle
from .utilities import contains_only_digits_and_spaces, is_blank

if TYPE_CHECKING:
    from ..game import BaseTessellation, PusherStep, Tessellation
    from .snapshot_parsing import MovementTokens


class Snapshot:
    """
    Base class for game snapshots and accompanying metadata.

    Game snapshot is sequence of pusher steps representing actual steps, jumps (in
    reverse solving mode) and pusher selections (in Multiban variant).
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
    def is_move_step(cls, character: str) -> bool:
        from .snapshot_parsing import Constants

        return character in Constants.MOVE_CHARACTERS

    @classmethod
    def is_push_step(cls, character: str) -> bool:
        from .snapshot_parsing import Constants

        return character in Constants.PUSH_CHARACTERS

    @classmethod
    def is_pusher_step(cls, character: str) -> bool:
        return cls.is_move_step(character) or cls.is_push_step(character)

    @classmethod
    def is_marker(cls, character: str) -> bool:
        from .snapshot_parsing import Constants

        return character in Constants.MARKERS

    @classmethod
    def is_snapshot(cls, line: str) -> bool:
        """
        True if ``line`` contains only:

        - movement characters
        - other snapshot characters (ie. jump markers)
        - Rle characters
        - spaces and newlines
        """
        from .snapshot_parsing import Constants

        return (
            not is_blank(line)
            and not contains_only_digits_and_spaces(line)
            and all(
                True if Constants.RE_SNAPSHOT_STRING.match(l) else False
                for l in line.splitlines()
            )
        )

    def __init__(self, tessellation: Tessellation, moves_data: str = ""):
        self.title: str = ""
        self.solver: str = ""
        self.notes: List[str] = []

        self._tessellation = tessellation
        self._tessellation_obj_val: Optional[BaseTessellation] = None

        if not is_blank(moves_data) and not self.is_snapshot(moves_data):
            raise ValueError("Invalid characters in snapshot string!")
        self._moves_data: str = moves_data or ""

        self._parsed_moves: MovementTokens = []
        self._was_parsed = False
        self._pushes_count: int = 0
        self._moves_count: int = 0
        self._jumps_count: int = 0
        self._is_reverse: bool = False

    def to_str(self, rle_encode=False) -> str:
        self._reparse_if_not_parsed()

        retv = "".join(str(_) for _ in self._parsed_moves)

        # Reverse snapshots must start with jump, even if it is empty one
        if self.is_reverse and (
            not self._parsed_moves
            or (self._parsed_moves and retv[0] != self.JUMP_BEGIN)
        ):
            retv = self.JUMP_BEGIN + self.JUMP_END + retv

        if rle_encode:
            retv = Rle.encode(retv)

        return retv

    def __str__(self):
        return self.to_str(rle_encode=False)

    def __repr__(self):
        klass = self.__class__.__name__
        return f'{klass}(moves_data="{self.to_str(rle_encode=False)}")'

    @property
    def tessellation(self) -> Tessellation:
        return self._tessellation

    @property
    def _tessellation_obj(self):
        from ..game import BaseTessellation

        if self._tessellation_obj_val is None:
            self._tessellation_obj_val = BaseTessellation.instance(self._tessellation)

        return self._tessellation_obj_val

    @property
    def moves_data(self) -> str:
        return self._moves_data

    @moves_data.setter
    def moves_data(self, rv: str):
        if not is_blank(rv) and not self.is_snapshot(rv):
            raise ValueError("Invalid characters in snapshot string!")
        self._moves_data = rv or ""
        self._was_parsed = False

    @property
    def pusher_steps(self) -> List[PusherStep]:
        """
        Game engine representation of pusher movement.
        """
        self._reparse_if_not_parsed()
        return sum(
            (_.pusher_steps(self._tessellation_obj) for _ in self._parsed_moves), []
        )

    @pusher_steps.setter
    def pusher_steps(self, rv: List[PusherStep]):
        """
        Warning:
            This will replace ``moves_data`` with ``rv`` converted to ``str``.
        """
        from .snapshot_parsing import Jump, PusherSelection, Steps

        i = 0
        iend = len(rv)

        self._parsed_moves = []
        self._pushes_count = 0
        self._moves_count = 0
        self._jumps_count = 0
        self._is_reverse = False
        self._was_parsed = True

        while i < iend:
            if rv[i].is_jump:
                jump = Jump("")
                while i < iend and rv[i].is_jump:
                    jump.data += self._tessellation_obj.pusher_step_to_char(rv[i])
                    if rv[i].is_current_pos:
                        jump.data += self.CURRENT_POSITION_CH
                    i += 1
                self._parsed_moves.append(jump)
                self._jumps_count += 1
                self._is_reverse = True
                self._moves_count += jump.moves_count

            elif rv[i].is_pusher_selection:
                pusher_selection = PusherSelection("")
                while i < iend and rv[i].is_pusher_selection:
                    pusher_selection.data += self._tessellation_obj.pusher_step_to_char(
                        rv[i]
                    )
                    if rv[i].is_current_pos:
                        pusher_selection.data += self.CURRENT_POSITION_CH
                    i += 1
                self._parsed_moves.append(pusher_selection)

            else:
                steps = Steps("")
                while i < iend and not rv[i].is_jump and not rv[i].is_pusher_selection:
                    steps.data += self._tessellation_obj.pusher_step_to_char(rv[i])
                    if rv[i].is_current_pos:
                        steps.data += self.CURRENT_POSITION_CH
                    i += 1
                self._parsed_moves.append(steps)
                self._pushes_count += steps.pushes_count
                self._moves_count += steps.moves_count

        self._moves_data = self.to_str(rle_encode=False)

    @property
    def pushes_count(self) -> int:
        """
        Count of box pushing steps.
        """
        self._reparse_if_not_parsed()
        return self._pushes_count

    @property
    def moves_count(self) -> int:
        """
        Count of steps that are:
            - not pushing a box
            - jumping (in reverse solving mode)
        """
        self._reparse_if_not_parsed()
        return self._moves_count

    @property
    def jumps_count(self) -> int:
        """
        Count of sequences of steps that are jumps. Jumps are possible when board is
        being solved in reverse mode.
        """
        self._reparse_if_not_parsed()
        return self._jumps_count

    @property
    def is_reverse(self) -> bool:
        """
        True if snapshot contains any jumps.
        """
        self._reparse_if_not_parsed()
        return self._is_reverse

    def _reparse_if_not_parsed(self):
        if not self._was_parsed:
            self._reparse()

    def _reparse(self):
        from .snapshot_parsing import Jump, Parser

        self._parsed_moves = []
        self._pushes_count = 0
        self._moves_count = 0
        self._jumps_count = 0
        self._is_reverse = False

        self._parsed_moves = Parser.parse(self._moves_data)

        for _ in self._parsed_moves:
            if isinstance(_, Jump):
                self._jumps_count += 1
                self._is_reverse = True
            self._moves_count += _.moves_count
            self._pushes_count += _.pushes_count

        self._was_parsed = True
