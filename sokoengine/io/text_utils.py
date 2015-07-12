"""
Helper utilities for string manipulation and Sokoban data parsing. Mostly
related to SOK file format, but probably useful for parsing any Sokoban file
format.
"""

import re
from enum import Enum
from itertools import groupby
from functools import reduce
from pyparsing import Regex, nestedExpr, ZeroOrMore, ParseBaseException


class BoardConversionError(RuntimeError):
    CONVERSION_OK         = 1
    RLE_ERROR             = 2
    NON_BOARD_CHARS_FOUND = 4
    INVALID_LAYOUT        = 8


class BoardEncodingCharacters(Enum):
    """
    Characters used in textual representation of boards.
    """
    WALL                = '#'
    PUSHER              = '@'
    PUSHER_ON_GOAL      = '+'
    BOX                 = '$'
    BOX_ON_GOAL         = '*'
    GOAL                = '.'
    FLOOR               = ' '
    VISIBLE_FLOOR       = '-'
    ALT_PUSHER1         = 'p'
    ALT_PUSHER2         = 'm'
    ALT_PUSHER_ON_GOAL1 = 'P'
    ALT_PUSHER_ON_GOAL2 = 'M'
    ALT_BOX1            = 'b'
    ALT_BOX_ON_GOAL1    = 'B'
    ALT_GOAL1           = 'o'
    ALT_VISIBLE_FLOOR1  = '_'


class SpecialSnapshotCharacters(Enum):
    """
    Some characters that can be found in textual representation of snapshots but
    do not represent atomic moves.
    """
    JUMP_BEGIN            = '['
    JUMP_END              = ']'
    PUSHER_CHANGE_BEGIN   = '{'
    PUSHER_CHANGE_END     = '}'
    CURENT_POSITION_CH    = '*'


class AtomicMoveCharacters(Enum):
    """
    Characters used in textual representation of snapshots. Not all variants use
    all characters. Also, fordifferent variants, same character may have
    different meaning.
    """
    LOWER_L  = 'l'
    LOWER_U  = 'u'
    LOWER_R  = 'r'
    LOWER_D  = 'd'
    UPPER_L  = 'L'
    UPPER_U  = 'U'
    UPPER_R  = 'R'
    UPPER_D  = 'D'
    LOWER_NW = 'w'
    UPPER_NW = 'W'
    LOWER_SE = 'e'
    UPPER_SE = 'E'
    LOWER_NE = 'n'
    UPPER_NE = 'N'
    LOWER_SW = 's'
    UPPER_SW = 'S'


class RleCharacters(Enum):
    """
    Separators used in RLE encoded board and snapshot texts
    """
    GROUP_LEFT_DELIM  = '('
    GROUP_RIGHT_DELIM = ')'
    RLE_ROW_SEPARATOR = '|'


def is_pusher(chr):
    if isinstance(chr, BoardEncodingCharacters):
        chr = chr.value
    return (
        chr == BoardEncodingCharacters.PUSHER.value or
        chr == BoardEncodingCharacters.ALT_PUSHER1.value or
        chr == BoardEncodingCharacters.ALT_PUSHER2.value or
        chr == BoardEncodingCharacters.PUSHER_ON_GOAL.value or
        chr == BoardEncodingCharacters.ALT_PUSHER_ON_GOAL1.value or
        chr == BoardEncodingCharacters.ALT_PUSHER_ON_GOAL2.value
    )

def is_box(chr):
    if isinstance(chr, BoardEncodingCharacters):
        chr = chr.value
    return (
        chr == BoardEncodingCharacters.BOX.value or
        chr == BoardEncodingCharacters.ALT_BOX1.value or
        chr == BoardEncodingCharacters.BOX_ON_GOAL.value or
        chr == BoardEncodingCharacters.ALT_BOX_ON_GOAL1.value
    )

def is_goal(chr):
    if isinstance(chr, BoardEncodingCharacters):
        chr = chr.value
    return (
        chr == BoardEncodingCharacters.GOAL.value or
        chr == BoardEncodingCharacters.ALT_GOAL1.value or
        chr == BoardEncodingCharacters.BOX_ON_GOAL.value or
        chr == BoardEncodingCharacters.ALT_BOX_ON_GOAL1.value or
        chr == BoardEncodingCharacters.PUSHER_ON_GOAL.value or
        chr == BoardEncodingCharacters.ALT_PUSHER_ON_GOAL1.value or
        chr == BoardEncodingCharacters.ALT_PUSHER_ON_GOAL2.value
    )

def is_empty_floor(chr):
    if isinstance(chr, BoardEncodingCharacters):
        chr = chr.value
    return (
        chr == BoardEncodingCharacters.FLOOR.value or
        chr == BoardEncodingCharacters.VISIBLE_FLOOR.value or
        chr == BoardEncodingCharacters.ALT_VISIBLE_FLOOR1.value
    )

def is_wall(chr):
    if isinstance(chr, BoardEncodingCharacters):
        chr = chr.value
    return chr == BoardEncodingCharacters.WALL.value

def is_atomic_move_char(chr):
    if isinstance(chr, AtomicMoveCharacters):
        chr = chr.value
    return (
        chr == AtomicMoveCharacters.LOWER_L.value or
        chr == AtomicMoveCharacters.LOWER_U.value or
        chr == AtomicMoveCharacters.LOWER_R.value or
        chr == AtomicMoveCharacters.LOWER_D.value or
        chr == AtomicMoveCharacters.LOWER_NW.value or
        chr == AtomicMoveCharacters.LOWER_SE.value or
        chr == AtomicMoveCharacters.LOWER_NE.value or
        chr == AtomicMoveCharacters.LOWER_SW.value or
        chr == AtomicMoveCharacters.UPPER_L.value or
        chr == AtomicMoveCharacters.UPPER_U.value or
        chr == AtomicMoveCharacters.UPPER_R.value or
        chr == AtomicMoveCharacters.UPPER_D.value or
        chr == AtomicMoveCharacters.UPPER_NW.value or
        chr == AtomicMoveCharacters.UPPER_SE.value or
        chr == AtomicMoveCharacters.UPPER_NE.value or
        chr == AtomicMoveCharacters.UPPER_SW.value
    )

re_only_digits_and_spaces = re.compile(r"^([0-9\s])*$")
def contains_only_digits_and_spaces(line):
    return reduce(lambda x, y: x and y, [
        True if re_only_digits_and_spaces.match(l) else False
        for l in line.splitlines()
    ], True)

def is_blank(line):
    return line.strip() == ""

re_board_string = re.compile(
    "^([0-9\s" +
    re.escape("".join([c.value for c in BoardEncodingCharacters])) +
    re.escape("".join([c.value for c in RleCharacters])) +
    "])*$"
)
def is_board_string(line):
    """
    Checks if line contains only characters legal in textual representation of
    boards.

    @note Doesn't check if it actually contains legal board, it only checks that
    there are no illegal characters. To find out if line is actual board
    representation, it must be converted to actual GameBoard.
    """
    return (
        not contains_only_digits_and_spaces(line) and
        reduce(lambda x, y: x and y, [
            True if re_board_string.match(l) else False
            for l in line.splitlines()
        ], True)
    )

def is_sokoban_plus_string(line):
    return contains_only_digits_and_spaces(line) and not is_blank(line)

re_snapshot_string = re.compile(
    "^([0-9\s" +
    re.escape("".join([c.value for c in AtomicMoveCharacters])) +
    re.escape("".join([c.value for c in SpecialSnapshotCharacters])) +
    re.escape("".join([c.value for c in RleCharacters])) +
    "])*$"
)
def is_snapshot_string(line):
    """
    Checks if @a tline is snapshot string: contains only digits,
    spaces, atomic move characters and rle separators.

    @note Doesn't check if snapshot string is properly formed (for example,
    if all jump sequences are closed, etc.). This is by design, so this
    method may be used to check strings read from stream line by line,
    where each line alone doesn't represent legally formed snapshot, but
    all of them together do. To completely validate this string, it needs
    to be converted to GameSnapshot.
    """
    return (
        not is_blank(line) and
        not contains_only_digits_and_spaces(line) and
        reduce(lambda x, y: x and y, [
            True if re_snapshot_string.match(l) else False
            for l in line.splitlines()
        ], True)
    )

re_ending_digits = re.compile(r"(\d+)$")
def ending_digits(line):
    retv = re_ending_digits.findall(line)
    if retv:
        return re_ending_digits.sub("", line), retv[-1]
    return line, None


re_contains_any_digit = re.compile(r"([0-9])+")
re_rle_replacer = re.compile(r"(\d+)(\D)")
class Rle(object):
    @classmethod
    def encode(cls, line):
        if len(line) == 0:
            line

        encoded = [(len(list(g)), k) for k, g in groupby(line)]
        return "".join([
            "".join([
                str(c) if c > 1 else "",
                v
            ])
            for c, v in encoded
        ])

    @classmethod
    def decode_rle_token(cls, rle_token):
        """
        Decodes rle encoded strings without grouping support. ie.
        decode('3a4b') == "aaabbb"
        decode('3a4b44') == "aaabbb44"
        """
        return re_rle_replacer.sub(lambda m: m.group(2) * int(m.group(1)), rle_token)

    rle_token = Regex(
        "([^" +
        re.escape(RleCharacters.GROUP_LEFT_DELIM.value) +
        re.escape(RleCharacters.GROUP_RIGHT_DELIM.value) +
        "])+"
    )
    grouped_rle = nestedExpr(
        RleCharacters.GROUP_LEFT_DELIM.value,
        RleCharacters.GROUP_RIGHT_DELIM.value
    )
    token_then_group = rle_token + grouped_rle
    group_then_token = grouped_rle + rle_token
    token_or_group = rle_token | grouped_rle
    grammar = ZeroOrMore(token_or_group) +\
        ZeroOrMore(token_then_group) +\
        ZeroOrMore(group_then_token) +\
        ZeroOrMore(token_or_group)

    @classmethod
    def tokenize_grouped_rle(cls, line):
        retv = []
        try:
            retv = cls.grammar.leaveWhitespace().parseString(line).asList()
        except ParseBaseException:
            retv = []
        return retv

    @classmethod
    def proces_group_tokens(cls, tokens):
        retv = ""
        ending_digits_num = 1
        for token in tokens:
            if isinstance(token, list):
                retv = retv + ending_digits_num * cls.decode_rle_token(
                    cls.proces_group_tokens(token)
                )
                ending_digits_num = 1
            else:
                token_contents, ending_digits_str = ending_digits(token)
                retv = retv + cls.decode_rle_token(
                    token_contents
                )
                ending_digits_num = (
                    int(ending_digits_str)
                    if ending_digits_str else 1
                )
        return retv

    @classmethod
    def decode(cls, line):
        return cls.proces_group_tokens(cls.tokenize_grouped_rle(line))


def rle_encode(line):
    return Rle.encode(line)

def rle_decode(line):
    return Rle.decode(line)

def drop_blank(string_list):
    return [l for l in string_list if len(l.strip()) > 0]

def drop_empty(string_list):
    return [l for l in string_list if len(l) > 0]

def normalize_width(string_list):
    width = 0
    for l in string_list:
        if len(l) > width:
            width = len(l)
    return [
        l + (" " * (width - len(l))) for l in string_list
    ]

rle_splitter = re.compile(
    '|'.join(map(re.escape, [RleCharacters.RLE_ROW_SEPARATOR.value, '\n']))
)
def parse_board_string(line):
    """
    Tries to parse string as Sokoban board as defined in SOK
    format specification
    """
    if is_blank(line):
        return []
    if not is_board_string(line):
        raise BoardConversionError(BoardConversionError.NON_BOARD_CHARS_FOUND)

    line = rle_decode(line)
    return normalize_width(drop_empty(rle_splitter.split(line)))