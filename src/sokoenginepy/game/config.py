from __future__ import annotations

import enum
from typing import Final, List


class Direction(enum.Enum):
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
    def opposite(self) -> Direction:
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


class GraphType(enum.Enum):
    """
    Types of `BoardGraph`.
    """

    #: Directed graphs
    DIRECTED = 0

    #: Directed graphs with self loops and parallel edges
    DIRECTED_MULTI = 1


class Config:
    """
    Various constants used across game package. Since they are needed by many modules
    it made more sense to place them here in their own class, than into one or more
    other classes.
    """

    #: Max board width
    MAX_WIDTH: Final[int] = 4096

    #: Max board height
    MAX_HEIGHT: Final[int] = 4096

    #: Invalid board position
    NO_POS: Final[int] = -1

    #: Default ID for pieces for situations whe one is needed and **must** be provided.
    #:
    #: See Also:
    #:     - :class:`.BoardManager`
    #:     - :class:`.PusherStep`
    DEFAULT_ID: Final[int] = 1

    #: Invalid, non-existing ID of a piece. It is used in situations where it would
    #: be OK to use `None`, but this is more specific and has same type as piece IDs
    #: have.
    #:
    #: See Also:
    #:     - :class:`.BoardManager`
    #:     - :class:`.PusherStep`
    NO_ID: Final[int] = -1
