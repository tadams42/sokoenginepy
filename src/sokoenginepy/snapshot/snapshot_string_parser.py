import re

from pyparsing import Group, ParseBaseException, Regex, ZeroOrMore, oneOf

from .. import utilities
from ..tessellation import Tessellation
from .atomic_move import AtomicMove
from .snapshot import Snapshot


class SnapshotStringParser:
    """
    Parses and validates game snapshot string into sequence of :class:`AtomicMove`.
    """

    _ATOMIC_MOVES = Regex("([" + "".join(c for c in AtomicMove.CHARACTERS) + "])+")
    _JUMP = Group(
        oneOf(Snapshot.JUMP_BEGIN)
        + ZeroOrMore(_ATOMIC_MOVES)
        + oneOf(Snapshot.JUMP_END)
    )
    _PUSHER_CHANGE = Group(
        oneOf(Snapshot.PUSHER_CHANGE_BEGIN)
        + ZeroOrMore(_ATOMIC_MOVES)
        + oneOf(Snapshot.PUSHER_CHANGE_END)
    )
    _GRAMMAR = ZeroOrMore(_ATOMIC_MOVES | _PUSHER_CHANGE | _JUMP)

    _RE_SNAPSHOT_STRING = re.compile(
        r"^([0-9\s"
        + re.escape("".join(AtomicMove.CHARACTERS))
        + re.escape("".join(Snapshot.NON_MOVE_CHARACTERS))
        + re.escape("".join(utilities.rle.DELIMITERS))
        + "])*$"
    )

    _RE_SNAPSHOT_STRING_CLEANUP = re.compile(
        "([" + re.escape(Snapshot.CURRENT_POSITION_CH) + r"\s])+"
    )

    def __init__(self):
        self._first_encountered_error = None
        self._resulting_solving_mode = None
        self._resulting_moves = None

    @classmethod
    def is_snapshot_string(cls, line: str) -> bool:
        return (
            not utilities.is_blank(line)
            and not utilities.contains_only_digits_and_spaces(line)
            and all(
                True if cls._RE_SNAPSHOT_STRING.match(l) else False
                for l in line.splitlines()
            )
        )

    def convert_from_string(self, from_string: str, to_snapshot: Snapshot):
        if not self._parse(from_string, to_snapshot.tessellation):
            raise ValueError(self._first_encountered_error)
        to_snapshot.clear()
        to_snapshot._solving_mode = self._resulting_solving_mode
        for atomic_move in self._resulting_moves:
            to_snapshot.append(atomic_move)

    @classmethod
    def convert_to_string(
        cls, snapshot: Snapshot, rle_encode: bool, break_long_lines_at: int = 80
    ) -> str:
        from .. import game

        retv = ""
        conversion_ok = True

        # Handling beginning jump in reverse snapshots.
        # It is required that in textual form reverse snapshots begin with
        # jump even if empty one.
        if snapshot.solving_mode == game.SolvingMode.REVERSE:
            # If is reverse, snapshot can be either
            #  (1) Empty
            #  (2) Non-empty, beginning with jump
            #  (3) Non-empty, not beginning with jump
            # Number (2) is handled gracefully later
            if len(snapshot) == 0:
                retv += snapshot.JUMP_BEGIN
                retv += snapshot.JUMP_END
            elif not snapshot[0].is_jump:
                retv += snapshot.JUMP_BEGIN
                retv += snapshot.JUMP_END

        i = 0
        iend = len(snapshot)
        while i < iend and conversion_ok:
            jump_flag = snapshot[i].is_jump
            pusher_selected_flag = snapshot[i].is_pusher_selection

            if jump_flag or pusher_selected_flag:
                backup_flag = jump_flag
                retv += (
                    snapshot.JUMP_BEGIN if jump_flag else snapshot.PUSHER_CHANGE_BEGIN
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

                retv += snapshot.JUMP_END if backup_flag else snapshot.PUSHER_CHANGE_END
            else:
                try:
                    retv += snapshot.tessellation.atomic_move_to_char(snapshot[i])
                except ValueError:
                    conversion_ok = False
                i += 1

        if conversion_ok and rle_encode:
            retv = utilities.rle_encode(retv)

        if conversion_ok and break_long_lines_at:
            tmp = ""
            for i, character in enumerate(retv):
                tmp += character
                if utilities.should_insert_line_break_at(i + 1, break_long_lines_at):
                    tmp += "\n"
            retv = tmp

        if not conversion_ok:
            raise ValueError(
                "Snapshot string contains directions not supported by requested "
                "tessellation"
            )
        return retv

    def _tokenize_moves_data(self, line: str):
        retv = None
        try:
            retv = self._GRAMMAR.parseString(line).asList()
        except ParseBaseException:
            retv = []
        return retv

    def _parse(self, moves_string: str, tessellation: Tessellation):
        """
        - Parses moves_string into sequence of AtomicMove using provided tessellation
        - Sets parser state detailing the first error encountered in parsing
        - returns boolean value signaling parsing success or failure
        """
        from .. import game

        self._first_encountered_error = None
        self._resulting_solving_mode = None
        self._resulting_moves = None

        moves_string = self._RE_SNAPSHOT_STRING_CLEANUP.sub("", moves_string)
        if utilities.is_blank(moves_string):
            self._resulting_solving_mode = game.SolvingMode.FORWARD
            self._resulting_moves = []
            return True

        if not self.is_snapshot_string(moves_string):
            self._first_encountered_error = (
                "Illegal characters found in snapshot string"
            )
            return False

        if Snapshot.JUMP_BEGIN in moves_string or Snapshot.JUMP_END in moves_string:

            self._resulting_solving_mode = game.SolvingMode.REVERSE
        else:
            self._resulting_solving_mode = game.SolvingMode.FORWARD

        moves_string = utilities.rle_decode(moves_string)
        if utilities.is_blank(moves_string):
            self._first_encountered_error = "Rle decoding board string failed"
            return False

        tokens = self._tokenize_moves_data(moves_string)
        if len(tokens) == 0:
            self._first_encountered_error = (
                "Tokenizing snapshot string elements failed. Maybe there "
                + "are unmatched parentheses"
            )
            return False

        self._resulting_moves = []
        for token in tokens:
            if isinstance(token, list):
                if len(token) < 3:
                    # Skip empty tokens
                    continue
                convert_success = self._convert_token(
                    token=token[1],
                    tessellation=tessellation,
                    is_jump=token[0] == Snapshot.JUMP_BEGIN,
                    is_pusher_change=(token[0] == Snapshot.PUSHER_CHANGE_BEGIN),
                )
            else:
                convert_success = self._convert_token(
                    token=token, tessellation=tessellation
                )
            if not convert_success:
                return False

        return True

    def _convert_token(
        self,
        token: str,
        tessellation: Tessellation,
        is_jump: bool = False,
        is_pusher_change: bool = False,
    ) -> AtomicMove:
        for character in token:
            atomic_move = None
            try:
                atomic_move = tessellation.char_to_atomic_move(character)
            except ValueError:
                atomic_move = None

            if atomic_move is None:
                self._first_encountered_error = (
                    "Snapshot string contains directions not supported by "
                    "requested tessellation"
                )
                return False

            if is_jump:
                if atomic_move.is_push_or_pull:
                    self._first_encountered_error = (
                        "Jump sequence in snapshot string contains atomic "
                        "pushes. This is not allowed"
                    )
                    return False
                else:
                    atomic_move.is_jump = True
            elif is_pusher_change:
                if atomic_move.is_push_or_pull:
                    self._first_encountered_error = (
                        "Pusher change sequence in snapshot string contains "
                        "atomic pushes. This is not allowed"
                    )
                    return False
                else:
                    atomic_move.is_pusher_selection = True

            self._resulting_moves.append(atomic_move)

        return True
