from __future__ import annotations

from typing import Final, Mapping, Tuple

from .tile_shape import TileShape
from .characters import Characters
from .config import Config
from .direction import Direction
from .graph_type import GraphType
from .tessellation import index_1d, index_column, index_row, is_on_board_2d
from .tessellation_impl import PusherStepData, TessellationImpl


class TriobanTessellation(TessellationImpl):
    _LEGAL_DIRECTIONS: Final[Tuple[Direction, ...]] = (
        Direction.LEFT,
        Direction.RIGHT,
        Direction.NORTH_EAST,
        Direction.NORTH_WEST,
        Direction.SOUTH_EAST,
        Direction.SOUTH_WEST,
    )

    _CHR_TO_PUSHER_STEP: Final[Mapping[str, PusherStepData]] = {
        Characters.l: PusherStepData(Direction.LEFT, False),
        Characters.L: PusherStepData(Direction.LEFT, True),
        Characters.r: PusherStepData(Direction.RIGHT, False),
        Characters.R: PusherStepData(Direction.RIGHT, True),
        Characters.n: PusherStepData(Direction.NORTH_EAST, False),
        Characters.N: PusherStepData(Direction.NORTH_EAST, True),
        Characters.u: PusherStepData(Direction.NORTH_WEST, False),
        Characters.U: PusherStepData(Direction.NORTH_WEST, True),
        Characters.d: PusherStepData(Direction.SOUTH_EAST, False),
        Characters.D: PusherStepData(Direction.SOUTH_EAST, True),
        Characters.s: PusherStepData(Direction.SOUTH_WEST, False),
        Characters.S: PusherStepData(Direction.SOUTH_WEST, True),
    }

    _PUSHER_STEP_TO_CHR: Final[Mapping[PusherStepData, str]] = {
        v: k for k, v in _CHR_TO_PUSHER_STEP.items()
    }

    @property
    def graph_type(self) -> GraphType:
        return GraphType.DIRECTED_MULTI

    def neighbor_position(
        self, position: int, direction: Direction, board_width: int, board_height: int
    ) -> int:
        triangle_points_down = (
            self.tile_shape(position, board_width, board_height)
            == TileShape.TRIANGLE_DOWN
        )
        row = index_row(position, board_width)
        column = index_column(position, board_width)

        dx, dy = 0, 0
        if direction == Direction.LEFT:
            dy = 0
            dx = -1
        elif direction == Direction.RIGHT:
            dy = 0
            dx = 1
        elif direction == Direction.NORTH_EAST:
            if triangle_points_down:
                dy = -1
                dx = 0
            else:
                dy = 0
                dx = 1
        elif direction == Direction.NORTH_WEST:
            if triangle_points_down:
                dy = -1
                dx = 0
            else:
                dy = 0
                dx = -1
        elif direction == Direction.SOUTH_EAST:
            if triangle_points_down:
                dy = 0
                dx = 1
            else:
                dy = 1
                dx = 0
        elif direction == Direction.SOUTH_WEST:
            if triangle_points_down:
                dy = 0
                dx = -1
            else:
                dy = 1
                dx = 0
        else:
            raise ValueError(
                f"Unsupported direction {direction} for {self.__class__.__name__}"
            )

        row += dy
        column += dx

        if is_on_board_2d(column, row, board_width, board_height):
            return index_1d(column, row, board_width)

        return Config.NO_POS

    def tile_shape(
        self, position: int, board_width: int, board_height: int
    ) -> TileShape:
        if position < 0:
            raise IndexError(f"Position {position} is invalid value!")

        if board_width < 0:
            raise ValueError(f"Board width {board_width} is invalid value!")

        if board_height < 0:
            raise ValueError(f"Board height {board_height} is invalid value!")

        row = index_row(position, board_width)
        column = index_column(position, board_width)
        return (
            TileShape.TRIANGLE_DOWN
            if (column + (row % 2)) % 2 == 0
            else TileShape.DEFAULT
        )
