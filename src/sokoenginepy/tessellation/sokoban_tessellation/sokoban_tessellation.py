from ...utilities import COLUMN, ROW, index_1d, inverted, is_on_board_2d
from ..direction import Direction
from ..tessellation_base import TessellationBase


class SokobanTessellation(TessellationBase):
    _LEGAL_DIRECTIONS = (Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN)

    _CHR_TO_ATOMIC_MOVE = None
    _ATOMIC_MOVE_TO_CHR = None

    @property
    def legal_directions(self):
        return self._LEGAL_DIRECTIONS

    @property
    def graph_type(self):
        from ...graph import GraphType

        return GraphType.DIRECTED

    _NEIGHBOR_SHIFT = {
        Direction.LEFT: (0, -1),
        Direction.RIGHT: (0, 1),
        Direction.UP: (-1, 0),
        Direction.DOWN: (1, 0),
    }

    def neighbor_position(self, position, direction, board_width, board_height):
        # if not is_on_board_1d(position, board_width, board_height):
        #     return None

        row = ROW(position, board_width)
        column = COLUMN(position, board_width)
        row_shift, column_shift = self._NEIGHBOR_SHIFT.get(direction, (None, None))

        if row_shift is None:
            raise ValueError(direction)

        row += row_shift
        column += column_shift

        if is_on_board_2d(column, row, board_width, board_height):
            return index_1d(column, row, board_width)

        return None

    @property
    def _char_to_atomic_move_dict(self):
        if not self.__class__._CHR_TO_ATOMIC_MOVE:
            from ...snapshot import AtomicMove

            self.__class__._CHR_TO_ATOMIC_MOVE = {
                AtomicMove.l: (Direction.LEFT, False),
                AtomicMove.L: (Direction.LEFT, True),
                AtomicMove.r: (Direction.RIGHT, False),
                AtomicMove.R: (Direction.RIGHT, True),
                AtomicMove.u: (Direction.UP, False),
                AtomicMove.U: (Direction.UP, True),
                AtomicMove.d: (Direction.DOWN, False),
                AtomicMove.D: (Direction.DOWN, True),
            }
        return self._CHR_TO_ATOMIC_MOVE

    @property
    def _atomic_move_to_char_dict(self):
        if not self.__class__._ATOMIC_MOVE_TO_CHR:
            self.__class__._ATOMIC_MOVE_TO_CHR = inverted(
                self._char_to_atomic_move_dict
            )
        return self._ATOMIC_MOVE_TO_CHR

    def __str__(self):
        return "sokoban"
