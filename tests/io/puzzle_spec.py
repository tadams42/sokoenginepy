import textwrap

import pytest

from sokoenginepy import BoardGraph, Puzzle, Tessellation


class DescribePuzzle:
    def test_init_rises_on_invalid_board_sizes(self):
        for tessellation in Tessellation.__members__.values():
            with pytest.raises(ValueError):
                Puzzle(tessellation, width=-1, height=42)

            with pytest.raises(ValueError):
                Puzzle(tessellation, width=42, height=-1)

            with pytest.raises(ValueError):
                Puzzle(tessellation, width=-1, height=-1)

    def test_getitem_rises_on_invalid_board_sizes(self):
        for tessellation in Tessellation.__members__.values():
            puzzle = Puzzle(tessellation, width=5, height=5)

            with pytest.raises(IndexError):
                puzzle[-1]

    def test_setitem_rises_on_invalid_board_sizes(self):
        for tessellation in Tessellation.__members__.values():
            puzzle = Puzzle(tessellation, width=5, height=5)

            with pytest.raises(IndexError):
                puzzle[-1] = " "

    def test_resize_rises_on_invalid_board_sizes(self):
        for tessellation in Tessellation.__members__.values():
            puzzle = Puzzle(tessellation, width=5, height=5)

            with pytest.raises(ValueError):
                puzzle.resize(-1, 5)

            with pytest.raises(ValueError):
                puzzle.resize(5, -1)

    def test_resize_and_center_rises_on_invalid_board_sizes(self):
        for tessellation in Tessellation.__members__.values():
            puzzle = Puzzle(tessellation, width=5, height=5)

            with pytest.raises(ValueError):
                puzzle.resize_and_center(-1, 5)

            with pytest.raises(ValueError):
                puzzle.resize_and_center(5, -1)

    def it_recognizes_alternative_characters_in_board_representation(self):
        board_str = textwrap.dedent(
            """
            #######
            #pm PM#
            #   Bb#
            #-_obb#
            #######
            """
        )
        preserved = textwrap.dedent(
            """
            #######
            #pm PM#
            #   Bb#
            #  obb#
            #######
            """
        )
        converted = textwrap.dedent(
            """
            #######
            #@@ ++#
            #   *$#
            #  .$$#
            #######
            """
        )
        puzzle = Puzzle(Tessellation.SOKOBAN, board=board_str)
        graph = BoardGraph(puzzle)

        assert str(puzzle) == preserved.lstrip("\n").rstrip()
        assert str(graph) == converted.lstrip("\n").rstrip()

    class describe_has_sokoban_plus:
        def it_returns_true_when_either_boxorder_or_goalorder_is_not_blank(self):
            s = Puzzle(Tessellation.SOKOBAN, 5, 5)

            s.boxorder = "1 2 3"
            assert s.has_sokoban_plus

            s.goalorder = "1 2 3"
            assert s.has_sokoban_plus

            s.boxorder = ""
            assert s.has_sokoban_plus

            s.goalorder = ""
            assert not s.has_sokoban_plus
