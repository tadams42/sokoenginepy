from .tessellation import Tessellation, on_board_2D, on_board_1D, ROW, \
    COLUMN, INDEX, Direction, CellOrientation
from ..core.exceptions import IllegalDirectionError
from ..io.text_utils import AtomicMoveCharacters


class OctobanTessellation(Tessellation):
    _LEGAL_DIRECTIONS = (
        Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN,
        Direction.NORTH_EAST, Direction.NORTH_WEST,
        Direction.SOUTH_EAST, Direction.SOUTH_WEST,
    )

    @property
    def legal_directions(self):
        return type(self)._LEGAL_DIRECTIONS

    _NEIGHBOR_SHIFT = {
        Direction.LEFT      : (0, -1),
        Direction.RIGHT     : (0, 1),
        Direction.UP        : (-1, 0),
        Direction.DOWN      : (1, 0),
        Direction.NORTH_WEST: (-1, -1),
        Direction.NORTH_EAST: (-1, 1),
        Direction.SOUTH_WEST: (1, -1),
        Direction.SOUTH_EAST: (1, 1),
    }

    def neighbor_position(self, position, direction, board_width, board_height):
        if on_board_1D(position, board_width, board_height):
            if self.cell_orientation(
                position, board_width, board_height
            ) != CellOrientation.OCTAGON and (
                direction == Direction.NORTH_EAST or
                direction == Direction.NORTH_WEST or
                direction == Direction.SOUTH_EAST or
                direction == Direction.SOUTH_WEST
            ):
                return None

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
                return INDEX(column, row, board_width)

        return None

    _CHR_TO_ATOMIC_MOVE = {
        AtomicMoveCharacters.LOWER_L.value : (Direction.LEFT, False),
        AtomicMoveCharacters.UPPER_L.value : (Direction.LEFT, True),
        AtomicMoveCharacters.LOWER_R.value : (Direction.RIGHT, False),
        AtomicMoveCharacters.UPPER_R.value : (Direction.RIGHT, True),
        AtomicMoveCharacters.LOWER_U.value : (Direction.UP, False),
        AtomicMoveCharacters.UPPER_U.value : (Direction.UP, True),
        AtomicMoveCharacters.LOWER_D.value : (Direction.DOWN, False),
        AtomicMoveCharacters.UPPER_D.value : (Direction.DOWN, True),
        AtomicMoveCharacters.LOWER_NW.value: (Direction.NORTH_WEST, False),
        AtomicMoveCharacters.UPPER_NW.value: (Direction.NORTH_WEST, True),
        AtomicMoveCharacters.LOWER_SE.value: (Direction.SOUTH_EAST, False),
        AtomicMoveCharacters.UPPER_SE.value: (Direction.SOUTH_EAST, True),
        AtomicMoveCharacters.LOWER_NE.value: (Direction.NORTH_EAST, False),
        AtomicMoveCharacters.UPPER_NE.value: (Direction.NORTH_EAST, True),
        AtomicMoveCharacters.LOWER_SW.value: (Direction.SOUTH_WEST, False),
        AtomicMoveCharacters.UPPER_SW.value: (Direction.SOUTH_WEST, True),
    }

    @property
    def char_to_atomic_move_dict(self):
        return type(self)._CHR_TO_ATOMIC_MOVE

    _ATOMIC_MOVE_TO_CHR = dict((v, k) for k, v in _CHR_TO_ATOMIC_MOVE.items())

    @property
    def atomic_move_to_char_dict(self):
        return type(self)._ATOMIC_MOVE_TO_CHR

    def cell_orientation(self, position, board_width, board_height):
        row = ROW(position, board_width)
        column = COLUMN(position, board_width)
        return (
            CellOrientation.OCTAGON
            if (column + (row % 2)) % 2 == 0
            else CellOrientation.DEFAULT
        )
