from sokoenginepy import (
    BoardGraph,
    TileShape,
    Config,
    Direction,
    Puzzle,
    Tessellation,
    index_1d,
    is_on_board_1d,
)

def triangle_points_down(board_graph, position):
    return (
        board_graph.tile_shape(position) == TileShape.TRIANGLE_DOWN
    )


class DescribeTriobanBoardGraph:
    class describe_neighbor_position:
        def test_generated_topLeft(self):
            width = 5
            height = 5
            row = 0
            column = 0
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert triangle_points_down(g, index)

            assert not is_on_board_1d(g.neighbor(index, Direction.LEFT), width, height)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(1, 0, width)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_WEST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_WEST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_EAST), width, height)
            assert g.neighbor(index, Direction.SOUTH_EAST) == index_1d(1, 0, width)

        def test_generated_topRight_columnOdd(self):
            width = 4
            height = 4
            row = 0
            column = 3
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert column % 2 == 1 and not triangle_points_down(g, index)

            assert g.neighbor(index, Direction.LEFT) == index_1d(2, 0, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(2, 0, width)
            assert g.neighbor(index, Direction.SOUTH_WEST) == index_1d(3, 1, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_EAST), width, height)
            assert g.neighbor(index, Direction.SOUTH_EAST) == index_1d(3, 1, width)

        def test_generated_topRight_columnEven(self):
            width = 5
            height = 5
            row = 0
            column = 4
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert column % 2 == 0 and triangle_points_down(g, index)

            assert g.neighbor(index, Direction.LEFT) == index_1d(3, 0, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_WEST), width, height)
            assert g.neighbor(index, Direction.SOUTH_WEST) == index_1d(3, 0, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_EAST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_EAST), width, height)

        def test_generated_bottomLeft_rowOdd(self):
            width = 4
            height = 4
            row = 3
            column = 0
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert row % 2 == 1 and not triangle_points_down(g, index)

            assert not is_on_board_1d(g.neighbor(index, Direction.LEFT), width, height)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(1, 3, width)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_WEST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_WEST), width, height)
            assert g.neighbor(index, Direction.NORTH_EAST) == index_1d(1, 3, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_EAST), width, height)

        def test_generated_bottomLeft_rowEven(self):
            width = 5
            height = 5
            row = 4
            column = 0
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert row % 2 == 0 and triangle_points_down(g, index)

            assert not is_on_board_1d(g.neighbor(index, Direction.LEFT), width, height)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(1, 4, width)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(0, 3, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_WEST), width, height)
            assert g.neighbor(index, Direction.NORTH_EAST) == index_1d(0, 3, width)
            assert g.neighbor(index, Direction.SOUTH_EAST) == index_1d(1, 4, width)

        def test_generated_bottomRight_rowEven_columnEven(self):
            width = 5
            height = 5
            row = 4
            column = 4
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert row % 2 == 0 and column % 2 == 0 and triangle_points_down(g, index)

            assert g.neighbor(index, Direction.LEFT) == index_1d(3, 4, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(4, 3, width)
            assert g.neighbor(index, Direction.SOUTH_WEST) == index_1d(3, 4, width)
            assert g.neighbor(index, Direction.NORTH_EAST) == index_1d(4, 3, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_EAST), width, height)

        def test_generated_bottomRight_rowEven_columnOdd(self):
            width = 4
            height = 5
            row = 4
            column = 3
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert row % 2 == 0 and column % 2 == 1 and not triangle_points_down(g, index)

            assert g.neighbor(index, Direction.LEFT) == index_1d(2, 4, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(2, 4, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_WEST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_EAST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_EAST), width, height)

        def test_generated_bottomRight_rowOdd_columnEven(self):
            width = 5
            height = 4
            row = 3
            column = 4
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert row % 2 == 1 and column % 2 == 0 and not triangle_points_down(g, index)

            assert g.neighbor(index, Direction.LEFT) == index_1d(3, 3, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(3, 3, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_WEST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_EAST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_EAST), width, height)

        def test_generated_bottomRight_rowOdd_columnOdd(self):
            width = 4
            height = 4
            row = 3
            column = 3
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert row % 2 == 1 and column % 2 == 1 and triangle_points_down(g, index)

            assert g.neighbor(index, Direction.LEFT) == index_1d(2, 3, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(3, 2, width)
            assert g.neighbor(index, Direction.SOUTH_WEST) == index_1d(2, 3, width)
            assert g.neighbor(index, Direction.NORTH_EAST) == index_1d(3, 2, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_EAST), width, height)

        def test_generated_midleTop_columnOdd(self):
            width = 10
            height = 10
            row = 0
            column = 3
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert column % 2 == 1 and not triangle_points_down(g, index)

            assert g.neighbor(index, Direction.LEFT) == index_1d(2, 0, width)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(4, 0, width)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(2, 0, width)
            assert g.neighbor(index, Direction.SOUTH_WEST) == index_1d(3, 1, width)
            assert g.neighbor(index, Direction.NORTH_EAST) == index_1d(4, 0, width)
            assert g.neighbor(index, Direction.SOUTH_EAST) == index_1d(3, 1, width)

        def test_generated_midleTop_columnEven(self):
            width = 10
            height = 10
            row = 0
            column = 4
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert column % 2 == 0 and triangle_points_down(g, index)

            assert g.neighbor(index, Direction.LEFT) == index_1d(3, 0, width)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(5, 0, width)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_WEST), width, height)
            assert g.neighbor(index, Direction.SOUTH_WEST) == index_1d(3, 0, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_EAST), width, height)
            assert g.neighbor(index, Direction.SOUTH_EAST) == index_1d(5, 0, width)

        def test_generated_midleBottom_columnOdd_rowEven(self):
            width = 10
            height = 5
            row = 4
            column = 3
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert column % 2 == 1 and row % 2 == 0 and not triangle_points_down(g, index)

            assert g.neighbor(index, Direction.LEFT) == index_1d(2, 4, width)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(4, 4, width)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(2, 4, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_WEST), width, height)
            assert g.neighbor(index, Direction.NORTH_EAST) == index_1d(4, 4, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_EAST), width, height)

        def test_generated_middleBottom_columnEven_rowEven(self):
            width = 10
            height = 5
            row = 4
            column = 4
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert column % 2 == 0 and row % 2 == 0 and triangle_points_down(g, index)

            assert g.neighbor(index, Direction.LEFT) == index_1d(3, 4, width)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(5, 4, width)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(4, 3, width)
            assert g.neighbor(index, Direction.SOUTH_WEST) == index_1d(3, 4, width)
            assert g.neighbor(index, Direction.NORTH_EAST) == index_1d(4, 3, width)
            assert g.neighbor(index, Direction.SOUTH_EAST) == index_1d(5, 4, width)

        def test_generated_midleBottom_columnOdd_rowOdd(self):
            width = 10
            height = 4
            row = 3
            column = 3
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert column % 2 == 1 and row % 2 == 1 and triangle_points_down(g, index)

            assert g.neighbor(index, Direction.LEFT) == index_1d(2, 3, width)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(4, 3, width)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(3, 2, width)
            assert g.neighbor(index, Direction.SOUTH_WEST) == index_1d(2, 3, width)
            assert g.neighbor(index, Direction.NORTH_EAST) == index_1d(3, 2, width)
            assert g.neighbor(index, Direction.SOUTH_EAST) == index_1d(4, 3, width)

        def test_generated_middleBottom_columnEven_rowOdd(self):
            width = 10
            height = 4
            row = 3
            column = 4
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert column % 2 == 0 and row % 2 == 1 and not triangle_points_down(g, index)

            assert g.neighbor(index, Direction.LEFT) == index_1d(3, 3, width)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(5, 3, width)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(3, 3, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_WEST), width, height)
            assert g.neighbor(index, Direction.NORTH_EAST) == index_1d(5, 3, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_EAST), width, height)

        def test_generated_midleLeft_rowOdd(self):
            width = 10
            height = 10
            row = 3
            column = 0
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert row % 2 == 1 and not triangle_points_down(g, index)

            assert not is_on_board_1d(g.neighbor(index, Direction.LEFT), width, height)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(1, 3, width)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_WEST), width, height)
            assert g.neighbor(index, Direction.SOUTH_WEST) == index_1d(0, 4, width)
            assert g.neighbor(index, Direction.NORTH_EAST) == index_1d(1, 3, width)
            assert g.neighbor(index, Direction.SOUTH_EAST) == index_1d(0, 4, width)

        def test_generated_midleLeft_rowEven(self):
            width = 10
            height = 10
            row = 2
            column = 0
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert row % 2 == 0 and triangle_points_down(g, index)

            assert not is_on_board_1d(g.neighbor(index, Direction.LEFT), width, height)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(1, 2, width)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(0, 1, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_WEST), width, height)
            assert g.neighbor(index, Direction.NORTH_EAST) == index_1d(0, 1, width)
            assert g.neighbor(index, Direction.SOUTH_EAST) == index_1d(1, 2, width)

        def test_generated_midleRight_rowOdd_columnOdd(self):
            width = 4
            height = 10
            row = 3
            column = 3
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert row % 2 == 1 and column % 2 == 1 and triangle_points_down(g, index)

            assert g.neighbor(index, Direction.LEFT) == index_1d(2, 3, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(3, 2, width)
            assert g.neighbor(index, Direction.SOUTH_WEST) == index_1d(2, 3, width)
            assert g.neighbor(index, Direction.NORTH_EAST) == index_1d(3, 2, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_EAST), width, height)

        def test_generated_midleRight_rowEven_columnOdd(self):
            width = 4
            height = 10
            row = 2
            column = 3
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert row % 2 == 0 and column % 2 == 1 and not triangle_points_down(g, index)

            assert g.neighbor(index, Direction.LEFT) == index_1d(2, 2, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(2, 2, width)
            assert g.neighbor(index, Direction.SOUTH_WEST) == index_1d(3, 3, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_EAST), width, height)
            assert g.neighbor(index, Direction.SOUTH_EAST) == index_1d(3, 3, width)

        def test_generated_midleRight_rowOdd_columnEven(self):
            width = 5
            height = 10
            row = 3
            column = 4
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert row % 2 == 1 and column % 2 == 0 and not triangle_points_down(g, index)

            assert g.neighbor(index, Direction.LEFT) == index_1d(3, 3, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(3, 3, width)
            assert g.neighbor(index, Direction.SOUTH_WEST) == index_1d(4, 4, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_EAST), width, height)
            assert g.neighbor(index, Direction.SOUTH_EAST) == index_1d(4, 4, width)

        def test_generated_midleRight_rowEven_columnEven(self):
            width = 5
            height = 10
            row = 2
            column = 4
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert row % 2 == 0 and column % 2 == 0 and triangle_points_down(g, index)

            assert g.neighbor(index, Direction.LEFT) == index_1d(3, 2, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(4, 1, width)
            assert g.neighbor(index, Direction.SOUTH_WEST) == index_1d(3, 2, width)
            assert g.neighbor(index, Direction.NORTH_EAST) == index_1d(4, 1, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_EAST), width, height)

        def test_generated_midle_rowOdd_columnOdd(self):
            width = 10
            height = 10
            row = 3
            column = 3
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert row % 2 == 1 and column % 2 == 1 and triangle_points_down(g, index)

            assert g.neighbor(index, Direction.LEFT) == index_1d(2, 3, width)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(4, 3, width)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(3, 2, width)
            assert g.neighbor(index, Direction.SOUTH_WEST) == index_1d(2, 3, width)
            assert g.neighbor(index, Direction.NORTH_EAST) == index_1d(3, 2, width)
            assert g.neighbor(index, Direction.SOUTH_EAST) == index_1d(4, 3, width)

        def test_generated_midle_rowOdd_columnEven(self):
            width = 10
            height = 10
            row = 3
            column = 2
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert row % 2 == 1 and column % 2 == 0 and not triangle_points_down(g, index)

            assert g.neighbor(index, Direction.LEFT) == index_1d(1, 3, width)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(3, 3, width)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(1, 3, width)
            assert g.neighbor(index, Direction.SOUTH_WEST) == index_1d(2, 4, width)
            assert g.neighbor(index, Direction.NORTH_EAST) == index_1d(3, 3, width)
            assert g.neighbor(index, Direction.SOUTH_EAST) == index_1d(2, 4, width)

        def test_generated_midle_rowEven_columnOdd(self):
            width = 10
            height = 10
            row = 2
            column = 3
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert row % 2 == 0 and column % 2 == 1 and not triangle_points_down(g, index)

            assert g.neighbor(index, Direction.LEFT) == index_1d(2, 2, width)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(4, 2, width)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(2, 2, width)
            assert g.neighbor(index, Direction.SOUTH_WEST) == index_1d(3, 3, width)
            assert g.neighbor(index, Direction.NORTH_EAST) == index_1d(4, 2, width)
            assert g.neighbor(index, Direction.SOUTH_EAST) == index_1d(3, 3, width)

        def test_generated_midle_rowEven_columnEven(self):
            width = 10
            height = 10
            row = 2
            column = 2
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert row % 2 == 0 and column % 2 == 0 and triangle_points_down(g, index)

            assert g.neighbor(index, Direction.LEFT) == index_1d(1, 2, width)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(3, 2, width)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(2, 1, width)
            assert g.neighbor(index, Direction.SOUTH_WEST) == index_1d(1, 2, width)
            assert g.neighbor(index, Direction.NORTH_EAST) == index_1d(2, 1, width)
            assert g.neighbor(index, Direction.SOUTH_EAST) == index_1d(3, 2, width)

        def test_generated_board_1x1(self):
            width = 1
            height = 1
            row = 0
            column = 0
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert not is_on_board_1d(g.neighbor(index, Direction.LEFT), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_WEST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_WEST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_EAST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_EAST), width, height)

        def test_generated_board_2x1_left(self):
            width = 2
            height = 1
            row = 0
            column = 0
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert not is_on_board_1d(g.neighbor(index, Direction.LEFT), width, height)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(1, 0, width)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_WEST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_WEST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_EAST), width, height)
            assert g.neighbor(index, Direction.SOUTH_EAST) == index_1d(1, 0, width)

        def test_generated_board_2x1_right(self):
            width = 2
            height = 1
            row = 0
            column = 1
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert g.neighbor(index, Direction.LEFT) == index_1d(0, 0, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(0, 0, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_WEST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_EAST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_EAST), width, height)

        def test_generated_board_3x1_right(self):
            width = 3
            height = 1
            row = 0
            column = 2
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert g.neighbor(index, Direction.LEFT) == index_1d(1, 0, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_WEST), width, height)
            assert g.neighbor(index, Direction.SOUTH_WEST) == index_1d(1, 0, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_EAST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_EAST), width, height)

        def test_generated_1x2_top(self):
            width = 1
            height = 2
            row = 0
            column = 0
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert not is_on_board_1d(g.neighbor(index, Direction.LEFT), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_WEST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_WEST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_EAST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_EAST), width, height)

        def test_generated_1x2_bottom(self):
            width = 1
            height = 2
            row = 1
            column = 0
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert not is_on_board_1d(g.neighbor(index, Direction.LEFT), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_WEST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_WEST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.NORTH_EAST), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_EAST), width, height)

        def test_generated_1x3_bottom(self):
            width = 1
            height = 3
            row = 2
            column = 0
            puzzle = Puzzle(Tessellation.TRIOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert not is_on_board_1d(g.neighbor(index, Direction.LEFT), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert g.neighbor(index, Direction.UP) == Config.NO_POS
            assert g.neighbor(index, Direction.DOWN) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_WEST) == index_1d(0, 1, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_WEST), width, height)
            assert g.neighbor(index, Direction.NORTH_EAST) == index_1d(0, 1, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.SOUTH_EAST), width, height)


