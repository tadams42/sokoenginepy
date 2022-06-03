from __future__ import annotations

from typing import Dict, Final, Optional, Tuple

from ..io import Snapshot
from .direction import Direction
from .tessellation_base import TessellationBase
from .utilities import COLUMN, ROW, index_1d, inverted, is_on_board_2d


class SokobanTessellation(TessellationBase):
    """
    Board is laid out on squares.

    Direction <-> character mapping:

    ====  =====  ====  ====
    LEFT  RIGHT  UP    DOWN
    ====  =====  ====  ====
    l, L  r, R   u, U  d, D
    ====  =====  ====  ====
    """

    _LEGAL_DIRECTIONS: Final[Tuple[Direction, ...]] = (
        Direction.LEFT,
        Direction.RIGHT,
        Direction.UP,
        Direction.DOWN,
    )

    _CHR_TO_ATOMIC_MOVE: Final[Dict[str, Tuple[Direction, bool]]] = {
        Snapshot.l: (Direction.LEFT, False),
        Snapshot.L: (Direction.LEFT, True),
        Snapshot.r: (Direction.RIGHT, False),
        Snapshot.R: (Direction.RIGHT, True),
        Snapshot.u: (Direction.UP, False),
        Snapshot.U: (Direction.UP, True),
        Snapshot.d: (Direction.DOWN, False),
        Snapshot.D: (Direction.DOWN, True),
    }

    _ATOMIC_MOVE_TO_CHR: Final[Dict[Tuple[Direction, bool], str]] = inverted(
        _CHR_TO_ATOMIC_MOVE
    )

    _NEIGHBOR_SHIFT: Final[Dict[Direction, Tuple[int, int]]] = {
        Direction.LEFT: (0, -1),
        Direction.RIGHT: (0, 1),
        Direction.UP: (-1, 0),
        Direction.DOWN: (1, 0),
    }

    def neighbor_position(
        self, position: int, direction: Direction, board_width: int, board_height: int
    ) -> Optional[int]:
        row = ROW(position, board_width)
        column = COLUMN(position, board_width)
        row_shift, column_shift = self._NEIGHBOR_SHIFT.get(direction, (None, None))

        if row_shift is None or column_shift is None:
            raise ValueError(direction)

        row += row_shift
        column += column_shift

        if is_on_board_2d(column, row, board_width, board_height):
            return index_1d(column, row, board_width)

        return None

    def __str__(self):
        return "sokoban"