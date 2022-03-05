from enum import Enum
from typing import Union

from .. import utilities
from .hexoban_tessellation import HexobanTessellation
from .octoban_tessellation import OctobanTessellation
from .sokoban_tessellation import SokobanTessellation
from .trioban_tessellation import TriobanTessellation


class Tessellation(Enum):
    """Implemented tessellation types."""

    #: Board is laid out on squares. Direction <-> character mapping
    #:
    #: ====  =====  ====  ====
    #: LEFT  RIGHT  UP    DOWN
    #: ====  =====  ====  ====
    #: l, L  r, R   u, U  d, D
    #: ====  =====  ====  ====
    SOKOBAN = SokobanTessellation()

    #: Board is laid out on alternating triangles with origin triangle poiting
    #: down. Direction <-> character mapping
    #:
    #: ====  =====  ==========  ==========  ==========  ==========
    #: LEFT  RIGHT  NORTH_EAST  NORTH_WEST  SOUTH_EAST  SOUTH_WEST
    #: ====  =====  ==========  ==========  ==========  ==========
    #: l, L  r, R   n, N        u, U        d, D        s, S
    #: ====  =====  ==========  ==========  ==========  ==========
    #:
    #: Depending on current pusher position, some moves are not allowed:
    #:
    #: .. image:: /images/trioban_am.png
    #:     :alt: Trioban movement
    TRIOBAN = TriobanTessellation()

    #: Board space is laid out on vertical hexagons with following coordinate
    #: system:
    #:
    #: .. image:: /images/hexoban_coordinates.png
    #:     :alt: Hexoban coordinates
    #:
    #: Textual representation uses two characters for each hexagon. This allows
    #: different encoding schemes.
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
    #: As long as encoding of single board is consistent, all methods handle any
    #: scheme transparently - parsing of board strings 'Just Works (TM)'
    #:
    #: Direction <-> character mapping:
    #:
    #: ====  =====  ==========  ==========  ==========  ==========
    #: LEFT  RIGHT  NORTH_WEST  SOUTH_WEST  NORTH_EAST  SOUTH_EAST
    #: ====  =====  ==========  ==========  ==========  ==========
    #: l, L  r, R   u, U        d, D        n, N        s, S
    #: ====  =====  ==========  ==========  ==========  ==========
    HEXOBAN = HexobanTessellation()

    #: Board space is laid out on alternating squares and octagons with
    #: origin of coordinate system being octagon. Tessellation allows all
    #: 8 directions of movement from Direction and depending on current
    #: pusher position some of these directions do not result in successful
    #: move.
    #:
    #: Direction <-> character mapping:
    #:
    #: ====  ==========  =====  ==========  ====  ==========  ====  ==========
    #: UP    NORTH_EAST  RIGHT  SOUTH_EAST  DOWN  SOUTH_WEST  LEFT  NORTH_WEST
    #: ====  ==========  =====  ==========  ====  ==========  ====  ==========
    #: u, U  n, N        r, R   e, E        d, D  s, S        l, L  w, W
    #: ====  ==========  =====  ==========  ====  ==========  ====  ==========
    OCTOBAN = OctobanTessellation()

    def __str__(self):
        return self.name.title()

    def __repr__(self):
        return "Tessellation." + self.name

    @classmethod
    def instance_from(
        cls,
        tessellation_or_description: Union[
            SokobanTessellation,
            TriobanTessellation,
            HexobanTessellation,
            OctobanTessellation,
            str,
        ],
    ) -> "Tessellation":
        if (
            not tessellation_or_description
            or "sokoban" in str(tessellation_or_description).lower()
            or utilities.is_blank(str(tessellation_or_description))
        ):
            return cls.SOKOBAN
        elif "trioban" in str(tessellation_or_description).lower():
            return cls.TRIOBAN
        elif "hexoban" in str(tessellation_or_description).lower():
            return cls.HEXOBAN
        elif "octoban" in str(tessellation_or_description).lower():
            return cls.OCTOBAN
        else:
            raise ValueError(tessellation_or_description)
