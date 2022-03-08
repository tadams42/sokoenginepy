from enum import IntEnum
from typing import List


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

    def __repr__(self):
        return "Direction." + self.name

    @property
    def opposite(self) -> "Direction":
        return _OPPOSITE[self.value]


_OPPOSITE: List[Direction] = [
    Direction.DOWN,
    Direction.SOUTH_WEST,
    Direction.LEFT,
    Direction.NORTH_WEST,
    Direction.UP,
    Direction.NORTH_EAST,
    Direction.RIGHT,
    Direction.SOUTH_EAST,
]
