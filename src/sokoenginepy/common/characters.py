import re
from typing import Final, List, Optional, Set, Union


class Characters:
    WALL: Final[str] = "#"
    PUSHER: Final[str] = "@"
    PUSHER_ON_GOAL: Final[str] = "+"
    BOX: Final[str] = "$"
    BOX_ON_GOAL: Final[str] = "*"
    GOAL: Final[str] = "."
    FLOOR: Final[str] = " "
    VISIBLE_FLOOR: Final[str] = "-"
    ALT_PUSHER1: Final[str] = "p"
    ALT_PUSHER2: Final[str] = "m"
    ALT_PUSHER_ON_GOAL1: Final[str] = "P"
    ALT_PUSHER_ON_GOAL2: Final[str] = "M"
    ALT_BOX1: Final[str] = "b"
    ALT_BOX_ON_GOAL1: Final[str] = "B"
    ALT_GOAL1: Final[str] = "o"
    ALT_VISIBLE_FLOOR1: Final[str] = "_"

    PUZZLE_CHARACTERS: Final[Set[str]] = {
        WALL,
        PUSHER,
        PUSHER_ON_GOAL,
        BOX,
        BOX_ON_GOAL,
        GOAL,
        FLOOR,
        VISIBLE_FLOOR,
        ALT_PUSHER1,
        ALT_PUSHER2,
        ALT_PUSHER_ON_GOAL1,
        ALT_PUSHER_ON_GOAL2,
        ALT_BOX1,
        ALT_BOX_ON_GOAL1,
        ALT_GOAL1,
        ALT_VISIBLE_FLOOR1,
    }

    # Characters used in textual representation of game snapshot. Not all game variants
    # use all characters. Also, for different game variants, same character may have
    # different meaning (represent different direction of movement).

    l: Final[str] = "l"
    u: Final[str] = "u"
    r: Final[str] = "r"
    d: Final[str] = "d"
    L: Final[str] = "L"
    U: Final[str] = "U"
    R: Final[str] = "R"
    D: Final[str] = "D"
    w: Final[str] = "w"
    W: Final[str] = "W"
    e: Final[str] = "e"
    E: Final[str] = "E"
    n: Final[str] = "n"
    N: Final[str] = "N"
    s: Final[str] = "s"
    S: Final[str] = "S"

    JUMP_BEGIN: Final[str] = "["
    JUMP_END: Final[str] = "]"
    PUSHER_CHANGE_BEGIN: Final[str] = "{"
    PUSHER_CHANGE_END: Final[str] = "}"
    CURRENT_POSITION_CH: Final[str] = "*"

    MOVE_CHARACTERS: Final[Set[str]] = {l, u, r, d, n, s, e, w}
    PUSH_CHARACTERS: Final[Set[str]] = {L, U, R, D, N, S, E, W}

    SNAPSHOT_MARKERS: Final[Set[str]] = {
        JUMP_BEGIN,
        JUMP_END,
        PUSHER_CHANGE_BEGIN,
        PUSHER_CHANGE_END,
        CURRENT_POSITION_CH,
    }

    RLE_GROUP_START: Final[str] = "("
    RLE_GROUP_END: Final[str] = ")"
    RLE_EOL: Final[str] = "|"

    @classmethod
    def is_pusher(cls, character: str) -> bool:
        return character in (
            cls.PUSHER,
            cls.ALT_PUSHER1,
            cls.ALT_PUSHER2,
            cls.PUSHER_ON_GOAL,
            cls.ALT_PUSHER_ON_GOAL1,
            cls.ALT_PUSHER_ON_GOAL2,
        )

    @classmethod
    def is_box(cls, character: str) -> bool:
        return character in (
            cls.BOX,
            cls.ALT_BOX1,
            cls.BOX_ON_GOAL,
            cls.ALT_BOX_ON_GOAL1,
        )

    @classmethod
    def is_goal(cls, character: str) -> bool:
        return character in (
            cls.GOAL,
            cls.ALT_GOAL1,
            cls.BOX_ON_GOAL,
            cls.ALT_BOX_ON_GOAL1,
            cls.PUSHER_ON_GOAL,
            cls.ALT_PUSHER_ON_GOAL1,
            cls.ALT_PUSHER_ON_GOAL2,
        )

    @classmethod
    def is_empty_floor(cls, character: str) -> bool:
        return character in (
            cls.FLOOR,
            cls.VISIBLE_FLOOR,
            cls.ALT_VISIBLE_FLOOR1,
        )

    @classmethod
    def is_wall(cls, character: str) -> bool:
        return character == cls.WALL

    @classmethod
    def is_border_element(cls, character: str) -> bool:
        return character in (
            cls.WALL,
            cls.BOX_ON_GOAL,
            cls.ALT_BOX_ON_GOAL1,
        )

    @classmethod
    def is_puzzle_element(cls, character: str) -> bool:
        return (
            cls.is_empty_floor(character)
            or cls.is_wall(character)
            or cls.is_pusher(character)
            or cls.is_box(character)
            or cls.is_goal(character)
        )

    @classmethod
    def is_move_step(cls, character: str) -> bool:
        return character in cls.MOVE_CHARACTERS

    @classmethod
    def is_push_step(cls, character: str) -> bool:
        return character in cls.PUSH_CHARACTERS

    @classmethod
    def is_pusher_step(cls, character: str) -> bool:
        return cls.is_move_step(character) or cls.is_push_step(character)

    @classmethod
    def is_snapshot_marker(cls, character: str) -> bool:
        return character in cls.SNAPSHOT_MARKERS

    @classmethod
    def is_board(cls, line: Optional[str]) -> bool:
        """
        Checks if line contains only characters legal in textual representation of
        boards.

        Note:
            Doesn't check if it actually contains legal board, it only checks that
            there are no illegal characters.
        """
        return not cls.contains_only_digits_and_spaces(line) and all(
            cls._RE_BOARD_STRING.match(l) for l in (line or "").splitlines()
        )

    @classmethod
    def is_sokoban_plus(cls, line: str) -> bool:
        return cls.contains_only_digits_and_spaces(line) and not is_blank(line)

    _RE_BOARD_STRING = re.compile(
        r"^([0-9\s"
        + re.escape("".join(PUZZLE_CHARACTERS))
        + re.escape("".join({RLE_GROUP_START, RLE_GROUP_END, RLE_EOL}))
        + "])*$"
    )

    @classmethod
    def contains_only_digits_and_spaces(cls, line: Optional[str]) -> bool:
        return all(
            cls._RE_ONLY_DIGITS_AND_SPACES.match(l) for l in (line or "").splitlines()
        )

    _RE_ONLY_DIGITS_AND_SPACES = re.compile(r"^([0-9\s])*$")

    @classmethod
    def is_snapshot(cls, line: str) -> bool:
        """
        True if ``line`` contains only:

        - movement characters
        - other snapshot characters (ie. jump markers)
        - Rle characters
        - spaces and newlines
        """
        return (
            not is_blank(line)
            and not Characters.contains_only_digits_and_spaces(line)
            and all(bool(cls._RE_SNAPSHOT_STRING.match(l)) for l in line.splitlines())
        )

    _RE_SNAPSHOT_STRING = re.compile(
        r"^([0-9\s"
        + re.escape("".join(MOVE_CHARACTERS))
        + re.escape("".join(PUSH_CHARACTERS))
        + re.escape("".join(SNAPSHOT_MARKERS))
        + re.escape("".join({RLE_GROUP_START, RLE_GROUP_END, RLE_EOL}))
        + "])*$"
    )


def is_blank(data: Optional[Union[str, List[str]]]) -> bool:
    """Line is blank if it is either length 0 or contains only spaces."""

    _check = lambda l: l is None or l.strip() == ""

    if not data:
        return True

    if isinstance(data, str):
        return _check(data)

    return all(_check(_) for _ in data)
