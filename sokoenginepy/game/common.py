from enum import Enum


class GameSolvingMode(Enum):
    """
    Game solving mode
    """
    FORWARD = 0
    REVERSE = 1


class PieceConstants(object):
    DEFAULT_ID = 1
    DEFAULT_PLUS_ID = 0
