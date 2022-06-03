from __future__ import annotations

from typing import Final, Set

import lark

from ..io import Snapshot as TextSnapshot
from ..io import is_blank
from .snapshot import Snapshot
from .solving_mode import SolvingMode
from .tessellation import AnyTessellation, Tessellation


class SnapshotStringParser:
    @classmethod
    def parse(
        cls, data: str, tessellation: AnyTessellation = Tessellation.SOKOBAN
    ) -> Snapshot:
        if is_blank(data):
            return Snapshot(
                tessellation_or_description=tessellation,
                solving_mode=SolvingMode.FORWARD,
            )

        transformer = LarkTreeTransformer(tessellation)
        data = "".join(data)

        try:
            snapshot = transformer.transform(cls._PARSER.parse(data))

        except lark.exceptions.VisitError as e:
            # raise ValueError(str(e))
            raise e.orig_exc from e

        except lark.exceptions.UnexpectedInput as e:
            raise ValueError("Unexpected input in Snapshot string! " + str(e)) from e

        return snapshot

    @classmethod
    def convert_to_string(cls, snapshot: Snapshot) -> str:
        retv = ""
        conversion_ok = True

        # Handling beginning jump in reverse snapshots.
        # It is required that in textual form reverse snapshots begin with
        # jump even if empty one.
        if snapshot.solving_mode == SolvingMode.REVERSE:
            # If is reverse, snapshot can be either
            #  (1) Empty
            #  (2) Non-empty, beginning with jump
            #  (3) Non-empty, not beginning with jump
            # Number (2) is handled gracefully later
            if len(snapshot) == 0:
                retv += TextSnapshot.JUMP_BEGIN
                retv += TextSnapshot.JUMP_END
            elif not snapshot[0].is_jump:
                retv += TextSnapshot.JUMP_BEGIN
                retv += TextSnapshot.JUMP_END

        i = 0
        iend = len(snapshot)
        while i < iend and conversion_ok:
            jump_flag = snapshot[i].is_jump
            pusher_selected_flag = snapshot[i].is_pusher_selection

            if jump_flag or pusher_selected_flag:
                backup_flag = jump_flag
                retv += (
                    TextSnapshot.JUMP_BEGIN
                    if jump_flag
                    else TextSnapshot.PUSHER_CHANGE_BEGIN
                )

                while (
                    i < iend and conversion_ok and (jump_flag or pusher_selected_flag)
                ):
                    try:
                        retv += snapshot.tessellation.atomic_move_to_char(snapshot[i])
                    except ValueError:
                        conversion_ok = False
                    i += 1
                    if i < iend:
                        jump_flag = snapshot[i].is_jump
                        pusher_selected_flag = snapshot[i].is_pusher_selection

                retv += (
                    TextSnapshot.JUMP_END
                    if backup_flag
                    else TextSnapshot.PUSHER_CHANGE_END
                )
            else:
                try:
                    retv += snapshot.tessellation.atomic_move_to_char(snapshot[i])
                except ValueError:
                    conversion_ok = False
                i += 1

        if not conversion_ok:
            raise ValueError(
                "Snapshot string contains directions not supported by requested "
                "tessellation"
            )
        return retv

    _MOVEMENT_CHARACTERS: Final[Set[str]] = {
        TextSnapshot.l,
        TextSnapshot.u,
        TextSnapshot.r,
        TextSnapshot.d,
        TextSnapshot.L,
        TextSnapshot.U,
        TextSnapshot.R,
        TextSnapshot.D,
        TextSnapshot.W,
        TextSnapshot.W,
        TextSnapshot.e,
        TextSnapshot.E,
        TextSnapshot.n,
        TextSnapshot.N,
        TextSnapshot.s,
        TextSnapshot.S,
    }

    _GRAMMAR = f"""
        snapshot: (pusher_change | jump | moves)* (current_pos (pusher_change | jump | moves)*)*

        jump: _JUMP_BEGIN moves _JUMP_END
            | _JUMP_BEGIN _JUMP_END
        pusher_change: _PUSHER_CHANGE_BEGIN moves _PUSHER_CHANGE_END
            | _PUSHER_CHANGE_BEGIN _PUSHER_CHANGE_END
        moves: MOVE+
        current_pos: CURRENT_POS

        _JUMP_BEGIN: "{TextSnapshot.JUMP_BEGIN}"
        _JUMP_END: "{TextSnapshot.JUMP_END}"

        _PUSHER_CHANGE_BEGIN: "{TextSnapshot.PUSHER_CHANGE_BEGIN}"
        _PUSHER_CHANGE_END: "{TextSnapshot.PUSHER_CHANGE_END}"

        CURRENT_POS: "{TextSnapshot.CURRENT_POSITION_CH}"

        MOVE: /[{''.join(c for c in _MOVEMENT_CHARACTERS)}]/

        %import common.WS
        %ignore WS
    """

    _PARSER = lark.Lark(_GRAMMAR, parser="lalr", start="snapshot")


class LarkTreeTransformer(lark.Transformer):
    def __init__(self, tessellation: AnyTessellation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_pos: int = -1
        self.solving_mode = SolvingMode.FORWARD
        self.tessellation = tessellation

    def moves(self, children):
        return [(_.column, self.tessellation.char_to_atomic_move(_)) for _ in children]

    def pusher_change(self, children):
        if not children or not children[0]:
            return []

        retv = children[0]
        for column, am in retv:
            if am.is_push_or_pull:
                raise ValueError(
                    "Failed parsing Snapshot! Pusher selections can't contain pushes "
                    f"(col: {column})!"
                )
            am.is_pusher_selection = True
        return retv

    def jump(self, children):
        self.solving_mode = SolvingMode.REVERSE

        if not children or not children[0]:
            return []

        retv = children[0]
        for column, am in retv:
            if am.is_push_or_pull:
                raise ValueError(
                    "Failed parsing Snaphot! Jumps can't contain pushes "
                    f"(col: {column})!"
                )
            am.is_jump = True
        return retv

    def current_pos(self, children):
        self._current_pos = children[0].start_pos
        return []

    def snapshot(self, children):
        snapshot = Snapshot(
            tessellation_or_description=self.tessellation,
            solving_mode=self.solving_mode,
        )

        if not children:
            return snapshot

        for child in children:
            for _, atomic_move in child:
                snapshot.append(atomic_move)

        return snapshot
