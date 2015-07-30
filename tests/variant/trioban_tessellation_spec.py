from sokoengine import Direction, AtomicMove
from sokoengine.core import Tessellation
from helpers import TessellationSpecMixin

from autogenerated import TriobanTessellationAutogeneratedSpecMixin


class DescribeTriobanTessellation(
    TessellationSpecMixin, TriobanTessellationAutogeneratedSpecMixin
):

    illegal_directions = [
        Direction.UP, Direction.DOWN
    ]

    legal_directions = [
        Direction.LEFT, Direction.RIGHT,
        Direction.NORTH_WEST, Direction.NORTH_EAST,
        Direction.SOUTH_WEST, Direction.SOUTH_EAST,
    ]

    legal_moves = [
        AtomicMove(Direction.LEFT, False),
        AtomicMove(Direction.RIGHT, False),
        AtomicMove(Direction.NORTH_WEST, False),
        AtomicMove(Direction.NORTH_EAST, False),
        AtomicMove(Direction.SOUTH_WEST, False),
        AtomicMove(Direction.SOUTH_EAST, False),
        AtomicMove(Direction.LEFT, True),
        AtomicMove(Direction.RIGHT, True),
        AtomicMove(Direction.NORTH_WEST, True),
        AtomicMove(Direction.NORTH_EAST, True),
        AtomicMove(Direction.SOUTH_WEST, True),
        AtomicMove(Direction.SOUTH_EAST, True)
    ]

    legal_characters = [
        'l', 'r', 'u', 'n', 's', 'd', 'L', 'R', 'U', 'N', 'S', 'D'
    ]

    tessellation = Tessellation.factory('Trioban')
