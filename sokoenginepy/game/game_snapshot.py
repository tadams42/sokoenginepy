from collections.abc import Iterable, MutableSequence

from ..common import (EqualityComparable, PrettyPrintable, SokoengineError,
                      UnknownDirectionError, Variant, is_blank, rle_encode)
from ..input_output import OutputSettings
from ..snapshot import (SnapshotConversionError, SnapshotStringParser,
                        SpecialSnapshotCharacters)
from ..tessellation import Tessellated
from .common import GameSolvingMode


class GameSnapshot(MutableSequence, PrettyPrintable, Tessellated, EqualityComparable):
    """Sequence of AtomicMove representing snapshot of game.

    Args:
        variant (Variant): game variant
        solving_mode (GameSolvingMode): game solving mode
        moves_data (string): Strings consisting of characters representing
            atomic moves. If not empty it will be parsed. Also, if not empty,
            solving mode will be parsed from it, and the value of
            ``solving_mode`` argument will be ignored
    """

    def __init__(
        self, variant=Variant.SOKOBAN, solving_mode=GameSolvingMode.FORWARD,
        moves_data=""
    ):
        super().__init__(variant)
        self._solving_mode = None
        self._moves_count = 0
        self._pushes_count = 0
        self._jumps_count = 0
        self._jumps_count_invalidated = False
        self._moves = []

        if not is_blank(moves_data):
            self._parse_string(moves_data)
        else:
            self._solving_mode = solving_mode

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
            game_snapshot = GameSnapshot(
                variant=self.variant, solving_mode=self.solving_mode
            )
            for atomic_move in retv:
                game_snapshot.append(atomic_move)
            return game_snapshot
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
    def insert(self, index, atomic_move):
        self._before_inserting_move(atomic_move)
        self._moves.insert(index, atomic_move)

    # PrettyPrintable
    @property
    def _representation_attributes(self):
        return {
            'solving_mode': self.solving_mode,
            'tessellation': self.variant,
            'moves_count': self.moves_count,
            'pushes_count': self.pushes_count,
            'jumps_count': self.jumps_count,
        }

    # EqualityComparable
    @property
    def _equality_attributes(self):
        return (
            self.variant, len(self._moves), self.solving_mode, self.moves_count,
            self.pushes_count, self.jumps_count, self._moves
        )

    @property
    def solving_mode(self):
        return self._solving_mode

    @property
    def moves_count(self):
        """Count of atomic moves in self that are not pushes.

        Note:
            This doesn't account moves that are used for pusher selection in
            Multiban games.
        """
        return self._moves_count

    @property
    def pushes_count(self):
        return self._pushes_count

    @property
    def jumps_count(self):
        self._recalc_jumps_count()
        return self._jumps_count

    def clear(self):
        self._moves_count = 0
        self._pushes_count = 0
        self._jumps_count = 0
        self._jumps_count_invalidated = False
        self._moves = []

    def to_s(self, output_settings=OutputSettings()):
        retv = ""
        conversion_ok = True

        # Handling beginning jump in reverse snapshots.
        # It is required that in textual form reverse snapshots begin with
        # jump even if empty one.
        if self.solving_mode == GameSolvingMode.REVERSE:
            # If is reverse, snapshot can be either
            #  (1) Empty
            #  (2) Non-empty, beginning with jump
            #  (3) Non-empty, not beginning with jump
            # Number (2) is handled gracefully later
            if len(self._moves) == 0:
                retv += SpecialSnapshotCharacters.JUMP_BEGIN.value
                retv += SpecialSnapshotCharacters.JUMP_END.value
            elif not self._moves[0].is_jump:
                retv += SpecialSnapshotCharacters.JUMP_BEGIN.value
                retv += SpecialSnapshotCharacters.JUMP_END.value

        i = 0
        iend = len(self._moves)
        while i < iend and conversion_ok:
            jump_flag = self._moves[i].is_jump
            pusher_selected_flag = self._moves[i].is_pusher_selection

            if jump_flag or pusher_selected_flag:
                backup_flag = jump_flag
                retv += (
                    SpecialSnapshotCharacters.JUMP_BEGIN.value if jump_flag else
                    SpecialSnapshotCharacters.PUSHER_CHANGE_BEGIN.value
                )

                while (
                    i < iend and conversion_ok and
                    (jump_flag or pusher_selected_flag)
                ):
                    try:
                        retv += self.tessellation.atomic_move_to_char(
                            self._moves[i]
                        )
                    except SokoengineError:
                        conversion_ok = False
                    i += 1
                    if i < iend:
                        jump_flag = self._moves[i].is_jump
                        pusher_selected_flag = self._moves[i
                                                          ].is_pusher_selection

                retv += (
                    SpecialSnapshotCharacters.JUMP_END.value if backup_flag else
                    SpecialSnapshotCharacters.PUSHER_CHANGE_END.value
                )
            else:
                try:
                    retv += self.tessellation.atomic_move_to_char(
                        self._moves[i]
                    )
                except SokoengineError:
                    conversion_ok = False
                i += 1

        if conversion_ok and output_settings.rle_encode:
            retv = rle_encode(retv)

        if conversion_ok and output_settings.break_long_lines:
            tmp = ""
            for i, character in enumerate(retv):
                tmp += character
                if output_settings.should_insert_line_break_at(i + 1):
                    tmp += "\n"
            retv = tmp

        if not conversion_ok:
            raise SnapshotConversionError(
                SnapshotConversionError.NON_VARIANT_CHARACTERS_FOUND
            )
        return retv

    def _before_removing_move(self, atomic_move):
        if not atomic_move.is_pusher_selection:
            if atomic_move.is_jump:
                self._jumps_count_invalidated = True
            if atomic_move.is_move:
                self._moves_count -= 1
            elif atomic_move.is_push_or_pull:
                self._pushes_count -= 1

    def _before_inserting_move(self, atomic_move):
        if (self._solving_mode == GameSolvingMode.FORWARD and atomic_move.is_jump):
            raise SokoengineError(
                "Forward mode snapshots are not allowed to contain jumps!"
            )

        if atomic_move.direction not in self.tessellation.legal_directions:
            raise UnknownDirectionError(
                "Invalid direction for tessellation {0}".format(self.variant)
            )

        if not atomic_move.is_pusher_selection:
            if atomic_move.is_jump:
                self._jumps_count_invalidated = True
            if atomic_move.is_move:
                self._moves_count += 1
            elif atomic_move.is_push_or_pull:
                self._pushes_count += 1

    def _recalc_jumps_count(self):
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

    def _parse_string(self, moves_data):
        parser = SnapshotStringParser()
        if not parser.convert(moves_data, self.tessellation):
            raise SnapshotConversionError(parser.first_encountered_error)
        self.clear()

        if parser.resulting_solving_mode == 'forward':
            self._solving_mode = GameSolvingMode.FORWARD
        elif parser.resulting_solving_mode == 'reverse':
            self._solving_mode = GameSolvingMode.REVERSE
        else:
            raise SokoengineError('Unknown parsed solving mode!')

        for atomic_move in parser.resulting_moves:
            self.append(atomic_move)
