from ...utilities import COLUMN, ROW, index_1d, inverted, is_on_board_2d
from ..direction import Direction, UnknownDirectionError
from ..tessellation_base import (TessellationBase,
                                 TessellationBaseInheritableDocstrings)


class HexobanTessellation(
    TessellationBase, metaclass=TessellationBaseInheritableDocstrings
):
    _LEGAL_DIRECTIONS = (
        Direction.LEFT,
        Direction.RIGHT,
        Direction.NORTH_EAST,
        Direction.NORTH_WEST,
        Direction.SOUTH_EAST,
        Direction.SOUTH_WEST,
    )

    _CHR_TO_ATOMIC_MOVE = None
    _ATOMIC_MOVE_TO_CHR = None

    @property
    @copy_ancestor_docstring
    def legal_directions(self):
        return self._LEGAL_DIRECTIONS

    @property
    @copy_ancestor_docstring
    def graph_type(self):
        from ...graph import GraphType
        return GraphType.DIRECTED

    @copy_ancestor_docstring
    def neighbor_position(
        self, position, direction, board_width, board_height
    ):
        # if not is_on_board_1d(position, board_width, board_height):
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
            raise UnknownDirectionError(direction)

        if is_on_board_2d(column, row, board_width, board_height):
            return index_1d(column, row, board_width)
        return None

    @property
    def _char_to_atomic_move_dict(self):
        if not self.__class__._CHR_TO_ATOMIC_MOVE:
            from ...snapshot import AtomicMoveCharacters
            self.__class__._CHR_TO_ATOMIC_MOVE = {
                AtomicMoveCharacters.l: (Direction.LEFT, False),
                AtomicMoveCharacters.L: (Direction.LEFT, True),
                AtomicMoveCharacters.r: (Direction.RIGHT, False),
                AtomicMoveCharacters.R: (Direction.RIGHT, True),
                AtomicMoveCharacters.u: (Direction.NORTH_WEST, False),
                AtomicMoveCharacters.U: (Direction.NORTH_WEST, True),
                AtomicMoveCharacters.d: (Direction.SOUTH_EAST, False),
                AtomicMoveCharacters.D: (Direction.SOUTH_EAST, True),
                AtomicMoveCharacters.n: (Direction.NORTH_EAST, False),
                AtomicMoveCharacters.N: (Direction.NORTH_EAST, True),
                AtomicMoveCharacters.s: (Direction.SOUTH_WEST, False),
                AtomicMoveCharacters.S: (Direction.SOUTH_WEST, True),
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
        return "hexoban"
