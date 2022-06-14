from __future__ import annotations

from typing import Dict, Final, Optional, Tuple

from ..io import Snapshot
from .base_tessellation import COLUMN, ROW, BaseTessellation, index_1d, is_on_board_2d
from .config import Direction
from .utilities import inverted


class HexobanTessellation(BaseTessellation):

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

    _CHR_TO_PUSHER_STEP: Final[Dict[str, Tuple[Direction, bool]]] = {
        Snapshot.l: (Direction.LEFT, False),
        Snapshot.L: (Direction.LEFT, True),
        Snapshot.r: (Direction.RIGHT, False),
        Snapshot.R: (Direction.RIGHT, True),
        Snapshot.u: (Direction.NORTH_WEST, False),
        Snapshot.U: (Direction.NORTH_WEST, True),
        Snapshot.d: (Direction.SOUTH_EAST, False),
        Snapshot.D: (Direction.SOUTH_EAST, True),
        Snapshot.n: (Direction.NORTH_EAST, False),
        Snapshot.N: (Direction.NORTH_EAST, True),
        Snapshot.s: (Direction.SOUTH_WEST, False),
        Snapshot.S: (Direction.SOUTH_WEST, True),
    }

    _PUSHER_STEP_TO_CHR: Final[Dict[Tuple[Direction, bool], str]] = inverted(
        _CHR_TO_PUSHER_STEP
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
