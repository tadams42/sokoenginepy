from abc import ABC, abstractmethod

from .cell_orientation import CellOrientation
from .direction import UnknownDirectionError


class TessellationBase(ABC):
    """Base class for all tessellation implementations."""

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

        Position is always expressed as int index of board graph vertex. To
        convert 2D coordinates into vertex index, use :func:`.index_1d` method
        """
        pass

    @property
    @abstractmethod
    def _char_to_atomic_move_dict(self):
        """Dict mapping string to :class:`.AtomicMove` parameters,"""
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
        from .. import snapshot
        if isinstance(input_chr, snapshot.AtomicMove.Characters):
            input_chr = input_chr.value

        direction, box_moved = self._char_to_atomic_move_dict.get(
            input_chr, (None, None)
        )

        if direction is None:
            raise UnknownDirectionError(input_chr)

        return snapshot.AtomicMove(direction=direction, box_moved=box_moved)

    @property
    @abstractmethod
    def _atomic_move_to_char_dict(self):
        """Dict mapping :class:`.AtomicMove` parameters to string representation."""
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
            CellOrientation: cell orientation for given ``position``
        """
        return CellOrientation.DEFAULT

    def __eq__(self, rv):
        return self.__class__.__name__ == rv.__class__.__name__

    def __ne__(self, other):
        return not self == other