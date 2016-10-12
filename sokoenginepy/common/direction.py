from enum import IntEnum

from .exceptions import SokoengineError


class UnknownDirectionError(SokoengineError):
    pass


class Direction(IntEnum):
    """Directions of movement."""
    UP = 0
    NORTH_EAST = 1
    RIGHT = 2
    SOUTH_EAST = 3
    DOWN = 4
    SOUTH_WEST = 5
    LEFT = 6
    NORTH_WEST = 7

    @property
    def opposite(self):
        if self == Direction.UP:
            retv = Direction.DOWN
        elif self == Direction.DOWN:
            retv = Direction.UP
        elif self == Direction.LEFT:
            retv = Direction.RIGHT
        elif self == Direction.RIGHT:
            retv = Direction.LEFT
        elif self == Direction.NORTH_WEST:
            retv = Direction.SOUTH_EAST
        elif self == Direction.NORTH_EAST:
            retv = Direction.SOUTH_WEST
        elif self == Direction.SOUTH_WEST:
            retv = Direction.NORTH_EAST
        elif self == Direction.SOUTH_EAST:
            retv = Direction.NORTH_WEST
        else:
            retv = None
        return retv
