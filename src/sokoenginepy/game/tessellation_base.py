from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import ClassVar, Mapping, Optional, Tuple

from .pusher_step import PusherStep
from .cell_orientation import CellOrientation
from .direction import Direction
from .graph_type import GraphType


class TessellationBase(metaclass=ABCMeta):
    """
    Base class for all tessellation implementations.
    """

    _LEGAL_DIRECTIONS: ClassVar[Tuple[Direction, ...]] = tuple()
    _CHR_TO_PUSHER_STEP: ClassVar[Mapping[str, Tuple[Direction, bool]]] = {}
    _PUSHER_STEP_TO_CHR: ClassVar[Mapping[Tuple[Direction, bool], str]] = {}

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

    def pusher_step_to_char(self, pusher_step: PusherStep) -> str:
        """
        Converts :class:`.PusherStep` to movement character.

        Raises:
            :exc:`ValueError`: conversion not possible in context of this tessellation
        """
        try:
            retv = self._PUSHER_STEP_TO_CHR[
                (pusher_step.direction, pusher_step.is_push_or_pull)
            ]
        except KeyError:
            raise ValueError(pusher_step)

        return retv

    def char_to_pusher_step(self, input_chr: str) -> PusherStep:
        """
        Converts movement character to :class:`.PusherStep`.

        Raises:
            :exc:`ValueError`: conversion is not possible in context of this
                               tessellation
        """
        try:
            direction, box_moved = self._CHR_TO_PUSHER_STEP[input_chr]
        except KeyError:
            raise ValueError(input_chr)

        return PusherStep(direction=direction, box_moved=box_moved)

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
