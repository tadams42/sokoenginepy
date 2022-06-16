from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final, List, Set, Union

import lark

from .rle import Rle
from .snapshot import Snapshot
from .utilities import is_blank

if TYPE_CHECKING:
    from ..game import BaseTessellation, PusherStep, Tessellation


class Constants:
    l: Final[str] = Snapshot.l
    u: Final[str] = Snapshot.u
    r: Final[str] = Snapshot.r
    d: Final[str] = Snapshot.d
    L: Final[str] = Snapshot.L
    U: Final[str] = Snapshot.U
    R: Final[str] = Snapshot.R
    D: Final[str] = Snapshot.D
    w: Final[str] = Snapshot.w
    W: Final[str] = Snapshot.W
    e: Final[str] = Snapshot.e
    E: Final[str] = Snapshot.E
    n: Final[str] = Snapshot.n
    N: Final[str] = Snapshot.N
    s: Final[str] = Snapshot.s
    S: Final[str] = Snapshot.S

    JUMP_BEGIN: Final[str] = Snapshot.JUMP_BEGIN
    JUMP_END: Final[str] = Snapshot.JUMP_END
    PUSHER_CHANGE_BEGIN: Final[str] = Snapshot.PUSHER_CHANGE_BEGIN
    PUSHER_CHANGE_END: Final[str] = Snapshot.PUSHER_CHANGE_END
    CURRENT_POSITION_CH: Final[str] = Snapshot.CURRENT_POSITION_CH

    MOVE_CHARACTERS: Final[Set[str]] = {l, u, r, d, n, s, e, w}
    PUSH_CHARACTERS: Final[Set[str]] = {L, U, R, D, N, S, E, W}
    MARKERS: Final[Set[str]] = {
        JUMP_BEGIN,
        JUMP_END,
        PUSHER_CHANGE_BEGIN,
        PUSHER_CHANGE_END,
        CURRENT_POSITION_CH,
    }

    RE_SNAPSHOT_STRING = re.compile(
        r"^([0-9\s"
        + re.escape("".join(MOVE_CHARACTERS))
        + re.escape("".join(PUSH_CHARACTERS))
        + re.escape("".join(MARKERS))
        + re.escape("".join({Rle.GROUP_START, Rle.GROUP_END, Rle.EOL}))
        + "])*$"
    )


@dataclass
class Steps:
    data: str

    @property
    def pushes_count(self):
        return sum(1 for _ in self.data if _ in Constants.PUSH_CHARACTERS)

    @property
    def moves_count(self):
        return sum(1 for _ in self.data if _ in Constants.MOVE_CHARACTERS)

    def __str__(self):
        return self.data

    @classmethod
    def converted(cls, data: str, tessellation: BaseTessellation) -> List[PusherStep]:
        retv: List[PusherStep] = []
        for _ in data:
            if _ == Constants.CURRENT_POSITION_CH:
                if retv:
                    retv[-1].is_current_pos = True
            else:
                step = tessellation.char_to_pusher_step(_)
                retv.append(step)

        return retv

    def pusher_steps(self, tessellation: BaseTessellation) -> List[PusherStep]:
        return self.converted(self.data, tessellation)


@dataclass
class Jump:
    data: str
    pushes_count: int = field(init=False, repr=False, default=0)

    @property
    def moves_count(self):
        return sum(1 for _ in self.data if _ in Constants.MOVE_CHARACTERS)

    def __str__(self):
        return Constants.JUMP_BEGIN + self.data + Constants.JUMP_END

    def pusher_steps(self, tessellation: BaseTessellation) -> List[PusherStep]:
        retv = Steps.converted(self.data, tessellation)
        for _ in retv:
            _.is_jump = True
        return retv


@dataclass
class PusherSelection:
    data: str
    pushes_count: int = field(init=False, repr=False, default=0)
    moves_count: int = field(init=False, repr=False, default=0)

    def __str__(self):
        return Constants.PUSHER_CHANGE_BEGIN + self.data + Constants.PUSHER_CHANGE_END

    def pusher_steps(self, tessellation: BaseTessellation) -> List[PusherStep]:
        retv = Steps.converted(self.data, tessellation)
        for _ in retv:
            _.is_pusher_selection = True
        return retv


MovementTokens = List[Union[Jump, PusherSelection, Steps]]


class Parser:
    GRAMMAR = f"""
        snapshot: (jump | pusher_selection | steps)+

        jump: jump_begin moves* jump_end
        pusher_selection: pusher_change_begin moves pusher_change_end
        steps: (moves | pushes)+

        jump_begin: "{Constants.JUMP_BEGIN}"
        jump_end: "{Constants.JUMP_END}"
        pusher_change_begin: "{Constants.PUSHER_CHANGE_BEGIN}"
        pusher_change_end: "{Constants.PUSHER_CHANGE_END}"

        moves: /[{''.join(Constants.MOVE_CHARACTERS)}\\{Constants.CURRENT_POSITION_CH}]+/
        pushes: /[{''.join(Constants.PUSH_CHARACTERS)}]+/

        %import common.WS
        %ignore WS
    """

    # Reference: .venv/lib/python3.9/site-packages/lark/grammars/common.lark
    #
    #     WS: /[ \t\f\r\n]/+

    PARSER = lark.Lark(GRAMMAR, parser="lalr", start="snapshot")

    @classmethod
    def parse(cls, data: str) -> MovementTokens:
        if is_blank(data):
            return []

        data = Rle.decode(data)

        try:
            parsed = LarkTreeTransformer().transform(cls.PARSER.parse(data))

        except lark.exceptions.VisitError as e:
            # raise ValueError(str(e))
            raise e.orig_exc from e

        except lark.exceptions.UnexpectedInput as e:
            raise ValueError("Unexpected input in Snapshot string! " + str(e)) from e

        return parsed


class LarkTreeTransformer(lark.Transformer):
    def snapshot(self, args: MovementTokens):
        return args

    def jump(self, args):
        return Jump("".join(args))

    def pusher_selection(self, args):
        return PusherSelection("".join(args))

    def steps(self, args):
        return Steps("".join(args))

    def pushes(self, args):
        return "".join(args)

    def moves(self, args):
        return "".join(args)

    def jump_begin(self, args):
        return lark.visitors.Discard

    def jump_end(self, args):
        return lark.visitors.Discard

    def pusher_change_begin(self, args):
        return lark.visitors.Discard

    def pusher_change_end(self, args):
        return lark.visitors.Discard
