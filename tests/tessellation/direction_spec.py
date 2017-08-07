from sokoenginepy import Direction


class DesctibeDirection_opposite:
    def it_returns_opposite_direction(self):
        assert Direction.UP.opposite == Direction.DOWN
        assert Direction.DOWN.opposite == Direction.UP
        assert Direction.LEFT.opposite == Direction.RIGHT
        assert Direction.RIGHT.opposite == Direction.LEFT
        assert Direction.NORTH_WEST.opposite == Direction.SOUTH_EAST
        assert Direction.NORTH_EAST.opposite == Direction.SOUTH_WEST
        assert Direction.SOUTH_WEST.opposite == Direction.NORTH_EAST
        assert Direction.SOUTH_EAST.opposite == Direction.NORTH_WEST
