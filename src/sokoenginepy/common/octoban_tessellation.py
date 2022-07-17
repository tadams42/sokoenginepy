from __future__ import annotations

from typing import Dict, Final, Tuple

from .cell_orientation import CellOrientation
from .characters import Characters
from .config import Config
from .direction import Direction
from .tessellation import index_1d, index_column, index_row, is_on_board_2d
from .tessellation_impl import PusherStepData, TessellationImpl


class OctobanTessellation(TessellationImpl):
    _LEGAL_DIRECTIONS: Final[Tuple[Direction, ...]] = (
        Direction.LEFT,
        Direction.RIGHT,
        Direction.UP,
        Direction.DOWN,
        Direction.NORTH_EAST,
        Direction.NORTH_WEST,
        Direction.SOUTH_EAST,
        Direction.SOUTH_WEST,
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
        Characters.w: PusherStepData(Direction.NORTH_WEST, False),
        Characters.W: PusherStepData(Direction.NORTH_WEST, True),
        Characters.e: PusherStepData(Direction.SOUTH_EAST, False),
        Characters.E: PusherStepData(Direction.SOUTH_EAST, True),
        Characters.n: PusherStepData(Direction.NORTH_EAST, False),
        Characters.N: PusherStepData(Direction.NORTH_EAST, True),
        Characters.s: PusherStepData(Direction.SOUTH_WEST, False),
        Characters.S: PusherStepData(Direction.SOUTH_WEST, True),
    }

    _PUSHER_STEP_TO_CHR: Final[Dict[PusherStepData, str]] = {
        v: k for k, v in _CHR_TO_PUSHER_STEP.items()
    }

    _NEIGHBOR_SHIFT: Final[Dict[Direction, Tuple[int, int]]] = {
        Direction.LEFT: (0, -1),
        Direction.RIGHT: (0, 1),
        Direction.UP: (-1, 0),
        Direction.DOWN: (1, 0),
        Direction.NORTH_WEST: (-1, -1),
        Direction.NORTH_EAST: (-1, 1),
        Direction.SOUTH_WEST: (1, -1),
        Direction.SOUTH_EAST: (1, 1),
    }

    def neighbor_position(
        self, position: int, direction: Direction, board_width: int, board_height: int
    ) -> int:
        if self.cell_orientation(
            position, board_width, board_height
        ) != CellOrientation.OCTAGON and direction in (
            Direction.NORTH_EAST,
            Direction.NORTH_WEST,
            Direction.SOUTH_EAST,
            Direction.SOUTH_WEST,
        ):
            return Config.NO_POS

        row = index_row(position, board_width)
        column = index_column(position, board_width)
        row_shift, column_shift = self._NEIGHBOR_SHIFT.get(direction, (None, None))

        if row_shift is None or column_shift is None:
            raise ValueError(
                f"Unsupported direction {direction} for {self.__class__.__name__}"
            )

        row += row_shift
        column += column_shift

        if is_on_board_2d(column, row, board_width, board_height):
            return index_1d(column, row, board_width)

        return Config.NO_POS

    def cell_orientation(
        self, position: int, board_width: int, board_height: int
    ) -> CellOrientation:
        if position < 0:
            raise IndexError(f"Position {position} is invalid value!")

        if board_width < 0:
            raise ValueError(f"Board width {board_width} is invalid value!")

        if board_height < 0:
            raise ValueError(f"Board height {board_height} is invalid value!")

        row = index_row(position, board_width)
        column = index_column(position, board_width)
        return (
            CellOrientation.OCTAGON
            if (column + (row % 2)) % 2 == 0
            else CellOrientation.DEFAULT
        )
