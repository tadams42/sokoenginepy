from enum import IntEnum
from abc import ABC, abstractmethod

from .atomic_move import AtomicMove
from .exceptions import UnknownTessellationError, IllegalDirectionError
from .variant import Variant


class CellOrientation(IntEnum):
    """
    Dynamic board cell property that depends on cell position in some
    tessellations. ie. in Trioban, coordinate origin is triangle pointig
    upwards. This means that orientation of all other triangles depends on
    their position. Methods that calculate orientation return one of these
    values.
    """
    DEFAULT = 0
    TRIANGLE_DOWN = 1
    OCTAGON = 2


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

    def char_to_atomic_move(self, input_chr):
        """
        Converts string to AtomicMove instance or raises exception if conversion
        not possible.
        """
        from ..io import AtomicMoveCharacters

        if isinstance(input_chr, AtomicMoveCharacters):
            input_chr = input_chr.value

        direction, box_moved = self._char_to_atomic_move_dict.get(
            input_chr, (None, None)
        )

        if direction is None:
            raise IllegalDirectionError(input_chr)

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
        retv = self._atomic_move_to_char_dict.get(
            (atomic_move.direction, atomic_move.is_push_or_pull), None
        )

        if retv is None:
            raise IllegalDirectionError(atomic_move)

        return retv

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


def on_board_2d(x, y, board_width, board_height):
    return x >= 0 and y >= 0 and x < board_width and y < board_height


def on_board_1d(index, board_width, board_height):
    return index is not None and index >= 0 and on_board_2d(
        X(index, board_width), Y(index, board_width), board_width, board_height
    )
