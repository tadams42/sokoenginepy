from sokoenginepy.common import Direction
from sokoenginepy.tessellation import X, Y, index_1d, on_board_1d, on_board_2d


class Describe_INDEX:

    def it_calculates_1D_index_from_2D_coordinates(self):
        assert index_1d(0, 0, 5) == 0
        assert index_1d(4, 5, 5) == 29
        assert index_1d(3, 3, 5) == 18


class Describe_X:

    def it_calculates_X_coordinate_from_1D_index(self):
        assert X(0, 5) == 0
        assert X(29, 5) == 4
        assert X(18, 5) == 3


class Describe_Y:

    def it_calculates_Y_coordinate_from_1D_index(self):
        assert Y(0, 5) == 0
        assert Y(29, 5) == 5
        assert Y(18, 5) == 3


class Describe_on_board_2d:

    def it_checks_if_2D_coordinate_is_on_board(self):
        assert on_board_2d(0, 0, 3, 3)
        assert on_board_2d(1, 1, 3, 3)
        assert on_board_2d(2, 2, 3, 3)
        assert not on_board_2d(3, 3, 3, 3)


class Describe_on_board_1d:

    def it_checks_if_1D_coordinate_is_on_board(self):
        assert on_board_1d(0, 3, 3)
        assert on_board_1d(4, 3, 3)
        assert on_board_1d(8, 3, 3)
        assert not on_board_1d(9, 3, 3)


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
