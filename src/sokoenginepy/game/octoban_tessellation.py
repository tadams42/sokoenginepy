from __future__ import annotations

from typing import Dict, Final, Optional, Tuple

from ..io import CellOrientation, Snapshot
from .base_tessellation import COLUMN, ROW, BaseTessellation, index_1d, is_on_board_2d
from .config import Direction
from .utilities import inverted


class OctobanTessellation(BaseTessellation):
    """
    Board space is laid out on alternating squares and octagons with origin of
    coordinate system being octagon. Tessellation allows all 8 directions of movement
    from Direction and depending on current pusher position some of these directions do
    not result in successful move.

    Direction <-> character mapping:

    ====  ==========  =====  ==========  ====  ==========  ====  ==========
    UP    NORTH_EAST  RIGHT  SOUTH_EAST  DOWN  SOUTH_WEST  LEFT  NORTH_WEST
    ====  ==========  =====  ==========  ====  ==========  ====  ==========
    u, U  n, N        r, R   e, E        d, D  s, S        l, L  w, W
    ====  ==========  =====  ==========  ====  ==========  ====  ==========
    """

    _LEGAL_DIRECTIONS: Final[Tuple[Direction, ...]] = (
        Direction.LEFT,
        Direction.RIGHT,
        Direction.UP,
        Direction.DOWN,
        Direction.NORTH_EAST,
        Direction.NORTH_WEST,
        Direction.SOUTH_EAST,
        Direction.SOUTH_WEST,
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
        Snapshot.w: (Direction.NORTH_WEST, False),
        Snapshot.W: (Direction.NORTH_WEST, True),
        Snapshot.e: (Direction.SOUTH_EAST, False),
        Snapshot.E: (Direction.SOUTH_EAST, True),
        Snapshot.n: (Direction.NORTH_EAST, False),
        Snapshot.N: (Direction.NORTH_EAST, True),
        Snapshot.s: (Direction.SOUTH_WEST, False),
        Snapshot.S: (Direction.SOUTH_WEST, True),
    }

    _PUSHER_STEP_TO_CHR: Final[Dict[Tuple[Direction, bool], str]] = inverted(
        _CHR_TO_PUSHER_STEP
    )

    _NEIGHBOR_SHIFT: Final[Dict[Direction, Tuple[int, int]]] = {
        Direction.LEFT: (0, -1),
        Direction.RIGHT: (0, 1),
        Direction.UP: (-1, 0),
        Direction.DOWN: (1, 0),
        Direction.NORTH_WEST: (-1, -1),
        Direction.NORTH_EAST: (-1, 1),
        Direction.SOUTH_WEST: (1, -1),
        Direction.SOUTH_EAST: (1, 1),
    }

    def neighbor_position(
        self, position: int, direction: Direction, board_width: int, board_height: int
    ) -> Optional[int]:
        if self.cell_orientation(
            position, board_width, board_height
        ) != CellOrientation.OCTAGON and (
            direction == Direction.NORTH_EAST
            or direction == Direction.NORTH_WEST
            or direction == Direction.SOUTH_EAST
            or direction == Direction.SOUTH_WEST
        ):
            return None

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

    def cell_orientation(
        self, position: int, board_width: int, board_height: int
    ) -> CellOrientation:
        row = ROW(position, board_width)
        column = COLUMN(position, board_width)
        return (
            CellOrientation.OCTAGON
            if (column + (row % 2)) % 2 == 0
            else CellOrientation.DEFAULT
        )
