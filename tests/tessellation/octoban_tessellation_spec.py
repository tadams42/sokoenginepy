from sokoenginepy import AtomicMove, Direction, Tessellation

from .autogenerated_tessellation import OctobanTessellationAutogeneratedSpecMixin
from .tessellation_spec_mixin import TessellationSpecMixin


class DescribeOctobanTessellation(
    TessellationSpecMixin, OctobanTessellationAutogeneratedSpecMixin
):

    illegal_directions = []

    legal_directions = [
        Direction.LEFT,
        Direction.RIGHT,
        Direction.UP,
        Direction.DOWN,
        Direction.NORTH_WEST,
        Direction.NORTH_EAST,
        Direction.SOUTH_WEST,
        Direction.SOUTH_EAST,
    ]

    legal_moves = [
        AtomicMove(Direction.LEFT, False),
        AtomicMove(Direction.RIGHT, False),
        AtomicMove(Direction.UP, False),
        AtomicMove(Direction.DOWN, False),
        AtomicMove(Direction.NORTH_WEST, False),
        AtomicMove(Direction.NORTH_EAST, False),
        AtomicMove(Direction.SOUTH_WEST, False),
        AtomicMove(Direction.SOUTH_EAST, False),
        AtomicMove(Direction.LEFT, True),
        AtomicMove(Direction.RIGHT, True),
        AtomicMove(Direction.UP, True),
        AtomicMove(Direction.DOWN, True),
        AtomicMove(Direction.NORTH_WEST, True),
        AtomicMove(Direction.NORTH_EAST, True),
        AtomicMove(Direction.SOUTH_WEST, True),
        AtomicMove(Direction.SOUTH_EAST, True),
    ]

    legal_characters = [
        "l",
        "r",
        "u",
        "d",
        "w",
        "n",
        "s",
        "e",
        "L",
        "R",
        "U",
        "D",
        "W",
        "N",
        "S",
        "E",
    ]

    tessellation = Tessellation.instance_from("Octoban")
