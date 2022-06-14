from __future__ import annotations

import enum
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, ClassVar, Mapping, Optional, Tuple, Union

from ..io import CellOrientation
from .config import Direction, GraphType
from .pusher_step import PusherStep

if TYPE_CHECKING:
    from .hexoban_tessellation import HexobanTessellation
    from .octoban_tessellation import OctobanTessellation
    from .sokoban_tessellation import SokobanTessellation
    from .trioban_tessellation import TriobanTessellation


class Tessellation(enum.Enum):
    SOKOBAN = 0
    HEXOBAN = 1
    TRIOBAN = 2
    OCTOBAN = 3


def index_1d(x: int, y: int, board_width: int) -> int:
    """Converts 2D coordinate to board position index."""
    return y * board_width + x


def X(index: int, board_width: int) -> int:
    """x component of board position index."""
    return 0 if board_width == 0 else index % board_width


def Y(index: int, board_width: int) -> int:
    """y component of board position index."""
    return 0 if board_width == 0 else int(index / board_width)


def ROW(index: int, board_width: int) -> int:
    """x component of board position index."""
    return Y(index, board_width)


def COLUMN(index: int, board_width: int) -> int:
    """y component of board position index."""
    return X(index, board_width)


def is_on_board_2d(x: int, y: int, board_width: int, board_height: int) -> bool:
    return x >= 0 and y >= 0 and x < board_width and y < board_height


def is_on_board_1d(index: Optional[int], board_width: int, board_height: int) -> bool:
    return (
        index is not None
        and index >= 0
        and is_on_board_2d(
            X(index, board_width), Y(index, board_width), board_width, board_height
        )
    )


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
