from ..common import Direction, UnknownDirectionError
from ..snapshot import AtomicMoveCharacters
from .graph import GraphType
from .tessellation import (COLUMN, ROW, CellOrientation, Tessellation,
                           index_1d, on_board_2d)


class TriobanTessellation(Tessellation):
    """Implements :class:`.Tessellation` for Trioban variant. """

    _LEGAL_DIRECTIONS = (
        Direction.LEFT, Direction.RIGHT, Direction.NORTH_EAST,
        Direction.NORTH_WEST, Direction.SOUTH_EAST, Direction.SOUTH_WEST
    )

    @property
    def legal_directions(self):
        return self._LEGAL_DIRECTIONS

    @property
    def graph_type(self):
        return GraphType.DIRECTED_MULTI

    def neighbor_position(self, position, direction, board_width, board_height):
        # if not on_board_1d(position, board_width, board_height):
        #     return None

        row = ROW(position, board_width)
        column = COLUMN(position, board_width)
        triangle_points_down = (
            self.cell_orientation(position, board_width, board_height) ==
            CellOrientation.TRIANGLE_DOWN
        )

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
            raise UnknownDirectionError(direction)

        row += dy
        column += dx

        if on_board_2d(column, row, board_width, board_height):
            return index_1d(column, row, board_width)

        return None

    _CHR_TO_ATOMIC_MOVE = {
        AtomicMoveCharacters.LOWER_L.value: (Direction.LEFT, False),
        AtomicMoveCharacters.UPPER_L.value: (Direction.LEFT, True),
        AtomicMoveCharacters.LOWER_R.value: (Direction.RIGHT, False),
        AtomicMoveCharacters.UPPER_R.value: (Direction.RIGHT, True),
        AtomicMoveCharacters.LOWER_NE.value: (Direction.NORTH_EAST, False),
        AtomicMoveCharacters.UPPER_NE.value: (Direction.NORTH_EAST, True),
        AtomicMoveCharacters.LOWER_U.value: (Direction.NORTH_WEST, False),
        AtomicMoveCharacters.UPPER_U.value: (Direction.NORTH_WEST, True),
        AtomicMoveCharacters.LOWER_D.value: (Direction.SOUTH_EAST, False),
        AtomicMoveCharacters.UPPER_D.value: (Direction.SOUTH_EAST, True),
        AtomicMoveCharacters.LOWER_SW.value: (Direction.SOUTH_WEST, False),
        AtomicMoveCharacters.UPPER_SW.value: (Direction.SOUTH_WEST, True),
    }

    @property
    def _char_to_atomic_move_dict(self):
        return self._CHR_TO_ATOMIC_MOVE

    _ATOMIC_MOVE_TO_CHR = dict((v, k) for k, v in _CHR_TO_ATOMIC_MOVE.items())

    @property
    def _atomic_move_to_char_dict(self):
        return self._ATOMIC_MOVE_TO_CHR

    def cell_orientation(self, position, board_width, board_height):
        row = ROW(position, board_width)
        column = COLUMN(position, board_width)
        return (
            CellOrientation.TRIANGLE_DOWN
            if (column + (row % 2)) % 2 == 0 else CellOrientation.DEFAULT
        )
