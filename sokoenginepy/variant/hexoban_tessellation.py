from ..core import (
    Tessellation, on_board_2D, on_board_1D, ROW, COLUMN, index_1d, Direction,
    IllegalDirectionError
)
from ..io import AtomicMoveCharacters
from .hexoban_board import HexobanBoardResizer
from .board_graph import GraphType


class HexobanTessellation(Tessellation):
    """
    Implements Tessellation for Hexoban variant.
    """

    _LEGAL_DIRECTIONS = (
        Direction.LEFT, Direction.RIGHT, Direction.NORTH_EAST,
        Direction.NORTH_WEST, Direction.SOUTH_EAST, Direction.SOUTH_WEST,
    )

    @property
    def legal_directions(self):
        return type(self)._LEGAL_DIRECTIONS

    @property
    def graph_type(self):
        return GraphType.DIRECTED

    @property
    def board_resizer_type(self):
        return HexobanBoardResizer

    def neighbor_position(self, position, direction, board_width, board_height):
        # if not on_board_1D(position, board_width, board_height):
        #     return None

        row = ROW(position, board_width)
        column = COLUMN(position, board_width)

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
            raise IllegalDirectionError(direction)

        if on_board_2D(column, row, board_width, board_height):
            return index_1d(column, row, board_width)
        return None

    _CHR_TO_ATOMIC_MOVE = {
        AtomicMoveCharacters.LOWER_L.value: (Direction.LEFT, False),
        AtomicMoveCharacters.UPPER_L.value: (Direction.LEFT, True),
        AtomicMoveCharacters.LOWER_R.value: (Direction.RIGHT, False),
        AtomicMoveCharacters.UPPER_R.value: (Direction.RIGHT, True),
        AtomicMoveCharacters.LOWER_U.value: (Direction.NORTH_WEST, False),
        AtomicMoveCharacters.UPPER_U.value: (Direction.NORTH_WEST, True),
        AtomicMoveCharacters.LOWER_D.value: (Direction.SOUTH_EAST, False),
        AtomicMoveCharacters.UPPER_D.value: (Direction.SOUTH_EAST, True),
        AtomicMoveCharacters.LOWER_NE.value: (Direction.NORTH_EAST, False),
        AtomicMoveCharacters.UPPER_NE.value: (Direction.NORTH_EAST, True),
        AtomicMoveCharacters.LOWER_SW.value: (Direction.SOUTH_WEST, False),
        AtomicMoveCharacters.UPPER_SW.value: (Direction.SOUTH_WEST, True),
    }

    @property
    def _char_to_atomic_move_dict(self):
        return type(self)._CHR_TO_ATOMIC_MOVE

    _ATOMIC_MOVE_TO_CHR = dict((v, k) for k, v in _CHR_TO_ATOMIC_MOVE.items())

    @property
    def _atomic_move_to_char_dict(self):
        return type(self)._ATOMIC_MOVE_TO_CHR
