import re
from functools import reduce

from pyparsing import Group, ParseBaseException, Regex, ZeroOrMore, oneOf

from .. import settings, utilities
from .atomic_move import AtomicMove
from .snapshot import Snapshot, SnapshotConversionError

_RE_SNAPSHOT_STRING = re.compile(
    r"^([0-9\s" + re.escape("".join(c for c in AtomicMove.Characters)) +
    re.escape("".join(c for c in Snapshot.NonMoveCharacters)
             ) + re.escape("".join(c for c in utilities.RleCharacters)) + "])*$"
)


class SnapshotStringParser:
    """
    Parses and validates game snapshot string into sequence of
    :class:`AtomicMove`
    """

    atomic_moves = Regex(
        "([" + "".join(c for c in AtomicMove.Characters) + "])+"
    )
    jump = Group(
        oneOf(Snapshot.NonMoveCharacters.JUMP_BEGIN) + ZeroOrMore(atomic_moves)
        + oneOf(Snapshot.NonMoveCharacters.JUMP_END)
    )
    pusher_change = Group(
        oneOf(Snapshot.NonMoveCharacters.PUSHER_CHANGE_BEGIN) + ZeroOrMore(
            atomic_moves
        ) + oneOf(Snapshot.NonMoveCharacters.PUSHER_CHANGE_END)
    )
    grammar = ZeroOrMore(atomic_moves | pusher_change | jump)

    _re_snapshot_string_cleanup = re.compile(
        "([" + re.escape(Snapshot.NonMoveCharacters.CURRENT_POSITION_CH) +
        r"\s])+"
    )

    def __init__(self):
        self._first_encountered_error = None
        self._resulting_solving_mode = None
        self._resulting_moves = None

    @classmethod
    def is_snapshot_string(cls, line):
        return (
            not utilities.is_blank(line) and
            not utilities.contains_only_digits_and_spaces(line) and reduce(
                lambda x, y: x and y, [
                    True if _RE_SNAPSHOT_STRING.match(l) else False
                    for l in line.splitlines()
                ], True
            )
        )

    def convert_from_string(self, from_string, to_snapshot):
        #pylint: disable=protected-access
        if not self._parse(from_string, to_snapshot.tessellation):
            raise SnapshotConversionError(self._first_encountered_error)
        to_snapshot.clear()
        to_snapshot._solving_mode = self._resulting_solving_mode
        for atomic_move in self._resulting_moves:
            to_snapshot.append(atomic_move)

    @classmethod
    def convert_to_string(cls, snapshot):
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
                retv += snapshot.NonMoveCharacters.JUMP_BEGIN
                retv += snapshot.NonMoveCharacters.JUMP_END
            elif not snapshot[0].is_jump:
                retv += snapshot.NonMoveCharacters.JUMP_BEGIN
                retv += snapshot.NonMoveCharacters.JUMP_END

        i = 0
        iend = len(snapshot)
        while i < iend and conversion_ok:
            jump_flag = snapshot[i].is_jump
            pusher_selected_flag = snapshot[i].is_pusher_selection

            if jump_flag or pusher_selected_flag:
                backup_flag = jump_flag
                retv += (
                    snapshot.NonMoveCharacters.JUMP_BEGIN if jump_flag else
                    snapshot.NonMoveCharacters.PUSHER_CHANGE_BEGIN
                )

                while (
                    i < iend and conversion_ok and
                    (jump_flag or pusher_selected_flag)
                ):
                    try:
                        retv += snapshot.tessellation.atomic_move_to_char(
                            snapshot[i]
                        )
                    except utilities.SokoengineError:
                        conversion_ok = False
                    i += 1
                    if i < iend:
                        jump_flag = snapshot[i].is_jump
                        pusher_selected_flag = snapshot[i].is_pusher_selection

                retv += (
                    snapshot.NonMoveCharacters.JUMP_END if backup_flag else
                    snapshot.NonMoveCharacters.PUSHER_CHANGE_END
                )
            else:
                try:
                    retv += snapshot.tessellation.atomic_move_to_char(
                        snapshot[i]
                    )
                except utilities.SokoengineError:
                    conversion_ok = False
                i += 1

        if conversion_ok and settings.RLE_ENCODE_BOARD_STRINGS:
            retv = utilities.rle_encode(retv)

        if conversion_ok and settings.BREAK_LONG_SNAPSHOT_STRINGS:
            tmp = ""
            for i, character in enumerate(retv):
                tmp += character
                if settings.should_insert_line_break_at(i + 1):
                    tmp += "\n"
            retv = tmp

        if not conversion_ok:
            raise SnapshotConversionError(
                "Snapshot string contains directions not supported by requested"
                "tessellation"
            )
        return retv

    def _tokenize_moves_data(self, line):
        retv = []
        try:
            retv = self.grammar.parseString(line).asList()
        except ParseBaseException:
            retv = []
        return retv

    def _parse(self, moves_string, tessellation):
        """
        - Parses moves_string into sequence of AtomicMove using provided
          tessellation
        - Sets parser state detailing the first error encountered in parsing
        - returns boolean value signaling parsing success or failure
        """
        from .. import game

        self._first_encountered_error = None
        self._resulting_solving_mode = None
        self._resulting_moves = None

        moves_string = self._re_snapshot_string_cleanup.sub("", moves_string)
        if utilities.is_blank(moves_string):
            self._resulting_solving_mode = game.SolvingMode.FORWARD
            self._resulting_moves = []
            return True

        if not self.is_snapshot_string(moves_string):
            self._first_encountered_error = (
                "Illegal characters found in snapshot string"
            )
            return False


        if (
            Snapshot.NonMoveCharacters.JUMP_BEGIN in moves_string or
            Snapshot.NonMoveCharacters.JUMP_END in moves_string
        ):

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
                "Tokenizing snapshot string elements failed. Maybe there " +
                "are unmatched parentheses"
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
                    is_jump=(token[0] == Snapshot.NonMoveCharacters.JUMP_BEGIN),
                    is_pusher_change=(
                        token[0] ==
                        Snapshot.NonMoveCharacters.PUSHER_CHANGE_BEGIN
                    ),
                )
            else:
                convert_success = self._convert_token(
                    token=token, tessellation=tessellation
                )
            if not convert_success:
                return False

        return True

    def _convert_token(
        self, token, tessellation, is_jump=False, is_pusher_change=False
    ):

        for character in token:
            atomic_move = None
            try:
                atomic_move = tessellation.char_to_atomic_move(character)
            except utilities.SokoengineError:
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
