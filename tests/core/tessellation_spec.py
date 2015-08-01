
from hamcrest import assert_that, equal_to
from sokoenginepy import Direction
from sokoenginepy.core import index_1d, X, Y, on_board_2D, on_board_1D


class Describe_INDEX(object):
    def test_it_calculates_1D_index_from_2D_coordinates(self):
        assert_that(index_1d(0, 0, 5), equal_to(0))
        assert_that(index_1d(4, 5, 5), equal_to(29))
        assert_that(index_1d(3, 3, 5), equal_to(18))


class Describe_X(object):
    def test_it_calculates_X_coordinate_from_1D_index(self):
        assert_that(X(0, 5), equal_to(0))
        assert_that(X(29, 5), equal_to(4))
        assert_that(X(18, 5), equal_to(3))


class Describe_Y(object):
    def test_it_calculates_Y_coordinate_from_1D_index(self):
        assert_that(Y(0, 5), equal_to(0))
        assert_that(Y(29, 5), equal_to(5))
        assert_that(Y(18, 5), equal_to(3))


class Describe_on_board_2D(object):
    def test_it_checks_if_2D_coordinate_is_on_board(self):
        assert_that(on_board_2D(0, 0, 3, 3), equal_to(True))
        assert_that(on_board_2D(1, 1, 3, 3), equal_to(True))
        assert_that(on_board_2D(2, 2, 3, 3), equal_to(True))
        assert_that(on_board_2D(3, 3, 3, 3), equal_to(False))


class Describe_on_board_1D(object):
    def test_it_checks_if_1D_coordinate_is_on_board(self):
        assert_that(on_board_1D(0, 3, 3), equal_to(True))
        assert_that(on_board_1D(4, 3, 3), equal_to(True))
        assert_that(on_board_1D(8, 3, 3), equal_to(True))
        assert_that(on_board_1D(9, 3, 3), equal_to(False))


class DesctibeDirection_opposite(object):
    def test_it_returns_opposite_direction(self):
        assert_that(Direction.UP.opposite, equal_to(Direction.DOWN))
        assert_that(Direction.DOWN.opposite, equal_to(Direction.UP))
        assert_that(Direction.LEFT.opposite, equal_to(Direction.RIGHT))
        assert_that(Direction.RIGHT.opposite, equal_to(Direction.LEFT))
        assert_that(Direction.NORTH_WEST.opposite, equal_to(Direction.SOUTH_EAST))
        assert_that(Direction.NORTH_EAST.opposite, equal_to(Direction.SOUTH_WEST))
        assert_that(Direction.SOUTH_WEST.opposite, equal_to(Direction.NORTH_EAST))
        assert_that(Direction.SOUTH_EAST.opposite, equal_to(Direction.NORTH_WEST))
