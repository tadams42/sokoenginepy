from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import ClassVar, Mapping, Optional, Tuple

from .atomic_move import AtomicMove
from .cell_orientation import CellOrientation
from .direction import Direction
from .graph_type import GraphType


class TessellationBase(metaclass=ABCMeta):
    """
    Base class for all tessellation implementations.
    """

    _LEGAL_DIRECTIONS: ClassVar[Tuple[Direction, ...]] = tuple()
    _CHR_TO_ATOMIC_MOVE: ClassVar[Mapping[str, Tuple[Direction, bool]]] = {}
    _ATOMIC_MOVE_TO_CHR: ClassVar[Mapping[Tuple[Direction, bool], str]] = {}

    @property
    def legal_directions(self) -> Tuple[Direction, ...]:
        """
        Directions that are valid in context of this tessellation.
        """
        return self._LEGAL_DIRECTIONS

    @abstractmethod
    def neighbor_position(
        self, position: int, direction: Direction, board_width: int, board_height: int
    ) -> Optional[int]:
        """
        Calculates neighbor position in given direction.

        Position is always expressed as 1D index of board graph vertex.

        To convert 2D coordinates into vertex index, use :func:`.index_1d` method.

        To convert 1D vertex index into 2D coordinates, use combinations of :func:`.ROW`
        and :func:`.COLUMN` functions.

        Returns:
            int: New position or `None` when new position would be off-board.

        Raises:
            :exc:`ValueError`: ``direction`` is not one of :attr:`legal_directions`
        """
        pass

    @property
    def graph_type(self) -> GraphType:
        """
        Type of board graph used in context of this tessellation.
        """
        return GraphType.DIRECTED

    def atomic_move_to_char(self, atomic_move: AtomicMove) -> str:
        """
        Converts :class:`.AtomicMove` to movement character.

        Raises:
            :exc:`ValueError`: conversion not possible in context of this tessellation
        """
        try:
            retv = self._ATOMIC_MOVE_TO_CHR[
                (atomic_move.direction, atomic_move.is_push_or_pull)
            ]
        except KeyError:
            raise ValueError(atomic_move)

        return retv

    def char_to_atomic_move(self, input_chr: str) -> AtomicMove:
        """
        Converts movement character to :class:`.AtomicMove`.

        Raises:
            :exc:`ValueError`: conversion is not possible in context of this
                               tessellation
        """
        try:
            direction, box_moved = self._CHR_TO_ATOMIC_MOVE[input_chr]
        except KeyError:
            raise ValueError(input_chr)

        return AtomicMove(direction=direction, box_moved=box_moved)

    def cell_orientation(
        self, position: int, board_width: int, board_height: int
    ) -> CellOrientation:
        """
        Calculates board cell orientation for given coordinate.
        """
        return CellOrientation.DEFAULT

    def __eq__(self, rv):
        return self.__class__.__name__ == rv.__class__.__name__

    def __ne__(self, other):
        return not self == other
