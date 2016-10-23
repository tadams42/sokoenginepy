import re
from enum import Enum
from functools import reduce

from ..common import (RleCharacters, SokoengineError,
                      contains_only_digits_and_spaces, is_blank,
                      normalize_width, rle_decode)


class BoardCharacters(Enum):
    """Characters used in textual representation of boards."""
    WALL = '#'
    PUSHER = '@'
    PUSHER_ON_GOAL = '+'
    BOX = '$'
    BOX_ON_GOAL = '*'
    GOAL = '.'
    FLOOR = ' '
    VISIBLE_FLOOR = '-'
    ALT_PUSHER1 = 'p'
    ALT_PUSHER2 = 'm'
    ALT_PUSHER_ON_GOAL1 = 'P'
    ALT_PUSHER_ON_GOAL2 = 'M'
    ALT_BOX1 = 'b'
    ALT_BOX_ON_GOAL1 = 'B'
    ALT_GOAL1 = 'o'
    ALT_VISIBLE_FLOOR1 = '_'


class BoardConversionError(SokoengineError):
    """Exception risen when converting board to or from board strings."""
    RLE_DECODING_ERROR = "Rle decoding board string failed"
    NON_BOARD_CHARS_FOUND = "Illegal characters found in board string"
    INVALID_LAYOUT = (
        "Board string has invalid layout for tessellation with multiple "
        "characters per single board cell"
    )


def is_pusher(character):
    if isinstance(character, BoardCharacters):
        character = character.value
    return (
        character == BoardCharacters.PUSHER.value or
        character == BoardCharacters.ALT_PUSHER1.value or
        character == BoardCharacters.ALT_PUSHER2.value or
        character == BoardCharacters.PUSHER_ON_GOAL.value or
        character == BoardCharacters.ALT_PUSHER_ON_GOAL1.value or
        character == BoardCharacters.ALT_PUSHER_ON_GOAL2.value
    )


def is_box(character):
    if isinstance(character, BoardCharacters):
        character = character.value
    return (
        character == BoardCharacters.BOX.value or
        character == BoardCharacters.ALT_BOX1.value or
        character == BoardCharacters.BOX_ON_GOAL.value or
        character == BoardCharacters.ALT_BOX_ON_GOAL1.value
    )


def is_goal(character):
    if isinstance(character, BoardCharacters):
        character = character.value
    return (
        character == BoardCharacters.GOAL.value or
        character == BoardCharacters.ALT_GOAL1.value or
        character == BoardCharacters.BOX_ON_GOAL.value or
        character == BoardCharacters.ALT_BOX_ON_GOAL1.value or
        character == BoardCharacters.PUSHER_ON_GOAL.value or
        character == BoardCharacters.ALT_PUSHER_ON_GOAL1.value or
        character == BoardCharacters.ALT_PUSHER_ON_GOAL2.value
    )


def is_empty_floor(character):
    if isinstance(character, BoardCharacters):
        character = character.value
    return (
        character == BoardCharacters.FLOOR.value or
        character == BoardCharacters.VISIBLE_FLOOR.value or
        character == BoardCharacters.ALT_VISIBLE_FLOOR1.value
    )


def is_wall(character):
    if isinstance(character, BoardCharacters):
        character = character.value
    return character == BoardCharacters.WALL.value


_re_board_string = re.compile(
    r"^([0-9\s" + re.escape("".join(c.value for c in BoardCharacters)) +
    re.escape("".join(c.value for c in RleCharacters)) + "])*$"
)


def is_board_string(line):
    """Checks if line contains only characters legal in textual representation of boards.

    Note:
        Doesn't check if it actually contains legal board, it only checks that
        there are no illegal characters. To find out if line is actual board
        representation, it must be converted to actual game board.
    """
    return (
        not contains_only_digits_and_spaces(line) and reduce(
            lambda x, y: x and y, [
                True if _re_board_string.match(l) else False
                for l in line.splitlines()
            ], True
        )
    )


def is_sokoban_plus_string(line):
    return contains_only_digits_and_spaces(line) and not is_blank(line)


def parse_board_string(line):
    """Tries to parse board from string

    Returns:
        list: list of board strings, each representing single board line
    """
    if is_blank(line):
        return []
    if not is_board_string(line):
        raise BoardConversionError(BoardConversionError.NON_BOARD_CHARS_FOUND)

    line = rle_decode(line)
    return normalize_width(line.split('\n'))
