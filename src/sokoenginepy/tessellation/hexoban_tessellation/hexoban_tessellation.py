from __future__ import annotations

from typing import Dict, Final, Optional, Tuple

from ...atomic_move import AtomicMove
from ...direction import Direction
from ...utilities import COLUMN, ROW, index_1d, inverted, is_on_board_2d
from ..tessellation_base import TessellationBase


class HexobanTessellation(TessellationBase):
    """
    Board space is laid out on vertical hexagons with following coordinate system:

    .. image:: /images/hexoban_coordinates.png
        :alt: Hexoban coordinates

    Textual representation uses two characters for each hexagon. This allows different
    encoding schemes.

    .. |img1| image:: /images/hexoban_scheme1.png
    .. |img2| image:: /images/hexoban_scheme2.png

    +----------+----------+
    | Scheme 1 | Scheme 2 |
    +==========+==========+
    |  |img1|  |  |img2|  |
    +----------+----------+

    As long as encoding of single board is consistent, all methods handle any scheme
    transparently - parsing of board strings 'Just Works (TM)'

    Direction <-> character mapping:

    ====  =====  ==========  ==========  ==========  ==========
    LEFT  RIGHT  NORTH_WEST  SOUTH_WEST  NORTH_EAST  SOUTH_EAST
    ====  =====  ==========  ==========  ==========  ==========
    l, L  r, R   u, U        d, D        n, N        s, S
    ====  =====  ==========  ==========  ==========  ==========
    """

    _LEGAL_DIRECTIONS: Final[Tuple[Direction, ...]] = (
        Direction.LEFT,
        Direction.RIGHT,
        Direction.NORTH_EAST,
        Direction.NORTH_WEST,
        Direction.SOUTH_EAST,
        Direction.SOUTH_WEST,
    )

    _CHR_TO_ATOMIC_MOVE: Final[Dict[str, Tuple[Direction, bool]]] = {
        AtomicMove.l: (Direction.LEFT, False),
        AtomicMove.L: (Direction.LEFT, True),
        AtomicMove.r: (Direction.RIGHT, False),
        AtomicMove.R: (Direction.RIGHT, True),
        AtomicMove.u: (Direction.NORTH_WEST, False),
        AtomicMove.U: (Direction.NORTH_WEST, True),
        AtomicMove.d: (Direction.SOUTH_EAST, False),
        AtomicMove.D: (Direction.SOUTH_EAST, True),
        AtomicMove.n: (Direction.NORTH_EAST, False),
        AtomicMove.N: (Direction.NORTH_EAST, True),
        AtomicMove.s: (Direction.SOUTH_WEST, False),
        AtomicMove.S: (Direction.SOUTH_WEST, True),
    }

    _ATOMIC_MOVE_TO_CHR: Final[Dict[Tuple[Direction, bool], str]] = inverted(
        _CHR_TO_ATOMIC_MOVE
    )

    def neighbor_position(
        self, position: int, direction: Direction, board_width: int, board_height: int
    ) -> Optional[int]:
        row = ROW(position, board_width)
        column = COLUMN(position, board_width)

        if direction == Direction.LEFT:
            column -= 1
        elif direction == Direction.RIGHT:
            column += 1
        elif direction == Direction.NORTH_EAST:
            column += row % 2
            row -= 1
        elif direction == Direction.NORTH_WEST:
            column -= (row + 1) % 2
            row -= 1
        elif direction == Direction.SOUTH_EAST:
            column += row % 2
            row += 1
        elif direction == Direction.SOUTH_WEST:
            column -= (row + 1) % 2
            row += 1
        else:
            raise ValueError(direction)

        if is_on_board_2d(column, row, board_width, board_height):
            return index_1d(column, row, board_width)
        return None

    def __str__(self):
        return "hexoban"
