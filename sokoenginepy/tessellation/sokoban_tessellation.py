from ..common import Direction, UnknownDirectionError
from ..snapshot import AtomicMoveCharacters
from .graph import GraphType
from .tessellation import COLUMN, ROW, Tessellation, index_1d, on_board_2d


class SokobanTessellation(Tessellation):
    """Implements :class:`.Tessellation` for Sokoban variant."""

    _LEGAL_DIRECTIONS = (
        Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN
    )

    @property
    def legal_directions(self):
        return self._LEGAL_DIRECTIONS

    @property
    def graph_type(self):
        return GraphType.DIRECTED

    _NEIGHBOR_SHIFT = {
        Direction.LEFT: (0, -1),
        Direction.RIGHT: (0, 1),
        Direction.UP: (-1, 0),
        Direction.DOWN: (1, 0),
    }

    def neighbor_position(self, position, direction, board_width, board_height):
        # if not on_board_1d(position, board_width, board_height):
        #     return None

        row = ROW(position, board_width)
        column = COLUMN(position, board_width)
        row_shift, column_shift = self._NEIGHBOR_SHIFT.get(
            direction, (None, None)
        )

        if row_shift is None:
            raise UnknownDirectionError(direction)

        row += row_shift
        column += column_shift

        if on_board_2d(column, row, board_width, board_height):
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
        return self._CHR_TO_ATOMIC_MOVE

    _ATOMIC_MOVE_TO_CHR = dict((v, k) for k, v in _CHR_TO_ATOMIC_MOVE.items())

    @property
    def _atomic_move_to_char_dict(self):
        return self._ATOMIC_MOVE_TO_CHR
