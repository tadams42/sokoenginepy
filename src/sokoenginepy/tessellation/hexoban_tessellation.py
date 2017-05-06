from .. import utilities
from .direction import Direction, UnknownDirectionError
from .helpers import COLUMN, ROW, index_1d, is_on_board_2d
from .tessellation_base import (TessellationBase,
                                TessellationBaseInheritableDocstrings)

_GLOBALS = {}


def _init_module():
    """
    Avoiding circular dependnecies by not importing :mod:`.board` and
    :mod:`.snapshot` untill they are needed
    """
    from .. import board, snapshot
    _GLOBALS['graph_type'] = board.GraphType.DIRECTED
    _GLOBALS['chr_to_atomic_move'] = {
        snapshot.AtomicMove.Characters.LOWER_L: (Direction.LEFT, False),
        snapshot.AtomicMove.Characters.UPPER_L: (Direction.LEFT, True),
        snapshot.AtomicMove.Characters.LOWER_R: (Direction.RIGHT, False),
        snapshot.AtomicMove.Characters.UPPER_R: (Direction.RIGHT, True),
        snapshot.AtomicMove.Characters.LOWER_U: (Direction.NORTH_WEST, False),
        snapshot.AtomicMove.Characters.UPPER_U: (Direction.NORTH_WEST, True),
        snapshot.AtomicMove.Characters.LOWER_D: (Direction.SOUTH_EAST, False),
        snapshot.AtomicMove.Characters.UPPER_D: (Direction.SOUTH_EAST, True),
        snapshot.AtomicMove.Characters.LOWER_NE: (Direction.NORTH_EAST, False),
        snapshot.AtomicMove.Characters.UPPER_NE: (Direction.NORTH_EAST, True),
        snapshot.AtomicMove.Characters.LOWER_SW: (Direction.SOUTH_WEST, False),
        snapshot.AtomicMove.Characters.UPPER_SW: (Direction.SOUTH_WEST, True),
    }
    _GLOBALS['atomic_move_to_chr'
            ] = utilities.inverted(_GLOBALS['chr_to_atomic_move'])


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

    @property
    @copy_ancestor_docstring
    def legal_directions(self):
        return self._LEGAL_DIRECTIONS

    @property
    @copy_ancestor_docstring
    def graph_type(self):
        if not _GLOBALS:
            _init_module()
        return _GLOBALS['graph_type']

    @copy_ancestor_docstring
    def neighbor_position(self, position, direction, board_width, board_height):
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
        if not _GLOBALS:
            _init_module()
        return _GLOBALS['chr_to_atomic_move']

    @property
    def _atomic_move_to_char_dict(self):
        if not _GLOBALS:
            _init_module()
        return _GLOBALS['atomic_move_to_chr']

    def __str__(self):
        return "hexoban"
