from sokoenginepy.utilities import X, Y, index_1d, is_on_board_1d, is_on_board_2d


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
        assert is_on_board_2d(0, 0, 3, 3)
        assert is_on_board_2d(1, 1, 3, 3)
        assert is_on_board_2d(2, 2, 3, 3)
        assert not is_on_board_2d(3, 3, 3, 3)


class Describe_on_board_1d:
    def it_checks_if_1D_coordinate_is_on_board(self):
        assert is_on_board_1d(0, 3, 3)
        assert is_on_board_1d(4, 3, 3)
        assert is_on_board_1d(8, 3, 3)
        assert not is_on_board_1d(9, 3, 3)
