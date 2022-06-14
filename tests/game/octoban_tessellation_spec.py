from sokoenginepy.game import BaseTessellation, Direction, PusherStep, Tessellation

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
        PusherStep(Direction.LEFT, False),
        PusherStep(Direction.RIGHT, False),
        PusherStep(Direction.UP, False),
        PusherStep(Direction.DOWN, False),
        PusherStep(Direction.NORTH_WEST, False),
        PusherStep(Direction.NORTH_EAST, False),
        PusherStep(Direction.SOUTH_WEST, False),
        PusherStep(Direction.SOUTH_EAST, False),
        PusherStep(Direction.LEFT, True),
        PusherStep(Direction.RIGHT, True),
        PusherStep(Direction.UP, True),
        PusherStep(Direction.DOWN, True),
        PusherStep(Direction.NORTH_WEST, True),
        PusherStep(Direction.NORTH_EAST, True),
        PusherStep(Direction.SOUTH_WEST, True),
        PusherStep(Direction.SOUTH_EAST, True),
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

    tessellation = BaseTessellation.instance(Tessellation.OCTOBAN)
