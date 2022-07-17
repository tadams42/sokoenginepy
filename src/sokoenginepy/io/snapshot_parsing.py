from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Union

import lark

from ..common import Characters, TessellationImpl, is_blank
from .rle import Rle

if TYPE_CHECKING:
    from ..game import PusherStep


@dataclass
class Steps:
    data: str

    @property
    def pushes_count(self):
        return sum(1 for _ in self.data if _ in Characters.PUSH_CHARACTERS)

    @property
    def moves_count(self):
        return sum(1 for _ in self.data if _ in Characters.MOVE_CHARACTERS)

    def __str__(self):
        return self.data

    @classmethod
    def converted(cls, data: str, tessellation: TessellationImpl) -> List[PusherStep]:
        retv: List[PusherStep] = []
        for _ in data:
            if _ == Characters.CURRENT_POSITION_CH:
                if retv:
                    retv[-1].is_current_pos = True
            else:
                step = tessellation.char_to_pusher_step(_)
                retv.append(step)

        return retv

    def pusher_steps(self, tessellation: TessellationImpl) -> List[PusherStep]:
        return self.converted(self.data, tessellation)


@dataclass
class Jump:
    data: str
    pushes_count: int = field(init=False, repr=False, default=0)

    @property
    def moves_count(self):
        return sum(1 for _ in self.data if _ in Characters.MOVE_CHARACTERS)

    def __str__(self):
        return Characters.JUMP_BEGIN + self.data + Characters.JUMP_END

    def pusher_steps(self, tessellation: TessellationImpl) -> List[PusherStep]:
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
        return Characters.PUSHER_CHANGE_BEGIN + self.data + Characters.PUSHER_CHANGE_END

    def pusher_steps(self, tessellation: TessellationImpl) -> List[PusherStep]:
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

        jump_begin: "{Characters.JUMP_BEGIN}"
        jump_end: "{Characters.JUMP_END}"
        pusher_change_begin: "{Characters.PUSHER_CHANGE_BEGIN}"
        pusher_change_end: "{Characters.PUSHER_CHANGE_END}"

        moves: /[{''.join(Characters.MOVE_CHARACTERS)}\\{Characters.CURRENT_POSITION_CH}]+/
        pushes: /[{''.join(Characters.PUSH_CHARACTERS)}]+/

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
