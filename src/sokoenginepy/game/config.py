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
    Type of board graph.
    """

    DIRECTED = 0
    DIRECTED_MULTI = 1


class Config:
    MAX_WIDTH: Final[int] = 4096
    MAX_HEIGHT: Final[int] = 4096
    MAX_POS: Final[int] = MAX_WIDTH * MAX_HEIGHT

    NULL_ID: Final[int] = 0

    #: All pieces on board (pushers, boxes) and goals are assigned ID to be used for
    #: referring them.
    #:
    #: Piece ids are assigned by numbering each type of piece or goal starting with
    #: ``DEFAULT_PIECE_ID``
    #:
    #: .. image:: /images/assigning_ids.png
    #:     :alt: Assigning IDs to pieces and goals
    #:
    #: Once assigned, id of a piece doesn't change by either moving piece or
    #: applying board view transformations.
    DEFAULT_PIECE_ID: Final[int] = 1
