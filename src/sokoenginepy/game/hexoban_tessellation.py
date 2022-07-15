from __future__ import annotations

from typing import Dict, Final, Tuple

from ..io import Snapshot
from .base_tessellation import BaseTessellation
from .config import Config, Direction
from .coordinate_helpers import index_1d, index_column, index_row, is_on_board_2d
from .utilities import inverted


class HexobanTessellation(BaseTessellation):
    _LEGAL_DIRECTIONS: Final[Tuple[Direction, ...]] = (
        Direction.LEFT,
        Direction.RIGHT,
        Direction.NORTH_EAST,
        Direction.NORTH_WEST,
        Direction.SOUTH_EAST,
        Direction.SOUTH_WEST,
    )

    _CHR_TO_PUSHER_STEP: Final[Dict[str, Tuple[Direction, bool]]] = {
        Snapshot.l: (Direction.LEFT, False),
        Snapshot.L: (Direction.LEFT, True),
        Snapshot.r: (Direction.RIGHT, False),
        Snapshot.R: (Direction.RIGHT, True),
        Snapshot.u: (Direction.NORTH_WEST, False),
        Snapshot.U: (Direction.NORTH_WEST, True),
        Snapshot.d: (Direction.SOUTH_EAST, False),
        Snapshot.D: (Direction.SOUTH_EAST, True),
        Snapshot.n: (Direction.NORTH_EAST, False),
        Snapshot.N: (Direction.NORTH_EAST, True),
        Snapshot.s: (Direction.SOUTH_WEST, False),
        Snapshot.S: (Direction.SOUTH_WEST, True),
    }

    _PUSHER_STEP_TO_CHR: Final[Dict[Tuple[Direction, bool], str]] = inverted(
        _CHR_TO_PUSHER_STEP
    )

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

        if direction == Direction.LEFT:
            column -= 1
        elif direction == Direction.RIGHT:
            column += 1
        elif direction == Direction.NORTH_EAST:
            column += row % 2
            row -= 1
        elif direction == Direction.NORTH_WEST:
            column -= (row + 1) % 2
            row -= 1
        elif direction == Direction.SOUTH_EAST:
            column += row % 2
            row += 1
        elif direction == Direction.SOUTH_WEST:
            column -= (row + 1) % 2
            row += 1
        else:
            raise ValueError(
                f"Unsupported direction {direction} for {self.__class__.__name__}"
            )

        if is_on_board_2d(column, row, board_width, board_height):
            return index_1d(column, row, board_width)

        return Config.NO_POS
