from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections import namedtuple
from typing import TYPE_CHECKING, ClassVar, Dict, Tuple, Union

from .cell_orientation import CellOrientation
from .config import Config
from .direction import Direction
from .graph_type import GraphType
from .tessellation import Tessellation

if TYPE_CHECKING:
    from ..game import PusherStep
    from .hexoban_tessellation import HexobanTessellation
    from .octoban_tessellation import OctobanTessellation
    from .sokoban_tessellation import SokobanTessellation
    from .trioban_tessellation import TriobanTessellation

PusherStepData = namedtuple("PusherStepData", ["direction", "box_moved"])


class TessellationImpl(metaclass=ABCMeta):
    """Base class for all tessellation implementations."""

    _LEGAL_DIRECTIONS: ClassVar[Tuple[Direction, ...]]
    _CHR_TO_PUSHER_STEP: ClassVar[Dict[str, PusherStepData]]
    _PUSHER_STEP_TO_CHR: ClassVar[Dict[PusherStepData, str]]
    _INSTANCES: ClassVar[Dict[Tessellation, TessellationImpl]] = {}

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

        if not cls._INSTANCES:
            cls._INSTANCES = {
                Tessellation.SOKOBAN: SokobanTessellation(),
                Tessellation.HEXOBAN: HexobanTessellation(),
                Tessellation.TRIOBAN: TriobanTessellation(),
                Tessellation.OCTOBAN: OctobanTessellation(),
            }

        return cls._INSTANCES[tessellation]

    @property
    def legal_directions(self) -> Tuple[Direction, ...]:
        """Directions that are valid in context of this tessellation."""
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
        """Type of board graph used in context of this tessellation."""
        return GraphType.DIRECTED

    def pusher_step_to_char(self, pusher_step: PusherStep) -> str:
        """
        Converts PusherStepData to movement character.

        Raises:
            :exc:`ValueError`: conversion not possible in context of this tessellation
        """
        try:
            retv = self._PUSHER_STEP_TO_CHR[
                PusherStepData(pusher_step.direction, pusher_step.is_push_or_pull)
            ]
        except KeyError:
            raise ValueError(
                f"Illegal PusherStepData direction {pusher_step.direction} in "
                f"{self.__class__.__name__}!"
            )

        return retv

    def char_to_pusher_step(self, input_chr: str) -> PusherStep:
        """
        Converts movement character to :class:`.PusherStepData`.

        Raises:
            :exc:`ValueError`: conversion is not possible in context of this
                               tessellation
        """
        from ..game import PusherStep

        try:
            direction, box_moved = self._CHR_TO_PUSHER_STEP[input_chr]
        except KeyError:
            raise ValueError(
                f"Illegal PusherStepData character '{input_chr}' in "
                f"{self.__class__.__name__}!"
            )

        return PusherStep(
            direction=direction,
            moved_box_id=Config.NO_ID if not box_moved else Config.DEFAULT_ID,
        )

    def cell_orientation(
        self, position: int, board_width: int, board_height: int
    ) -> CellOrientation:
        """Calculates board cell orientation for given coordinate."""
        if position < 0:
            raise IndexError(f"Position {position} is invalid value!")

        if board_width < 0:
            raise ValueError(f"Board width {board_width} is invalid value!")

        if board_height < 0:
            raise ValueError(f"Board height {board_height} is invalid value!")

        return CellOrientation.DEFAULT
