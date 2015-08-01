from ..core import (
    Tessellation, on_board_2D, on_board_1D, ROW, COLUMN, index_1d, Direction,
    IllegalDirectionError
)
from ..io import AtomicMoveCharacters
from .sokoban_board import SokobanBoardResizer
from .board_graph import GraphType


class SokobanTessellation(Tessellation):
    """
    Implements Tessellation for Sokoban variant.
    """

    _LEGAL_DIRECTIONS = (
        Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN
    )

    @property
    def legal_directions(self):
        return type(self)._LEGAL_DIRECTIONS

    @property
    def graph_type(self):
        return GraphType.DIRECTED

    @property
    def board_resizer_type(self):
        return SokobanBoardResizer

    _NEIGHBOR_SHIFT = {
        Direction.LEFT: (0, -1),
        Direction.RIGHT: (0, 1),
        Direction.UP: (-1, 0),
        Direction.DOWN: (1, 0),
    }

    def neighbor_position(self, position, direction, board_width, board_height):
        # if not on_board_1D(position, board_width, board_height):
        #     return None

        row = ROW(position, board_width)
        column = COLUMN(position, board_width)
        row_shift, column_shift = type(self)._NEIGHBOR_SHIFT.get(
            direction, (None, None)
        )

        if row_shift is None:
            raise IllegalDirectionError(direction)

        row += row_shift
        column += column_shift

        if on_board_2D(column, row, board_width, board_height):
            return index_1d(column, row, board_width)

        return None

    _CHR_TO_ATOMIC_MOVE = {
        AtomicMoveCharacters.LOWER_L.value: (Direction.LEFT, False),
        AtomicMoveCharacters.UPPER_L.value: (Direction.LEFT, True),
        AtomicMoveCharacters.LOWER_R.value: (Direction.RIGHT, False),
        AtomicMoveCharacters.UPPER_R.value: (Direction.RIGHT, True),
        AtomicMoveCharacters.LOWER_U.value: (Direction.UP, False),
        AtomicMoveCharacters.UPPER_U.value: (Direction.UP, True),
        AtomicMoveCharacters.LOWER_D.value: (Direction.DOWN, False),
        AtomicMoveCharacters.UPPER_D.value: (Direction.DOWN, True),
    }

    @property
    def _char_to_atomic_move_dict(self):
        return type(self)._CHR_TO_ATOMIC_MOVE

    _ATOMIC_MOVE_TO_CHR = dict((v, k) for k, v in _CHR_TO_ATOMIC_MOVE.items())

    @property
    def _atomic_move_to_char_dict(self):
        return type(self)._ATOMIC_MOVE_TO_CHR
