from ..core.tessellation import Tessellation, on_board_2D, on_board_1D, ROW, \
    COLUMN, INDEX
from ..core import Direction, IllegalDirectionError, AtomicMove
from ..io.text_utils import AtomicMoveCharacters


class HexobanTessellation(Tessellation):
    _LEGAL_DIRECTIONS = (
        Direction.LEFT, Direction.RIGHT, Direction.NORTH_EAST,
        Direction.NORTH_WEST, Direction.SOUTH_EAST, Direction.SOUTH_WEST,
    )

    @property
    def legal_directions(self):
        return type(self)._LEGAL_DIRECTIONS

    def neighbor_position(self, position, direction, board_width, board_height):
        if on_board_1D(position, board_width, board_height):
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
                return INDEX(column, row, board_width)
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
    def char_to_atomic_move_dict(self):
        return type(self)._CHR_TO_ATOMIC_MOVE

    _ATOMIC_MOVE_TO_CHR = dict((v, k) for k, v in _CHR_TO_ATOMIC_MOVE.items())

    @property
    def atomic_move_to_char_dict(self):
        return type(self)._ATOMIC_MOVE_TO_CHR