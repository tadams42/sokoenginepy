from __future__ import annotations

import enum
from abc import ABCMeta, abstractmethod
from multiprocessing.sharedctypes import Value
from turtle import width
from typing import TYPE_CHECKING, ClassVar, Mapping, Tuple, Union

from ..io import CellOrientation
from .config import Config, Direction, GraphType
from .pusher_step import PusherStep

if TYPE_CHECKING:
    from .hexoban_tessellation import HexobanTessellation
    from .octoban_tessellation import OctobanTessellation
    from .sokoban_tessellation import SokobanTessellation
    from .trioban_tessellation import TriobanTessellation


class Tessellation(enum.Enum):
    """Supported game tessellations."""

    #: See Also:
    #      :class:`.SokobanTessellation`
    SOKOBAN = 0

    #: See Also:
    #      :class:`.HexobanTessellation`
    HEXOBAN = 1

    #: See Also:
    #      :class:`.TriobanTessellation`
    TRIOBAN = 2

    #: See Also:
    #      :class:`.OctobanTessellation`
    OCTOBAN = 3


class BaseTessellation(metaclass=ABCMeta):
    """
    Base class for all tessellation implementations.
    """

    _LEGAL_DIRECTIONS: ClassVar[Tuple[Direction, ...]] = tuple()
    _CHR_TO_PUSHER_STEP: ClassVar[Mapping[str, Tuple[Direction, bool]]] = {}
    _PUSHER_STEP_TO_CHR: ClassVar[Mapping[Tuple[Direction, bool], str]] = {}

    @classmethod
    def instance(
        cls, tessellation: Tessellation
    ) -> Union[
        TriobanTessellation,
        OctobanTessellation,
        HexobanTessellation,
        SokobanTessellation,
    ]:
        from .hexoban_tessellation import HexobanTessellation
        from .octoban_tessellation import OctobanTessellation
        from .sokoban_tessellation import SokobanTessellation
        from .trioban_tessellation import TriobanTessellation

        if tessellation == Tessellation.SOKOBAN:
            return SokobanTessellation()
        elif tessellation == Tessellation.HEXOBAN:
            return HexobanTessellation()
        elif tessellation == Tessellation.TRIOBAN:
            return TriobanTessellation()
        elif tessellation == Tessellation.OCTOBAN:
            return OctobanTessellation()
        else:
            raise ValueError("Unknown tessellation!")

    @property
    def legal_directions(self) -> Tuple[Direction, ...]:
        """
        Directions that are valid in context of this tessellation.
        """
        return self._LEGAL_DIRECTIONS

    @abstractmethod
    def neighbor_position(
        self, position: int, direction: Direction, board_width: int, board_height: int
    ) -> int:
        """
        Calculates neighbor position in given direction.

        Position is always expressed as 1D index of board graph vertex.

        To convert 2D coordinates into vertex index, use :func:`.index_1d` method.

        To convert 1D vertex index into 2D coordinates, use combinations of
        :func:`.index_row` and :func:`.index_column` functions.

        Returns:
            int: New position or `.Config.NO_POS` when new position would be off-board.

        Raises:
            :exc:`ValueError`: ``direction`` is not one of :attr:`legal_directions` or
                ``board_width`` is invalid value or ``board_height`` is invalid value.
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

        return PusherStep(
            direction=direction,
            moved_box_id=Config.NO_ID if not box_moved else Config.DEFAULT_ID,
        )

    def cell_orientation(
        self, position: int, board_width: int, board_height: int
    ) -> CellOrientation:
        """
        Calculates board cell orientation for given coordinate.
        """
        if position < 0:
            raise IndexError(f"Position {position} is invalid value!")

        if board_width < 0:
            raise ValueError(f"Board width {board_width} is invalid value!")

        if board_height < 0:
            raise ValueError(f"Board height {board_height} is invalid value!")

        return CellOrientation.DEFAULT
