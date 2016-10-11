import re
from enum import Enum
from functools import reduce

from pyparsing import Group, ParseBaseException, Regex, ZeroOrMore, oneOf

from ..common import (RleCharacters, SokoengineError,
                      contains_only_digits_and_spaces, is_blank, rle_decode)


class SnapshotConversionError(SokoengineError):
    """
    Exception risen when converting game snapshot to or from snapshot strings.
    """
    RLE_DECODING_ERROR = "Rle decoding board string failed"
    NON_SNAPSHOT_CHARACTERS_FOUND = "Illegal characters found in snapshot string"
    TOKENIZATION_ERROR = (
        "Tokenizing snapshot string elements failed. Maybe there are unmatched "
        "parentheses"
    )
    NON_VARIANT_CHARACTERS_FOUND = (
        "Snapshot string contains directions not supported by requested"
        "tessellation"
    )
    PUSHER_CHANGE_CONTAINS_PUSHES = (
        "Pusher change sequence in snapshot string contains atomic "
        "pushes. This is not allowed"
    )
    JUMP_CONTAINS_PUSHES = (
        "Jump sequence in snapshot string contains atomic pushes. "
        "This is not allowed"
    )


class SpecialSnapshotCharacters(Enum):
    """
    Some characters that can be found in textual representation of snapshots but
    do not represent atomic moves.
    """
    JUMP_BEGIN = '['
    JUMP_END = ']'
    PUSHER_CHANGE_BEGIN = '{'
    PUSHER_CHANGE_END = '}'
    CURENT_POSITION_CH = '*'


class AtomicMoveCharacters(Enum):
    """
    Characters used in textual representation of snapshots. Not all variants use
    all characters. Also, fordifferent variants, same character may have
    different meaning.
    """
    LOWER_L = 'l'
    LOWER_U = 'u'
    LOWER_R = 'r'
    LOWER_D = 'd'
    UPPER_L = 'L'
    UPPER_U = 'U'
    UPPER_R = 'R'
    UPPER_D = 'D'
    LOWER_NW = 'w'
    UPPER_NW = 'W'
    LOWER_SE = 'e'
    UPPER_SE = 'E'
    LOWER_NE = 'n'
    UPPER_NE = 'N'
    LOWER_SW = 's'
    UPPER_SW = 'S'


_re_snapshot_string = re.compile(
    r"^([0-9\s" + re.escape("".join(c.value for c in AtomicMoveCharacters)) +
    re.escape("".join(c.value for c in SpecialSnapshotCharacters)
             ) + re.escape("".join(c.value for c in RleCharacters)) + "])*$"
)


def is_atomic_move(character):
    if isinstance(character, AtomicMoveCharacters):
        character = character.value
    return (
        character == AtomicMoveCharacters.LOWER_L.value or
        character == AtomicMoveCharacters.LOWER_U.value or
        character == AtomicMoveCharacters.LOWER_R.value or
        character == AtomicMoveCharacters.LOWER_D.value or
        character == AtomicMoveCharacters.LOWER_NW.value or
        character == AtomicMoveCharacters.LOWER_SE.value or
        character == AtomicMoveCharacters.LOWER_NE.value or
        character == AtomicMoveCharacters.LOWER_SW.value or
        character == AtomicMoveCharacters.UPPER_L.value or
        character == AtomicMoveCharacters.UPPER_U.value or
        character == AtomicMoveCharacters.UPPER_R.value or
        character == AtomicMoveCharacters.UPPER_D.value or
        character == AtomicMoveCharacters.UPPER_NW.value or
        character == AtomicMoveCharacters.UPPER_SE.value or
        character == AtomicMoveCharacters.UPPER_NE.value or
        character == AtomicMoveCharacters.UPPER_SW.value
    )


def is_snapshot_string(line):
    """Checks if ``line`` is snapshot string.

    Snapshot strings contain only digits, spaces, atomic move characters and
    rle separators.

    Note:
        Doesn't check if snapshot string is properly formed (for example, if
        all jump sequences are closed, etc.). This is by design, so this method
        may be used to check strings read from stream line by line, where each
        line alone doesn't represent legally formed snapshot, but all of them
        together do. To completely validate this string, it needs to be
        converted to :class:`~sokoenginepy.game.game_snapshot.GameSnapshot`.
    """
    return (
        not is_blank(line) and not contains_only_digits_and_spaces(line) and
        reduce(
            lambda x, y: x and y, [
                True if _re_snapshot_string.match(l) else False
                for l in line.splitlines()
            ], True
        )
    )


class SnapshotStringParser:
    """Parses and validates game snapshot string into sequence of AtomicMoves"""
    
    atomic_moves = Regex(
        "([" + "".join(c.value for c in AtomicMoveCharacters) + "])+"
    )
    jump = Group(
        oneOf(SpecialSnapshotCharacters.JUMP_BEGIN.value) + ZeroOrMore(
            atomic_moves
        ) + oneOf(SpecialSnapshotCharacters.JUMP_END.value)
    )
    pusher_change = Group(
        oneOf(SpecialSnapshotCharacters.PUSHER_CHANGE_BEGIN.value) + ZeroOrMore(
            atomic_moves
        ) + oneOf(SpecialSnapshotCharacters.PUSHER_CHANGE_END.value)
    )
    grammar = ZeroOrMore(atomic_moves | pusher_change | jump)

    _re_snapshot_string_cleanup = re.compile(
        "([" + re.escape(SpecialSnapshotCharacters.CURENT_POSITION_CH.value) +
        r"\s])+"
    )

    def __init__(self):
        self._first_encountered_error = None
        self._resulting_solving_mode = None
        self._resulting_moves = None

    @property
    def first_encountered_error(self):
        return self._first_encountered_error

    @property
    def resulting_solving_mode(self):
        return self._resulting_solving_mode

    @property
    def resulting_moves(self):
        return self._resulting_moves

    def tokenize_moves_data(self, line):
        retv = []
        try:
            retv = self.grammar.parseString(line).asList()
        except ParseBaseException:
            retv = []
        return retv

    def convert(self, moves_string, tessellation):
        """
        - Parses moves_string into sequence of AtomicMove using provided
          tessellation
        - Sets parser state detailing the first error encountered in parsing
        - returns boolean value signaling parsing success or failure
        """
        self._first_encountered_error = None
        self._resulting_solving_mode = None
        self._resulting_moves = None

        moves_string = self._re_snapshot_string_cleanup.sub("", moves_string)
        if is_blank(moves_string):
            self._resulting_solving_mode = 'forward'
            self._resulting_moves = []
            return True

        if not is_snapshot_string(moves_string):
            self._first_encountered_error = SnapshotConversionError.NON_SNAPSHOT_CHARACTERS_FOUND
            return False

        if (SpecialSnapshotCharacters.JUMP_BEGIN.value in moves_string or
                SpecialSnapshotCharacters.JUMP_END.value in moves_string):
            self._resulting_solving_mode = 'reverse'
        else:
            self._resulting_solving_mode = 'forward'

        moves_string = rle_decode(moves_string)
        if is_blank(moves_string):
            self._first_encountered_error = SnapshotConversionError.RLE_DECODING_ERROR
            return False

        tokens = self.tokenize_moves_data(moves_string)
        if len(tokens) == 0:
            self._first_encountered_error = SnapshotConversionError.TOKENIZATION_ERROR
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
                    is_jump=(
                        token[0] == SpecialSnapshotCharacters.JUMP_BEGIN.value
                    ),
                    is_pusher_change=(
                        token[0] ==
                        SpecialSnapshotCharacters.PUSHER_CHANGE_BEGIN.value
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
            except SokoengineError:
                atomic_move = None

            if atomic_move is None:
                self._first_encountered_error = SnapshotConversionError.NON_VARIANT_CHARACTERS_FOUND
                return False

            if is_jump:
                if atomic_move.is_push_or_pull:
                    self._first_encountered_error = SnapshotConversionError.JUMP_CONTAINS_PUSHES
                    return False
                else:
                    atomic_move.is_jump = True
            elif is_pusher_change:
                if atomic_move.is_push_or_pull:
                    self._first_encountered_error = SnapshotConversionError.PUSHER_CHANGE_CONTAINS_PUSHES
                    return False
                else:
                    atomic_move.is_pusher_selection = True

            self._resulting_moves.append(atomic_move)

        return True
