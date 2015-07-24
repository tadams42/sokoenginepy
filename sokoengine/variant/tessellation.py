from enum import Enum
from abc import ABC, abstractmethod
from ..core.exceptions import UnknownTessellationError, IllegalDirectionError


class Direction(Enum):
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


class TessellationType(Enum):
    """
    Enumerates implemented tessellation types. All classes that are tessellation
    dependant have attribute tessellation_type whose value is one of these.
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
    Board is laid out on alternating triangles with origin triangle poiting up.
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

    @classmethod
    def factory(cls, description):
        tmp = description.strip().lower() if description else ""
        if tmp == "sokoban" or tmp == "":
            return cls.SOKOBAN
        elif tmp == 'trioban':
            return cls.TRIOBAN
        elif tmp == 'hexoban':
            return cls.HEXOBAN
        elif tmp == 'octoban':
            return cls.OCTOBAN
        else:
            raise UnknownTessellationError(description)


class Tessellated(object):
    """
    Mixin that marks class depending on Tessellation specifics. This means that
    class will have to be initialized with TessellationType and it will
    (internally) use one of Tessellation subclass instances.
    """

    def __init__(self, tessellation_type):
        """
        tessellation_type - either case insensitive  string naming tessellation
        (ie. "hexoban") or one of TessellationType members
        """
        assert tessellation_type is not None, "Tessellation type must be specified!"
        self._tessellation_type = tessellation_type
        self._tessellation_instance = Tessellation.factory(tessellation_type)

    @property
    def tessellation_type(self):
        return self._tessellation_type

    @property
    def _tessellation(self):
        return self._tessellation_instance


class Tessellation(ABC):

    _TESSELATION_REGISTER = None

    @classmethod
    def factory(cls, tessellation_type):
        if cls._TESSELATION_REGISTER is None:
            from .sokoban_tessellation import SokobanTessellation
            from .hexoban_tessellation import HexobanTessellation
            from .trioban_tessellation import TriobanTessellation
            from .octoban_tessellation import OctobanTessellation

            cls._TESSELATION_REGISTER = {
                TessellationType.SOKOBAN: SokobanTessellation(),
                TessellationType.TRIOBAN: TriobanTessellation(),
                TessellationType.HEXOBAN: HexobanTessellation(),
                TessellationType.OCTOBAN: OctobanTessellation(),
            }

        if isinstance(tessellation_type, str):
            tessellation_type = TessellationType.factory(tessellation_type)

        retv = cls._TESSELATION_REGISTER.get(tessellation_type, None)
        if not retv:
            raise UnknownTessellationError(tessellation_type)
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

        If position would lead off-board, returns None

        Raises IllegalDirection in case direction is not one of
        self.legal_directions

        Position is always expressed as int index of board graph vertice. To
        convert 2D coordinates into vertice index, use INDEX method
        """
        pass

    @property
    @abstractmethod
    def char_to_atomic_move_dict(self):
        pass

    @property
    @abstractmethod
    def graph_type(self):
        pass

    def char_to_atomic_move(self, chr):
        from ..io.text_utils import AtomicMoveCharacters
        from ..core.atomic_move import AtomicMove

        if isinstance(chr, AtomicMoveCharacters):
            chr = chr.value

        direction, box_moved = self.char_to_atomic_move_dict.get(
            chr, (None, None)
        )

        if direction is None:
            raise IllegalDirectionError(chr)

        return AtomicMove(direction=direction, box_moved=box_moved)

    @property
    @abstractmethod
    def atomic_move_to_char_dict(self):
        pass

    def atomic_move_to_char(self, atomic_move):
        chr = self.atomic_move_to_char_dict.get(
            (atomic_move.direction, atomic_move.is_push_or_pull),
            None
        )

        if chr is None:
            raise IllegalDirectionError(atomic_move)

        return chr

    def cell_orientation(self, position, board_width, board_height):
        return CellOrientation.DEFAULT


def INDEX(x, y, board_width):
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
