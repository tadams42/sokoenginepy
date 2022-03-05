from collections.abc import Iterable, MutableSequence
from typing import ClassVar, List, Optional, Set, Union

from .. import utilities
from ..tessellation import Tessellation


class Snapshot(MutableSequence):
    """
    Sequence of AtomicMove representing snapshot of game.

    Args:
        tessellation_or_description: game tessellation as string or
            :class:`.Tessellation` instance
        solving_mode: game solving mode
        moves_data: Strings consisting of characters representing
            :class:`.AtomicMove`. If not empty it will be parsed. Also, if not empty,
            solving mode will be parsed from it, and the value of ``solving_mode``
            argument will be ignored
    """

    JUMP_BEGIN: ClassVar[str] = "["
    JUMP_END: ClassVar[str] = "]"
    PUSHER_CHANGE_BEGIN: ClassVar[str] = "{"
    PUSHER_CHANGE_END: ClassVar[str] = "}"
    CURRENT_POSITION_CH: ClassVar[str] = "*"

    #: Some characters that can be found in textual representation of snapshots that do
    #: not represent :class:`.AtomicMove`.
    NON_MOVE_CHARACTERS: ClassVar[Set[str]] = {
        JUMP_BEGIN,
        JUMP_END,
        PUSHER_CHANGE_BEGIN,
        PUSHER_CHANGE_END,
        CURRENT_POSITION_CH,
    }

    def __init__(
        self,
        tessellation_or_description: Union[Tessellation, str],
        solving_mode: Optional["SolvingMode"] = None,
        moves_data: str = "",
    ):
        super().__init__()
        self._tessellation_instance = Tessellation.instance_from(
            tessellation_or_description
        )
        self._solving_mode = None
        self._moves_count = 0
        self._pushes_count = 0
        self._jumps_count = 0
        self._jumps_count_invalidated = False
        self._moves: List["AtomicMove"] = []

        if not utilities.is_blank(moves_data):
            from .snapshot_string_parser import SnapshotStringParser

            SnapshotStringParser().convert_from_string(moves_data, self)
        else:
            self._solving_mode = solving_mode

        if self._solving_mode is None:
            raise ValueError(
                "Snapshot not correctly initialized! Missing solving_mode. Either "
                "provide it explicitly or provide moves_data. "
                f"tessellation_or_description: '{tessellation_or_description}', "
                f"solving_mode: {solving_mode}, "
                f" moves_data: {moves_data}"
            )

    @classmethod
    def is_snapshot_string(cls, line: str) -> bool:
        """
        Checks if ``line`` is snapshot string.

        Snapshot strings contain only digits, spaces, atomic move characters and rle
        separators.

        Note:
            Doesn't check if snapshot string is properly formed (for example, if all
            jump sequences are closed, etc.). This is by design, so this method may
            be used to check strings read from stream line by line, where each line
            alone doesn't represent legally formed snapshot, but all of them together
            do. To completely validate this string, it needs to be converted to
            :class:`.Snapshot`.
        """
        from .snapshot_string_parser import SnapshotStringParser

        return SnapshotStringParser.is_snapshot_string(line)

    @property
    def tessellation(
        self
    ) -> Union[
        "SokobanTessellation",
        "TriobanTessellation",
        "HexobanTessellation",
        "OctobanTessellation",
    ]:
        return self._tessellation_instance.value

    # Iterable
    def __iter__(self):
        return self._moves.__iter__()

    # Sized
    def __len__(self):
        return self._moves.__len__()

    # Container
    def __contains__(self, atomic_move):
        return self._moves.__contains__(atomic_move)

    # Sequence
    def __getitem__(self, index):
        retv = self._moves.__getitem__(index)
        if isinstance(retv, self._moves.__class__):
            snapshot = Snapshot(
                tessellation_or_description=self.tessellation,
                solving_mode=self.solving_mode,
            )
            for atomic_move in retv:
                snapshot.append(atomic_move)
            return snapshot
        else:
            return retv

    # MutableSequence
    def __setitem__(self, index, value):
        if isinstance(index, slice):
            for atomic_move in self._moves[index]:
                self._before_removing_move(atomic_move)
        else:
            self._before_removing_move(self._moves[index])

        if isinstance(value, Iterable):
            for atomic_move in value:
                self._before_inserting_move(atomic_move)
        else:
            self._before_inserting_move(value)

        self._moves.__setitem__(index, value)

    # MutableSequence
    def __delitem__(self, index):
        if isinstance(index, slice):
            for atomic_move in self._moves[index]:
                self._before_removing_move(atomic_move)
        else:
            self._before_removing_move(self._moves[index])
        self._moves.__delitem__(index)

    # MutableSequence
    def insert(self, index, value):
        self._before_inserting_move(value)
        self._moves.insert(index, value)

    def __repr__(self):
        return (
            "Snapshot(tessellation="
            + "{0}, solving_mode={1}, moves_data={2})".format(
                repr(self.tessellation), self.solving_mode, str(self)
            )
        )

    def __eq__(self, rv):
        return (
            self.tessellation == rv.tessellation
            and len(self._moves) == len(rv._moves)
            and self.solving_mode == rv.solving_mode
            and self.moves_count == rv.moves_count
            and self.pushes_count == rv.pushes_count
            and self.jumps_count == rv.jumps_count
            and self._moves == rv._moves
        )

    def __ne__(self, rv):
        return not self == rv

    @property
    def solving_mode(self) -> "SolvingMode":
        return self._solving_mode

    @property
    def moves_count(self) -> int:
        """
        Count of atomic moves in self that are not pushes, not jumps and are not
        pusher selections.
        """
        return self._moves_count

    @property
    def pushes_count(self) -> int:
        return self._pushes_count

    @property
    def jumps_count(self) -> int:
        self._recalculate_jumps_count()
        return self._jumps_count

    def clear(self):
        self._moves_count = 0
        self._pushes_count = 0
        self._jumps_count = 0
        self._jumps_count_invalidated = False
        self._moves = []

    def to_str(self, break_long_lines_at: int = 80, rle_encode: bool = False) -> str:
        from .snapshot_string_parser import SnapshotStringParser

        return SnapshotStringParser.convert_to_string(
            self, break_long_lines_at=break_long_lines_at, rle_encode=rle_encode
        )

    def __str__(self):
        return self.to_str()

    def _before_removing_move(self, atomic_move):
        if not atomic_move.is_pusher_selection:
            if atomic_move.is_jump:
                self._jumps_count_invalidated = True
            if atomic_move.is_move:
                self._moves_count -= 1
            elif atomic_move.is_push_or_pull:
                self._pushes_count -= 1

    def _before_inserting_move(self, atomic_move):
        from .. import game

        if self._solving_mode == game.SolvingMode.FORWARD and atomic_move.is_jump:
            raise ValueError("Forward mode snapshots are not allowed to contain jumps!")

        if atomic_move.direction not in self.tessellation.legal_directions:
            raise ValueError(
                "Invalid direction for tessellation '{0}'".format(self.tessellation)
            )

        if not atomic_move.is_pusher_selection:
            if atomic_move.is_jump:
                self._jumps_count_invalidated = True
            if atomic_move.is_move:
                self._moves_count += 1
            elif atomic_move.is_push_or_pull:
                self._pushes_count += 1

    def _recalculate_jumps_count(self):
        if self._jumps_count_invalidated:
            self._jumps_count_invalidated = False
            self._jumps_count = self._count_jumps()

    def _count_jumps(self):
        retv = 0
        i = 0
        iend = len(self._moves)

        while i < iend:
            if self._moves[i].is_jump:
                while i < iend and self._moves[i].is_jump:
                    i += 1
                retv += 1
            else:
                i += 1

        return retv
