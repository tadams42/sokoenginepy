from __future__ import annotations

from typing import Final, Mapping, Optional, Tuple

from ...atomic_move import AtomicMove
from ...direction import Direction
from ...graph_type import GraphType
from ...utilities import COLUMN, ROW, index_1d, inverted, is_on_board_2d
from ..cell_orientation import CellOrientation
from ..tessellation_base import TessellationBase


class TriobanTessellation(TessellationBase):
    """
    Board is laid out on alternating triangles with origin triangle poiting down.

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

    _CHR_TO_ATOMIC_MOVE: Final[Mapping[str, Tuple[Direction, bool]]] = {
        AtomicMove.l: (Direction.LEFT, False),
        AtomicMove.L: (Direction.LEFT, True),
        AtomicMove.r: (Direction.RIGHT, False),
        AtomicMove.R: (Direction.RIGHT, True),
        AtomicMove.n: (Direction.NORTH_EAST, False),
        AtomicMove.N: (Direction.NORTH_EAST, True),
        AtomicMove.u: (Direction.NORTH_WEST, False),
        AtomicMove.U: (Direction.NORTH_WEST, True),
        AtomicMove.d: (Direction.SOUTH_EAST, False),
        AtomicMove.D: (Direction.SOUTH_EAST, True),
        AtomicMove.s: (Direction.SOUTH_WEST, False),
        AtomicMove.S: (Direction.SOUTH_WEST, True),
    }

    _ATOMIC_MOVE_TO_CHR: Final[Mapping[Tuple[Direction, bool], str]] = inverted(
        _CHR_TO_ATOMIC_MOVE
    )

    @property
    def graph_type(self) -> GraphType:
        return GraphType.DIRECTED_MULTI

    def neighbor_position(
        self, position: int, direction: Direction, board_width: int, board_height: int
    ) -> Optional[int]:
        row = ROW(position, board_width)
        column = COLUMN(position, board_width)
        triangle_points_down = (
            self.cell_orientation(position, board_width, board_height)
            == CellOrientation.TRIANGLE_DOWN
        )

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

        return None

    def cell_orientation(
        self, position: int, board_width: int, board_height: int
    ) -> CellOrientation:
        row = ROW(position, board_width)
        column = COLUMN(position, board_width)
        return (
            CellOrientation.TRIANGLE_DOWN
            if (column + (row % 2)) % 2 == 0
            else CellOrientation.DEFAULT
        )

    def __str__(self):
        return "trioban"
