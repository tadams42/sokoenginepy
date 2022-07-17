from __future__ import annotations

import enum
from typing import Optional


def index_1d(x: int, y: int, board_width: int) -> int:
    """Converts 2D coordinate to board position index."""
    return y * board_width + x


def index_x(index: int, board_width: int) -> int:
    """x component of board position index."""
    return 0 if board_width == 0 else index % board_width


def index_y(index: int, board_width: int) -> int:
    """y component of board position index."""
    return 0 if board_width == 0 else int(index / board_width)


def index_row(index: int, board_width: int) -> int:
    """x component of board position index."""
    return index_y(index, board_width)


def index_column(index: int, board_width: int) -> int:
    """y component of board position index."""
    return index_x(index, board_width)


def is_on_board_2d(x: int, y: int, board_width: int, board_height: int) -> bool:
    return x >= 0 and y >= 0 and x < board_width and y < board_height


def is_on_board_1d(index: Optional[int], board_width: int, board_height: int) -> bool:
    return (
        index is not None
        and index >= 0
        and is_on_board_2d(
            index_x(index, board_width),
            index_y(index, board_width),
            board_width,
            board_height,
        )
    )


class Tessellation(enum.Enum):
    """All game tessellations."""

    #: Tessellation for Sokoban game variant.
    #:
    #: Board is laid out on squares.
    #:
    #: Direction <-> character mapping:
    #:
    #: ====  =====  ====  ====
    #: LEFT  RIGHT  UP    DOWN
    #: ====  =====  ====  ====
    #: l, L  r, R   u, U  d, D
    #: ====  =====  ====  ====
    SOKOBAN = 0

    #: Tessellation for Hexoban game variant.
    #:
    #: Board space is laid out on vertical hexagons with following coordinate system:
    #:
    #: .. image:: /images/hexoban_coordinates.png
    #:    :alt: Hexoban coordinates
    #:
    #: Textual representation uses two characters for each hexagon. This allows different
    #: encoding schemes.
    #:
    #: .. |img1| image:: /images/hexoban_scheme1.png
    #: .. |img2| image:: /images/hexoban_scheme2.png
    #:
    #: +----------+----------+
    #: | Scheme 1 | Scheme 2 |
    #: +==========+==========+
    #: |  |img1|  |  |img2|  |
    #: +----------+----------+
    #:
    #: As long as encoding of single board is consistent, all methods handle any scheme
    #: transparently - parsing of board strings 'Just Works (TM)'
    #:
    #: Direction <-> character mapping:
    #:
    #: ====  =====  ==========  ==========  ==========  ==========
    #: LEFT  RIGHT  NORTH_WEST  SOUTH_WEST  NORTH_EAST  SOUTH_EAST
    #: ====  =====  ==========  ==========  ==========  ==========
    #: l, L  r, R   u, U        d, D        n, N        s, S
    #: ====  =====  ==========  ==========  ==========  ==========
    HEXOBAN = 1

    #: Tessellation for Trioban game variant.
    #:
    #: Board is laid out on alternating triangles with origin triangle pointing down.
    #:
    #: Direction <-> character mapping:
    #:
    #: ====  =====  ==========  ==========  ==========  ==========
    #: LEFT  RIGHT  NORTH_EAST  NORTH_WEST  SOUTH_EAST  SOUTH_WEST
    #: ====  =====  ==========  ==========  ==========  ==========
    #: l, L  r, R   n, N        u, U        d, D        s, S
    #: ====  =====  ==========  ==========  ==========  ==========
    #:
    #: Depending on pusher position, not all move directions are allowed on all board
    #: positions:
    #:
    #: .. image:: /images/trioban_am.png
    #:     :alt: Trioban movement
    TRIOBAN = 2

    #: Tessellation for Octoban game variant.
    #:
    #: Board space is laid out on alternating squares and octagons with origin of
    #: coordinate system being octagon. Tessellation allows all 8 directions of movement
    #: from Direction and depending on current pusher position some of these directions do
    #: not result in successful move.
    #:
    #: Direction <-> character mapping:
    #:
    #: ====  ==========  =====  ==========  ====  ==========  ====  ==========
    #: UP    NORTH_EAST  RIGHT  SOUTH_EAST  DOWN  SOUTH_WEST  LEFT  NORTH_WEST
    #: ====  ==========  =====  ==========  ====  ==========  ====  ==========
    #: u, U  n, N        r, R   e, E        d, D  s, S        l, L  w, W
    #: ====  ==========  =====  ==========  ====  ==========  ====  ==========
    OCTOBAN = 3
