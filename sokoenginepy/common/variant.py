from enum import IntEnum

from .exceptions import SokoengineError


class UnknownVariantError(SokoengineError):
    pass


class Variant(IntEnum):
    """Implemented tessellation types.

    All classes that are tessellation dependant have attribute variant whose
    value is one of these.
    """

    SOKOBAN = 0
    """
    Board is laid out on squares. Direction <-> character mapping:

    ====  =====  ====  ====
    LEFT  RIGHT  UP    DOWN
    ====  =====  ====  ====
    l, L  r, R   u, U  d, D
    ====  =====  ====  ====
    """

    TRIOBAN = 1
    """
    Board is laid out on alternating triangles with origin triangle poiting
    down. Direction <-> character mapping:

    ====  =====  ==========  ==========  ==========  ==========
    LEFT  RIGHT  NORTH_EAST  NORTH_WEST  SOUTH_EAST  SOUTH_WEST
    ====  =====  ==========  ==========  ==========  ==========
    l, L  r, R   n, N        u, U        d, D        s, S
    ====  =====  ==========  ==========  ==========  ==========

    Depending on current pusher position, some moves are not allowed:

    .. image:: /images/trioban_am.png
        :alt: Trioban movement
    """

    HEXOBAN = 2
    """
    Board space is laid out on vertical hexagons with following coordinate
    system:

    .. image:: /images/hexoban_coordinates.png
        :alt: Hexoban coordinates

    Textual representation uses two characters for each hexagon. This allows
    different encoding schemes.

    +----------------------------------------+---------------------------------------------+
    | Scheme 1                               | Scheme 2                                    |
    +========================================+=============================================+
    | .. image:: /images/hexoban_scheme1.png | .. image:: /images/hexoban_scheme2.png      |
    |     :alt: Scheme 1                     |     :alt: Scheme 2                          |
    +----------------------------------------+---------------------------------------------+

    As long as encoding of single board is consistent, all methods handle any
    scheme transparently - parsing of board strings 'Just Works (TM)'

    Direction <-> character mapping:

    ====  =====  ==========  ==========  ==========  ==========
    LEFT  RIGHT  NORTH_WEST  SOUTH_WEST  NORTH_EAST  SOUTH_EAST
    ====  =====  ==========  ==========  ==========  ==========
    l, L  r, R   u, U        d, D        n, N        s, S
    ====  =====  ==========  ==========  ==========  ==========
    """

    OCTOBAN = 3
    """
    Board space is laid out on alternating squares and octagons with
    origin of coordinate system being octagon. Tessellation allows all
    8 directions of movement from Direction and depending on current
    pusher position some of these directions do not result in successful
    move.

    Direction <-> character mapping:

    ====  ==========  =====  ==========  ====  ==========  ====  ==========
    UP    NORTH_EAST  RIGHT  SOUTH_EAST  DOWN  SOUTH_WEST  LEFT  NORTH_WEST
    ====  ==========  =====  ==========  ====  ==========  ====  ==========
    u, U  n, N        r, R   e, E        d, D  s, S        l, L  w, W
    ====  ==========  =====  ==========  ====  ==========  ====  ==========
    """

    def to_s(self):
        if self == self.SOKOBAN:
            return "Sokoban"
        elif self == self.HEXOBAN:
            return "Hexoban"
        elif self == self.TRIOBAN:
            return "Trioban"
        elif self == self.OCTOBAN:
            return "Octoban"
        else:
            raise UnknownVariantError(self)

    @classmethod
    def factory(cls, description):
        if isinstance(description, str):
            description = description.strip().lower()

        if description == "sokoban" or description == "" or description == cls.SOKOBAN:
            return cls.SOKOBAN
        elif description == 'trioban' or description == cls.TRIOBAN:
            return cls.TRIOBAN
        elif description == 'hexoban' or description == cls.HEXOBAN:
            return cls.HEXOBAN
        elif description == 'octoban' or description == cls.OCTOBAN:
            return cls.OCTOBAN
        else:
            raise UnknownVariantError(description)
