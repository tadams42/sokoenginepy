from abc import ABC, abstractmethod
from enum import IntEnum

from ..common import UnknownDirectionError


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
    """Base class for all variant tessellation implementations."""

    @property
    @abstractmethod
    def legal_directions(self):
        """Directions generally accepted by Tessellation.

        Returns:
            list: of :class:`.Direction`
        """
        pass

    @abstractmethod
    def neighbor_position(self, position, direction, board_width, board_height):
        """Calculates neighbor position in given direction and verifies calculated position.

        Returns:
            int: If resulting position is off-board returns None, otherwise position

        Raises:
            :exc:`.UnknownDirectionError`: in case direction is not one of self.legal_directions

        Position is always expressed as int index of board graph vertice. To
        convert 2D coordinates into vertice index, use :func:`index_1d` method
        """
        pass

    @property
    @abstractmethod
    def _char_to_atomic_move_dict(self):
        """Dict mapping string to AtomicMove parameters,"""
        pass

    @property
    @abstractmethod
    def graph_type(self):
        """Type of graph used in given tessellation."""
        pass

    def char_to_atomic_move(self, input_chr):
        """
        Converts string to :class:`.AtomicMove` instance or raises
        :exc:`.UnknownDirectionError` if conversion not possible.
        """
        from ..snapshot import AtomicMove, AtomicMoveCharacters

        if isinstance(input_chr, AtomicMoveCharacters):
            input_chr = input_chr.value

        direction, box_moved = self._char_to_atomic_move_dict.get(
            input_chr, (None, None)
        )

        if direction is None:
            raise UnknownDirectionError(input_chr)

        return AtomicMove(direction=direction, box_moved=box_moved)

    @property
    @abstractmethod
    def _atomic_move_to_char_dict(self):
        """Dict mapping AtomicMove parameters to string representation."""
        pass

    def atomic_move_to_char(self, atomic_move):
        """
        Converts :class:`.AtomicMove` to string or raises
        :exc:`.UnknownDirectionError` if conversion not possible.
        """
        retv = self._atomic_move_to_char_dict.get(
            (atomic_move.direction, atomic_move.is_push_or_pull), None
        )

        if retv is None:
            raise UnknownDirectionError(atomic_move)

        return retv

    def cell_orientation(self, position, board_width, board_height):
        """Calculates board cell orientation for given position.

        Returns:
            CellOrientation: cell orientation for given `position`
        """
        return CellOrientation.DEFAULT


def index_1d(x, y, board_width):
    """Converts 2D coordinate to board position index."""
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
