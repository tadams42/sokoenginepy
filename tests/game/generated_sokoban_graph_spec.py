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


class DescribeSokobanBoardGraph:
    class describe_neighbor_position:
        def test_generated_topLeft(self):
            width = 10
            height = 10
            row = 0
            column = 0
            puzzle = Puzzle(Tessellation.SOKOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert not is_on_board_1d(g.neighbor(index, Direction.LEFT), width, height)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(1, 0, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.UP), width, height)
            assert g.neighbor(index, Direction.DOWN) == index_1d(0, 1, width)
            assert g.neighbor(index, Direction.NORTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_EAST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_EAST) == Config.NO_POS

        def test_generated_topRight(self):
            width = 10
            height = 10
            row = 0
            column = 9
            puzzle = Puzzle(Tessellation.SOKOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert g.neighbor(index, Direction.LEFT) == index_1d(8, 0, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.UP), width, height)
            assert g.neighbor(index, Direction.DOWN) == index_1d(9, 1, width)
            assert g.neighbor(index, Direction.NORTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_EAST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_EAST) == Config.NO_POS

        def test_generated_bottomLeft(self):
            width = 10
            height = 10
            row = 9
            column = 0
            puzzle = Puzzle(Tessellation.SOKOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert not is_on_board_1d(g.neighbor(index, Direction.LEFT), width, height)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(1, 9, width)
            assert g.neighbor(index, Direction.UP) == index_1d(0, 8, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.DOWN), width, height)
            assert g.neighbor(index, Direction.NORTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_EAST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_EAST) == Config.NO_POS

        def test_generated_bottomRight(self):
            width = 10
            height = 10
            row = 9
            column = 9
            puzzle = Puzzle(Tessellation.SOKOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert g.neighbor(index, Direction.LEFT) == index_1d(8, 9, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert g.neighbor(index, Direction.UP) == index_1d(9, 8, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.DOWN), width, height)
            assert g.neighbor(index, Direction.NORTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_EAST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_EAST) == Config.NO_POS

        def test_generated_midleTop(self):
            width = 10
            height = 10
            row = 0
            column = 5
            puzzle = Puzzle(Tessellation.SOKOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert g.neighbor(index, Direction.LEFT) == index_1d(4, 0, width)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(6, 0, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.UP), width, height)
            assert g.neighbor(index, Direction.DOWN) == index_1d(5, 1, width)
            assert g.neighbor(index, Direction.NORTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_EAST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_EAST) == Config.NO_POS

        def test_generated_midleBottom(self):
            width = 10
            height = 10
            row = 9
            column = 5
            puzzle = Puzzle(Tessellation.SOKOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert g.neighbor(index, Direction.LEFT) == index_1d(4, 9, width)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(6, 9, width)
            assert g.neighbor(index, Direction.UP) == index_1d(5, 8, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.DOWN), width, height)
            assert g.neighbor(index, Direction.NORTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_EAST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_EAST) == Config.NO_POS

        def test_generated_midleLeft(self):
            width = 10
            height = 10
            row = 5
            column = 0
            puzzle = Puzzle(Tessellation.SOKOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert not is_on_board_1d(g.neighbor(index, Direction.LEFT), width, height)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(1, 5, width)
            assert g.neighbor(index, Direction.UP) == index_1d(0, 4, width)
            assert g.neighbor(index, Direction.DOWN) == index_1d(0, 6, width)
            assert g.neighbor(index, Direction.NORTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_EAST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_EAST) == Config.NO_POS

        def test_generated_midleRight(self):
            width = 10
            height = 10
            row = 5
            column = 9
            puzzle = Puzzle(Tessellation.SOKOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert g.neighbor(index, Direction.LEFT) == index_1d(8, 5, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert g.neighbor(index, Direction.UP) == index_1d(9, 4, width)
            assert g.neighbor(index, Direction.DOWN) == index_1d(9, 6, width)
            assert g.neighbor(index, Direction.NORTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_EAST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_EAST) == Config.NO_POS

        def test_generated_board_1x1(self):
            width = 1
            height = 1
            row = 0
            column = 0
            puzzle = Puzzle(Tessellation.SOKOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert not is_on_board_1d(g.neighbor(index, Direction.LEFT), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.UP), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.DOWN), width, height)
            assert g.neighbor(index, Direction.NORTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_EAST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_EAST) == Config.NO_POS

        def test_generated_board_2x1_left(self):
            width = 2
            height = 1
            row = 0
            column = 0
            puzzle = Puzzle(Tessellation.SOKOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert not is_on_board_1d(g.neighbor(index, Direction.LEFT), width, height)
            assert g.neighbor(index, Direction.RIGHT) == index_1d(1, 0, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.UP), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.DOWN), width, height)
            assert g.neighbor(index, Direction.NORTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_EAST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_EAST) == Config.NO_POS

        def test_generated_boarD_2x1_right(self):
            width = 2
            height = 1
            row = 0
            column = 1
            puzzle = Puzzle(Tessellation.SOKOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert g.neighbor(index, Direction.LEFT) == index_1d(0, 0, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.UP), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.DOWN), width, height)
            assert g.neighbor(index, Direction.NORTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_EAST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_EAST) == Config.NO_POS

        def test_generated_1x2_top(self):
            width = 1
            height = 2
            row = 0
            column = 0
            puzzle = Puzzle(Tessellation.SOKOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert not is_on_board_1d(g.neighbor(index, Direction.LEFT), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.UP), width, height)
            assert g.neighbor(index, Direction.DOWN) == index_1d(0, 1, width)
            assert g.neighbor(index, Direction.NORTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_EAST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_EAST) == Config.NO_POS

        def test_generated_1x2_bottom(self):
            width = 1
            height = 2
            row = 1
            column = 0
            puzzle = Puzzle(Tessellation.SOKOBAN, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)

            assert not is_on_board_1d(g.neighbor(index, Direction.LEFT), width, height)
            assert not is_on_board_1d(g.neighbor(index, Direction.RIGHT), width, height)
            assert g.neighbor(index, Direction.UP) == index_1d(0, 0, width)
            assert not is_on_board_1d(g.neighbor(index, Direction.DOWN), width, height)
            assert g.neighbor(index, Direction.NORTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_WEST) == Config.NO_POS
            assert g.neighbor(index, Direction.NORTH_EAST) == Config.NO_POS
            assert g.neighbor(index, Direction.SOUTH_EAST) == Config.NO_POS


