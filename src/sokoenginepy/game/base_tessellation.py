from __future__ import annotations

import enum
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, ClassVar, Mapping, Tuple, Union

from .config import Config, Direction, GraphType
from .pusher_step import PusherStep

if TYPE_CHECKING:
    from ..io import CellOrientation
    from .hexoban_tessellation import HexobanTessellation
    from .octoban_tessellation import OctobanTessellation
    from .sokoban_tessellation import SokobanTessellation
    from .trioban_tessellation import TriobanTessellation


class Tessellation(enum.Enum):
    """Supported game tessellations."""

    #: Tessellation for Sokoban game variant.
    #:
    #: Board is laid out on squares.
    #:
    #: Direction <-> character mapping:
    #:
    #: ====  =====  ====  ====
    #: LEFT  RIGHT  UP    DOWN
    #: ====  =====  ====  ====
    #: l, L  r, R   u, U  d, D
    #: ====  =====  ====  ====
    SOKOBAN = 0

    #: Tessellation for Hexoban game variant.
    #:
    #: Board space is laid out on vertical hexagons with following coordinate system:
    #:
    #: .. image:: /images/hexoban_coordinates.png
    #:    :alt: Hexoban coordinates
    #:
    #: Textual representation uses two characters for each hexagon. This allows different
    #: encoding schemes.
    #:
    #: .. |img1| image:: /images/hexoban_scheme1.png
    #: .. |img2| image:: /images/hexoban_scheme2.png
    #:
    #: +----------+----------+
    #: | Scheme 1 | Scheme 2 |
    #: +==========+==========+
    #: |  |img1|  |  |img2|  |
    #: +----------+----------+
    #:
    #: As long as encoding of single board is consistent, all methods handle any scheme
    #: transparently - parsing of board strings 'Just Works (TM)'
    #:
    #: Direction <-> character mapping:
    #:
    #: ====  =====  ==========  ==========  ==========  ==========
    #: LEFT  RIGHT  NORTH_WEST  SOUTH_WEST  NORTH_EAST  SOUTH_EAST
    #: ====  =====  ==========  ==========  ==========  ==========
    #: l, L  r, R   u, U        d, D        n, N        s, S
    #: ====  =====  ==========  ==========  ==========  ==========
    HEXOBAN = 1

    #: Tessellation for Trioban game variant.
    #:
    #: Board is laid out on alternating triangles with origin triangle pointing down.
    #:
    #: Direction <-> character mapping:
    #:
    #: ====  =====  ==========  ==========  ==========  ==========
    #: LEFT  RIGHT  NORTH_EAST  NORTH_WEST  SOUTH_EAST  SOUTH_WEST
    #: ====  =====  ==========  ==========  ==========  ==========
    #: l, L  r, R   n, N        u, U        d, D        s, S
    #: ====  =====  ==========  ==========  ==========  ==========
    #:
    #: Depending on pusher position, not all move directions are allowed on all board
    #: positions:
    #:
    #: .. image:: /images/trioban_am.png
    #:     :alt: Trioban movement
    TRIOBAN = 2

    #: Tessellation for Octoban game variant.
    #:
    #: Board space is laid out on alternating squares and octagons with origin of
    #: coordinate system being octagon. Tessellation allows all 8 directions of movement
    #: from Direction and depending on current pusher position some of these directions do
    #: not result in successful move.
    #:
    #: Direction <-> character mapping:
    #:
    #: ====  ==========  =====  ==========  ====  ==========  ====  ==========
    #: UP    NORTH_EAST  RIGHT  SOUTH_EAST  DOWN  SOUTH_WEST  LEFT  NORTH_WEST
    #: ====  ==========  =====  ==========  ====  ==========  ====  ==========
    #: u, U  n, N        r, R   e, E        d, D  s, S        l, L  w, W
    #: ====  ==========  =====  ==========  ====  ==========  ====  ==========
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
            raise ValueError(
                f"Illegal PusherStep direction {pusher_step.direction} in "
                f"{self.__class__.__name__}!"
            )

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
            raise ValueError(
                f"Illegal PusherStep character '{input_chr}' in "
                f"{self.__class__.__name__}!"
            )

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
        from ..io import CellOrientation

        if position < 0:
            raise IndexError(f"Position {position} is invalid value!")

        if board_width < 0:
            raise ValueError(f"Board width {board_width} is invalid value!")

        if board_height < 0:
            raise ValueError(f"Board height {board_height} is invalid value!")

        return CellOrientation.DEFAULT
