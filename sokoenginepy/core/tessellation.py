from enum import Enum
from abc import ABC, abstractmethod
from .exceptions import UnknownTessellationError, IllegalDirectionError


class Direction(Enum):
    """
    Directions of movement
    """
    UP         = 0
    NORTH_EAST = 1
    RIGHT      = 2
    SOUTH_EAST = 3
    DOWN       = 4
    SOUTH_WEST = 5
    LEFT       = 6
    NORTH_WEST = 7

    @property
    def opposite(self):
        if self == Direction.UP:
            return Direction.DOWN
        elif self == Direction.DOWN:
            return Direction.UP
        elif self == Direction.LEFT:
            return Direction.RIGHT
        elif self == Direction.RIGHT:
            return Direction.LEFT
        elif self == Direction.NORTH_WEST:
            return Direction.SOUTH_EAST
        elif self == Direction.NORTH_EAST:
            return Direction.SOUTH_WEST
        elif self == Direction.SOUTH_WEST:
            return Direction.NORTH_EAST
        elif self == Direction.SOUTH_EAST:
            return Direction.NORTH_WEST


class CellOrientation(Enum):
    """
    Dynamic board cell property that depends on cell position in some
    tessellations. ie. in Trioban, coordinate origin is triangle pointig upwards.
    This means that orientation of all other triangles depends on their position.
    Methods that calculate orientation return one of these values.
    """
    DEFAULT = 0
    TRIANGLE_DOWN = 1
    OCTAGON = 2


class Variant(Enum):
    """
    Enumerates implemented tessellation types. All classes that are tessellation
    dependant have attribute variant whose value is one of these.
    """

    """
    Board is laid out on squares.
    Direction <-> character mapping:

    |   LEFT  |  RIGHT  |    UP   |   DOWN  |
    |:-------:|:-------:|:-------:|:-------:|
    |   l, L  |   r, R  |   u, U  |  d, D   |
    """
    SOKOBAN = 0

    """
    Board is laid out on alternating triangles with origin triangle poiting down.
    Direction <-> character mapping:

    | LEFT | RIGHT | NORTH_EAST | NORTH_WEST | SOUTH_EAST | SOUTH_WEST |
    |:----:|:-----:|:----------:|:----------:|:----------:|:----------:|
    | l, L |  r, R |    n, N    |    u, U    |    d, D    |    s, S    |

    Depending on current pusher position, some moves are not allowed:

    ![Trioban movement](docs/images/trioban_am.png)
    """
    TRIOBAN = 1

    """
    Board space is laid out on vertical hexagons with following coordinate system:

    ![Hexoban coordinates](docs/images/hexoban_coordinates.png)

    Textual representation uses two characters for each hexagon. This allows
    different encoding schemes.

    |            Scheme 1          |            Scheme 2          |
    | :--------------------------: |:----------------------------:|
    | ![Scheme 1][hexoban_scheme1] | ![Scheme 2][hexoban_scheme2] |

    [hexoban_scheme1]:docs/images/hexoban_scheme1.png
    [hexoban_scheme2]:docs/images/hexoban_scheme2.png

    As long as encoding of single board is consistent, all methods handle any
    scheme transparently - parsing of board strings 'Just Works (TM)'

    Direction <-> character mapping:

    | LEFT | RIGHT | NORTH_WEST | SOUTH_WEST | NORTH_EAST | SOUTH_EAST |
    |:----:|:-----:|:----------:|:----------:|:----------:|:----------:|
    | l, L |  r, R |    u, U    |    d, D    |    n, N    |    s, S    |
    """
    HEXOBAN = 2

    """
    Board space is laid out on alternating squares and octagons with
    origin of coordinate system being octagon. Tessellation allows all
    8 directions of movement from Direction and depending on current
    pusher position some of these directions do not result in successful
    move.

    Direction <-> character mapping:

    |  UP  | NORTH_EAST | RIGHT | SOUTH_EAST | DOWN | SOUTH_WEST | LEFT | NORTH_WEST |
    |:----:|:----------:|:-----:|:----------:|:----:|:----------:|:----:|:----------:|
    | u, U |    n, N    |  r, R |    e, E    | d, D |    s, S    | l, L |    w, W    |
    """
    OCTOBAN = 3

    def to_s(self):
        if self == type(self).SOKOBAN:
            return "Sokoban"
        elif self == type(self).HEXOBAN:
            return "Hexoban"
        elif self == type(self).TRIOBAN:
            return "Trioban"
        elif self == type(self).OCTOBAN:
            return "Octoban"
        else:
            raise UnknownTessellationError(self)

    @classmethod
    def factory(cls, description):
        if isinstance(description, str):
            description = description.strip().lower()

        if (description == "sokoban" or
                description == "" or
                description == cls.SOKOBAN):
            return cls.SOKOBAN
        elif description == 'trioban' or description == cls.TRIOBAN:
            return cls.TRIOBAN
        elif description == 'hexoban' or description == cls.HEXOBAN:
            return cls.HEXOBAN
        elif description == 'octoban' or description == cls.OCTOBAN:
            return cls.OCTOBAN
        else:
            raise UnknownTessellationError(description)


class Tessellated(object):
    """
    Mixin that marks class depending on Tessellation specifics. This means that
    class will have to be initialized with Variant and it will use one of
    Tessellation subclass instances.
    """

    def __init__(self, variant):
        """
        variant - either case insensitive  string naming tessellation
        (ie. "hexoban") or one of Variant members
        """
        assert variant in Variant
        self._variant = variant
        self._tessellation_instance = Tessellation.factory(variant)

    @property
    def variant(self):
        return self._variant

    @property
    def tessellation(self):
        return self._tessellation_instance


class Tessellation(ABC):
    """
    Base class for all variant tessellation implementations.
    """

    _TESSELLATION_REGISTER = None

    @classmethod
    def _init_register(cls):
        if cls._TESSELLATION_REGISTER is None:
            from ..variant import (
                SokobanTessellation, HexobanTessellation, TriobanTessellation,
                OctobanTessellation
            )

            cls._TESSELLATION_REGISTER = {
                Variant.SOKOBAN: SokobanTessellation(),
                Variant.TRIOBAN: TriobanTessellation(),
                Variant.HEXOBAN: HexobanTessellation(),
                Variant.OCTOBAN: OctobanTessellation(),
            }

    @classmethod
    def factory(cls, variant):
        cls._init_register()

        if isinstance(variant, str):
            variant = Variant.factory(variant)

        retv = cls._TESSELLATION_REGISTER.get(variant, None)
        if not retv:
            raise UnknownTessellationError(variant)
        return retv

    @property
    @abstractmethod
    def legal_directions(self):
        """
        Directions generally accepted by Tessellation.
        """
        pass

    @abstractmethod
    def neighbor_position(self, position, direction, board_width, board_height):
        """
        Calculates neighbor position in given direction and verifies calculated
        position.

        If resulting position is off-board returns None

        Raises IllegalDirection in case direction is not one of
        self.legal_directions

        Position is always expressed as int index of board graph vertice. To
        convert 2D coordinates into vertice index, use index_1d method
        """
        pass

    @property
    @abstractmethod
    def _char_to_atomic_move_dict(self):
        """
        Dict mapping string to AtomicMove parameters
        """
        pass

    @property
    @abstractmethod
    def graph_type(self):
        """
        Graph class usable in given tessellation.
        """
        pass

    @property
    @abstractmethod
    def board_resizer_type(self):
        """
        VariantBoardResizer subclass
        """
        pass

    def char_to_atomic_move(self, chr):
        """
        Converts string to AtomicMove instance or raises exception if conversion
        not possible.
        """
        from ..io import AtomicMoveCharacters
        from ..game import AtomicMove

        if isinstance(chr, AtomicMoveCharacters):
            chr = chr.value

        direction, box_moved = self._char_to_atomic_move_dict.get(
            chr, (None, None)
        )

        if direction is None:
            raise IllegalDirectionError(chr)

        return AtomicMove(direction=direction, box_moved=box_moved)

    @property
    @abstractmethod
    def _atomic_move_to_char_dict(self):
        """
        Dict mapping AtomicMove parameters to string representation.
        """
        pass

    def atomic_move_to_char(self, atomic_move):
        """
        Converts AtomicMove to string or raises exception if conversion
        not possible.
        """
        chr = self._atomic_move_to_char_dict.get(
            (atomic_move.direction, atomic_move.is_push_or_pull),
            None
        )

        if chr is None:
            raise IllegalDirectionError(atomic_move)

        return chr

    def cell_orientation(self, position, board_width, board_height):
        """
        Calculates board cell orientation for given position.
        """
        return CellOrientation.DEFAULT


def index_1d(x, y, board_width):
    """
    Converts 2D coordinate to board position index.
    """
    return y * board_width + x

def X(index, board_width):
    return 0 if board_width == 0 else index % board_width

def Y(index, board_width):
    return 0 if board_width == 0 else int(index / board_width)

def ROW(index, board_width):
    return Y(index, board_width)

def COLUMN(index, board_width):
    return X(index, board_width)

def on_board_2D(x, y, board_width, board_height):
    return x >= 0 and y >= 0 and x < board_width and y < board_height

def on_board_1D(index, board_width, board_height):
    return index is not None and index >= 0 and on_board_2D(
        X(index, board_width),
        Y(index, board_width),
        board_width, board_height
    )
