from __future__ import annotations

from typing import Dict, Final, List, Optional, Tuple

from .characters import Characters
from .config import Config
from .direction import Direction
from .tessellation import index_1d, index_column, index_row, is_on_board_2d
from .tessellation_impl import PusherStepData, TessellationImpl


class SokobanTessellation(TessellationImpl):
    _LEGAL_DIRECTIONS: Final[Tuple[Direction, ...]] = (
        Direction.LEFT,
        Direction.RIGHT,
        Direction.UP,
        Direction.DOWN,
    )

    _CHR_TO_PUSHER_STEP: Final[Dict[str, PusherStepData]] = {
        Characters.l: PusherStepData(Direction.LEFT, False),
        Characters.L: PusherStepData(Direction.LEFT, True),
        Characters.r: PusherStepData(Direction.RIGHT, False),
        Characters.R: PusherStepData(Direction.RIGHT, True),
        Characters.u: PusherStepData(Direction.UP, False),
        Characters.U: PusherStepData(Direction.UP, True),
        Characters.d: PusherStepData(Direction.DOWN, False),
        Characters.D: PusherStepData(Direction.DOWN, True),
    }

    _PUSHER_STEP_TO_CHR: Final[Dict[PusherStepData, str]] = {
        v: k for k, v in _CHR_TO_PUSHER_STEP.items()
    }

    _NEIGHBOR_SHIFT: Final[List[Tuple[Optional[int], Optional[int]]]] = [
        (-1, 0),  # UP
        (None, None),
        (0, 1),  # RIGHT
        (None, None),
        (1, 0),  # DOWN
        (None, None),
        (0, -1),  # LEFT
        (None, None),
    ]

    def neighbor_position(
        self, position: int, direction: Direction, board_width: int, board_height: int
    ) -> int:
        if position < 0:
            raise IndexError(f"Position {position} is invalid value!")

        if board_width < 0:
            raise ValueError(f"Board width {board_width} is invalid value!")

        if board_height < 0:
            raise ValueError(f"Board height {board_height} is invalid value!")

        row = index_row(position, board_width)
        column = index_column(position, board_width)
        row_shift, column_shift = self._NEIGHBOR_SHIFT[direction.value]

        if row_shift is None or column_shift is None:
            raise ValueError(
                f"Unsupported direction {direction} for {self.__class__.__name__}"
            )

        row += row_shift
        column += column_shift

        if is_on_board_2d(column, row, board_width, board_height):
            return index_1d(column, row, board_width)

        return Config.NO_POS
