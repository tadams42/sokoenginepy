import pytest

from sokoenginepy import io
from sokoenginepy.game import Tessellation
from sokoenginepy.io import Puzzle, SokobanPuzzle


class DescribePuzzle:
    def it_correctly_categorizes_pusher_characters(self):
        assert Puzzle.is_pusher(Puzzle.PUSHER)
        assert Puzzle.is_pusher(Puzzle.ALT_PUSHER1)
        assert Puzzle.is_pusher(Puzzle.ALT_PUSHER2)
        assert Puzzle.is_pusher(Puzzle.PUSHER_ON_GOAL)
        assert Puzzle.is_pusher(Puzzle.ALT_PUSHER_ON_GOAL1)
        assert Puzzle.is_pusher(Puzzle.ALT_PUSHER_ON_GOAL2)

    def it_provides_factory_for_subtypes(self):
        for tessellation in Tessellation.__members__.values():
            klass = getattr(io, f"{tessellation.name.capitalize()}Puzzle")

            obj = Puzzle.instance_from(tessellation, width=2, height=2)
            assert isinstance(obj, klass)

            obj = Puzzle.instance_from(tessellation, board="###")
            assert isinstance(obj, klass)

    def test_init_rises_on_invalid_board_sizes(self):
        # It is OK to test for Sokoban only, all subtypes call Puzzle.__init__ anyway
        with pytest.raises(ValueError):
            SokobanPuzzle(width=-1, height=42)

        with pytest.raises(ValueError):
            SokobanPuzzle(width=42, height=-1)

        with pytest.raises(ValueError):
            SokobanPuzzle(width=-1, height=-1)

    def test_getitem_rises_on_invalid_board_sizes(self):
        # It is OK to test for Sokoban only, all subtypes user super() anyway
        puzzle = SokobanPuzzle(width=5, height=5)

        with pytest.raises(IndexError):
            puzzle[-1]

    def test_setitem_rises_on_invalid_board_sizes(self):
        # It is OK to test for Sokoban only, all subtypes user super() anyway
        puzzle = SokobanPuzzle(width=5, height=5)

        with pytest.raises(IndexError):
            puzzle[-1] = " "

    def test_resize_rises_on_invalid_board_sizes(self):
        # It is OK to test for Sokoban only, all subtypes user super() anyway
        SokobanPuzzle(width=5, height=5)
        puzzle = SokobanPuzzle(width=5, height=5)

        with pytest.raises(ValueError):
            puzzle.resize(-1, 5)

        with pytest.raises(ValueError):
            puzzle.resize(5, -1)

    def test_resize_and_center_rises_on_invalid_board_sizes(self):
        # It is OK to test for Sokoban only, all subtypes user super() anyway
        SokobanPuzzle(width=5, height=5)
        puzzle = SokobanPuzzle(width=5, height=5)

        with pytest.raises(ValueError):
            puzzle.resize_and_center(-1, 5)

        with pytest.raises(ValueError):
            puzzle.resize_and_center(5, -1)

    def it_correctly_categorizes_box_characters(self):
        assert Puzzle.is_box(Puzzle.BOX)
        assert Puzzle.is_box(Puzzle.ALT_BOX1)
        assert Puzzle.is_box(Puzzle.BOX_ON_GOAL)
        assert Puzzle.is_box(Puzzle.ALT_BOX_ON_GOAL1)

    def it_correctly_categorizes_goal_characters(self):
        assert Puzzle.is_goal(Puzzle.GOAL)
        assert Puzzle.is_goal(Puzzle.ALT_GOAL1)
        assert Puzzle.is_goal(Puzzle.PUSHER_ON_GOAL)
        assert Puzzle.is_goal(Puzzle.ALT_PUSHER_ON_GOAL1)
        assert Puzzle.is_goal(Puzzle.ALT_PUSHER_ON_GOAL2)
        assert Puzzle.is_goal(Puzzle.BOX_ON_GOAL)
        assert Puzzle.is_goal(Puzzle.ALT_BOX_ON_GOAL1)

    def it_correctly_categorizes_empty_floor_characters(self):
        assert Puzzle.is_empty_floor(Puzzle.FLOOR)
        assert Puzzle.is_empty_floor(Puzzle.VISIBLE_FLOOR)
        assert Puzzle.is_empty_floor(Puzzle.ALT_VISIBLE_FLOOR1)

    def it_correctly_categorizes_wall_characters(self):
        assert Puzzle.is_wall(Puzzle.WALL)

    def it_correctly_categorizes_border_characters(self):
        assert Puzzle.is_border_element(Puzzle.WALL)
        assert Puzzle.is_border_element(Puzzle.BOX_ON_GOAL)
        assert Puzzle.is_border_element(Puzzle.ALT_BOX_ON_GOAL1)

    def it_can_categorize_any_character(self):
        assert Puzzle.is_puzzle_element(Puzzle.WALL)
        assert not Puzzle.is_puzzle_element("Z")

    class describe_is_board:
        def it_recognizes_board_string(self):
            assert Puzzle.is_board("0123456789\n\t bB$*p_pmM@+#_-|")

        def it_fails_on_illegal_characters(self):
            assert not Puzzle.is_board("ZOMG!")

        def it_fails_on_purely_numeric_strings(self):
            assert not Puzzle.is_board("42")

        def it_fails_on_blank_strings(self):
            assert not Puzzle.is_board("")
            assert not Puzzle.is_board("    ")
            assert not Puzzle.is_board("   \r\n \t")

    class describe_is_sokoban_plus:
        def it_recognizes_sokoban_plus_strings(self):
            assert Puzzle.is_sokoban_plus("0 1 2 3 4 5 6 99")

        def it_fails_on_blank_strings(self):
            assert not Puzzle.is_sokoban_plus("")
            assert not Puzzle.is_sokoban_plus("    ")
            assert not Puzzle.is_sokoban_plus("   \r\n \t")
