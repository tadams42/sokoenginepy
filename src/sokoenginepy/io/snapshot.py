from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Final

from ..common import Characters, Tessellation, TessellationImpl, is_blank
from .rle import Rle
from .snapshot_parsing import Jump, MovementTokens, Parser, PusherSelection, Steps

if TYPE_CHECKING:
    from ..game import PusherStep


class Snapshot:
    """
    Base class for game snapshots and accompanying metadata.

    Game snapshot is a sequence of pusher steps representing actual steps, jumps (in
    reverse solving mode) and pusher selections (in Multiban variant).
    """

    # Characters used in textual representation of game snapshot. Not all game variants
    # use all characters. Also, for different game variants, same character may have
    # different meaning (represent different direction of movement).

    l: Final[str] = Characters.l
    u: Final[str] = Characters.u
    r: Final[str] = Characters.r
    d: Final[str] = Characters.d
    L: Final[str] = Characters.L
    U: Final[str] = Characters.U
    R: Final[str] = Characters.R
    D: Final[str] = Characters.D
    w: Final[str] = Characters.w
    W: Final[str] = Characters.W
    e: Final[str] = Characters.e
    E: Final[str] = Characters.E
    n: Final[str] = Characters.n
    N: Final[str] = Characters.N
    s: Final[str] = Characters.s
    S: Final[str] = Characters.S

    JUMP_BEGIN: Final[str] = Characters.JUMP_BEGIN
    JUMP_END: Final[str] = Characters.JUMP_END
    PUSHER_CHANGE_BEGIN: Final[str] = Characters.PUSHER_CHANGE_BEGIN
    PUSHER_CHANGE_END: Final[str] = Characters.PUSHER_CHANGE_END
    CURRENT_POSITION_CH: Final[str] = Characters.CURRENT_POSITION_CH

    def __init__(self, tessellation: Tessellation, moves_data: str = ""):
        self.title: str = ""
        self.solver: str = ""
        self.notes: str = ""

        self._tessellation = tessellation
        self._tessellation_obj_val: Optional[TessellationImpl] = None

        if not is_blank(moves_data) and not Characters.is_snapshot(moves_data):
            raise ValueError("Invalid characters in snapshot string!")
        self._moves_data: str = moves_data or ""

        self._parsed_moves: MovementTokens = []
        self._was_parsed = False
        self._pushes_count: int = 0
        self._moves_count: int = 0
        self._jumps_count: int = 0
        self._is_reverse: bool = False

    def to_str(self, rle_encode=False) -> str:
        """Formatted output of parsed and validated moves data."""
        self._reparse_if_not_parsed()

        retv = "".join(str(_) for _ in self._parsed_moves)

        # Reverse snapshots must start with jump, even if it is empty one
        if self.is_reverse and (
            not self._parsed_moves
            or (self._parsed_moves and retv[0] != Characters.JUMP_BEGIN)
        ):
            retv = Characters.JUMP_BEGIN + Characters.JUMP_END + retv

        if rle_encode:
            retv = Rle.encode(retv)

        return retv

    def __str__(self):
        return self.to_str(rle_encode=False)

    def __repr__(self):
        klass = self.__class__.__name__
        return (
            f"{klass}({self._tessellation}, "
            f'moves_data="{self.to_str(rle_encode=False)}")'
        )

    @property
    def tessellation(self) -> Tessellation:
        return self._tessellation

    @property
    def _tessellation_obj(self):
        if self._tessellation_obj_val is None:
            self._tessellation_obj_val = TessellationImpl.instance(self._tessellation)

        return self._tessellation_obj_val

    @property
    def moves_data(self) -> str:
        return self._moves_data

    @moves_data.setter
    def moves_data(self, rv: str):
        if not is_blank(rv) and not Characters.is_snapshot(rv):
            raise ValueError("Invalid characters in snapshot string!")
        self._moves_data = rv or ""
        self._was_parsed = False

    @property
    def pusher_steps(self) -> List[PusherStep]:
        """
        Game engine representation of pusher steps.

        Warning:
            Setting this property will also replace ``moves_data``.
        """
        self._reparse_if_not_parsed()
        return sum(
            (_.pusher_steps(self._tessellation_obj) for _ in self._parsed_moves), []
        )

    @pusher_steps.setter
    def pusher_steps(self, rv: List[PusherStep]):
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
                        jump.data += Characters.CURRENT_POSITION_CH
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
                        pusher_selection.data += Characters.CURRENT_POSITION_CH
                    i += 1
                self._parsed_moves.append(pusher_selection)

            else:
                steps = Steps("")
                while i < iend and not rv[i].is_jump and not rv[i].is_pusher_selection:
                    steps.data += self._tessellation_obj.pusher_step_to_char(rv[i])
                    if rv[i].is_current_pos:
                        steps.data += Characters.CURRENT_POSITION_CH
                    i += 1
                self._parsed_moves.append(steps)
                self._pushes_count += steps.pushes_count
                self._moves_count += steps.moves_count

        self._moves_data = self.to_str(rle_encode=False)

    @property
    def pushes_count(self) -> int:
        """Count of box pushing steps."""
        self._reparse_if_not_parsed()
        return self._pushes_count

    @property
    def moves_count(self) -> int:
        """
        Count of steps that are not pushing a box and are not selecting pusher.
        """
        self._reparse_if_not_parsed()
        return self._moves_count

    @property
    def jumps_count(self) -> int:
        """
        Count of groups of steps that are jumps. Jumps are possible when board is
        being solved in reverse mode.
        """
        self._reparse_if_not_parsed()
        return self._jumps_count

    @property
    def is_reverse(self) -> bool:
        """True if snapshot contains any jumps."""
        self._reparse_if_not_parsed()
        return self._is_reverse

    def _reparse_if_not_parsed(self):
        if not self._was_parsed:
            self._reparse()

    def _reparse(self):
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
