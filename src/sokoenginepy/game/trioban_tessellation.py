from __future__ import annotations

from typing import Final, Mapping, Tuple

from ..io import CellOrientation, Snapshot
from .base_tessellation import BaseTessellation
from .config import Config, Direction, GraphType
from .coordinate_helpers import index_1d, index_column, index_row, is_on_board_2d
from .utilities import inverted


class TriobanTessellation(BaseTessellation):
    """
    Tessellation for Trioban game variant.

    Board is laid out on alternating triangles with origin triangle pointing down.

    Direction <-> character mapping:

    ====  =====  ==========  ==========  ==========  ==========
    LEFT  RIGHT  NORTH_EAST  NORTH_WEST  SOUTH_EAST  SOUTH_WEST
    ====  =====  ==========  ==========  ==========  ==========
    l, L  r, R   n, N        u, U        d, D        s, S
    ====  =====  ==========  ==========  ==========  ==========

    Depending on pusher position, not all move directions are allowed on all board
    positions:

    .. image:: /images/trioban_am.png
        :alt: Trioban movement
    """

    _LEGAL_DIRECTIONS: Final[Tuple[Direction, ...]] = (
        Direction.LEFT,
        Direction.RIGHT,
        Direction.NORTH_EAST,
        Direction.NORTH_WEST,
        Direction.SOUTH_EAST,
        Direction.SOUTH_WEST,
    )

    _CHR_TO_PUSHER_STEP: Final[Mapping[str, Tuple[Direction, bool]]] = {
        Snapshot.l: (Direction.LEFT, False),
        Snapshot.L: (Direction.LEFT, True),
        Snapshot.r: (Direction.RIGHT, False),
        Snapshot.R: (Direction.RIGHT, True),
        Snapshot.n: (Direction.NORTH_EAST, False),
        Snapshot.N: (Direction.NORTH_EAST, True),
        Snapshot.u: (Direction.NORTH_WEST, False),
        Snapshot.U: (Direction.NORTH_WEST, True),
        Snapshot.d: (Direction.SOUTH_EAST, False),
        Snapshot.D: (Direction.SOUTH_EAST, True),
        Snapshot.s: (Direction.SOUTH_WEST, False),
        Snapshot.S: (Direction.SOUTH_WEST, True),
    }

    _PUSHER_STEP_TO_CHR: Final[Mapping[Tuple[Direction, bool], str]] = inverted(
        _CHR_TO_PUSHER_STEP
    )

    @property
    def graph_type(self) -> GraphType:
        return GraphType.DIRECTED_MULTI

    def neighbor_position(
        self, position: int, direction: Direction, board_width: int, board_height: int
    ) -> int:
        triangle_points_down = (
            self.cell_orientation(position, board_width, board_height)
            == CellOrientation.TRIANGLE_DOWN
        )
        row = index_row(position, board_width)
        column = index_column(position, board_width)

        dx, dy = 0, 0
        if direction == Direction.LEFT:
            dy = 0
            dx = -1
        elif direction == Direction.RIGHT:
            dy = 0
            dx = 1
        elif direction == Direction.NORTH_EAST:
            if triangle_points_down:
                dy = -1
                dx = 0
            else:
                dy = 0
                dx = 1
        elif direction == Direction.NORTH_WEST:
            if triangle_points_down:
                dy = -1
                dx = 0
            else:
                dy = 0
                dx = -1
        elif direction == Direction.SOUTH_EAST:
            if triangle_points_down:
                dy = 0
                dx = 1
            else:
                dy = 1
                dx = 0
        elif direction == Direction.SOUTH_WEST:
            if triangle_points_down:
                dy = 0
                dx = -1
            else:
                dy = 1
                dx = 0
        else:
            raise ValueError(direction)

        row += dy
        column += dx

        if is_on_board_2d(column, row, board_width, board_height):
            return index_1d(column, row, board_width)

        return Config.NO_POS

    def cell_orientation(
        self, position: int, board_width: int, board_height: int
    ) -> CellOrientation:
        if position < 0:
            raise IndexError(f"Position {position} is invalid value!")

        if board_width < 0:
            raise ValueError(f"Board width {board_width} is invalid value!")

        if board_height < 0:
            raise ValueError(f"Board height {board_height} is invalid value!")

        row = index_row(position, board_width)
        column = index_column(position, board_width)
        return (
            CellOrientation.TRIANGLE_DOWN
            if (column + (row % 2)) % 2 == 0
            else CellOrientation.DEFAULT
        )
