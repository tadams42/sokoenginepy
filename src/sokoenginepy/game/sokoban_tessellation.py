from __future__ import annotations

from typing import Dict, Final, List, Optional, Tuple

from ..io import Snapshot
from .base_tessellation import BaseTessellation
from .config import Config, Direction
from .coordinate_helpers import index_1d, index_column, index_row, is_on_board_2d
from .utilities import inverted


class SokobanTessellation(BaseTessellation):
    """
    Tessellation for Sokoban game variant.

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

    _CHR_TO_PUSHER_STEP: Final[Dict[str, Tuple[Direction, bool]]] = {
        Snapshot.l: (Direction.LEFT, False),
        Snapshot.L: (Direction.LEFT, True),
        Snapshot.r: (Direction.RIGHT, False),
        Snapshot.R: (Direction.RIGHT, True),
        Snapshot.u: (Direction.UP, False),
        Snapshot.U: (Direction.UP, True),
        Snapshot.d: (Direction.DOWN, False),
        Snapshot.D: (Direction.DOWN, True),
    }

    _PUSHER_STEP_TO_CHR: Final[Dict[Tuple[Direction, bool], str]] = inverted(
        _CHR_TO_PUSHER_STEP
    )

    _NEIGHBOR_SHIFT: Final[List[Tuple[Optional[int], Optional[int]]]] = [
        (-1, 0),  # UP
        (None, None),
        (0, 1),  # RIGHT
        (None, None),
        (1, 0),  # DOWN
        (None, None),
        (0, -1),  # LEFT
        (None, None),
    ]

    def neighbor_position(
        self, position: int, direction: Direction, board_width: int, board_height: int
    ) -> int:
        if position < 0:
            raise IndexError(f"Position {position} is invalid value!")

        if board_width < 0:
            raise ValueError(f"Board width {board_width} is invalid value!")

        if board_height < 0:
            raise ValueError(f"Board height {board_height} is invalid value!")

        row = index_row(position, board_width)
        column = index_column(position, board_width)
        row_shift, column_shift = self._NEIGHBOR_SHIFT[direction.value]

        if row_shift is None or column_shift is None:
            raise ValueError(direction)

        row += row_shift
        column += column_shift

        if is_on_board_2d(column, row, board_width, board_height):
            return index_1d(column, row, board_width)

        return Config.NO_POS
