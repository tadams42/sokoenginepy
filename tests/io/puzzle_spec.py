import pytest
from sokoenginepy.io import Puzzle


class DescribePuzzle:
    class Describe_is_pusher_chr:
        def it_correctly_categorizes(self):
            assert Puzzle.is_pusher(Puzzle.PUSHER)
            assert Puzzle.is_pusher(Puzzle.ALT_PUSHER1)
            assert Puzzle.is_pusher(Puzzle.ALT_PUSHER2)
            assert Puzzle.is_pusher(Puzzle.PUSHER_ON_GOAL)
            assert Puzzle.is_pusher(Puzzle.ALT_PUSHER_ON_GOAL1)
            assert Puzzle.is_pusher(Puzzle.ALT_PUSHER_ON_GOAL2)

    class Describe_is_box_chr:
        def it_correctly_categorizes(self):
            assert Puzzle.is_box(Puzzle.BOX)
            assert Puzzle.is_box(Puzzle.ALT_BOX1)
            assert Puzzle.is_box(Puzzle.BOX_ON_GOAL)
            assert Puzzle.is_box(Puzzle.ALT_BOX_ON_GOAL1)

    class Describe_is_goal_chr:
        def it_correctly_categorizes(self):
            assert Puzzle.is_goal(Puzzle.GOAL)
            assert Puzzle.is_goal(Puzzle.ALT_GOAL1)
            assert Puzzle.is_goal(Puzzle.PUSHER_ON_GOAL)
            assert Puzzle.is_goal(Puzzle.ALT_PUSHER_ON_GOAL1)
            assert Puzzle.is_goal(Puzzle.ALT_PUSHER_ON_GOAL2)
            assert Puzzle.is_goal(Puzzle.BOX_ON_GOAL)
            assert Puzzle.is_goal(Puzzle.ALT_BOX_ON_GOAL1)

    class Describe_is_empty_floor_chr:
        def it_correctly_categorizes(self):
            assert Puzzle.is_empty_floor(Puzzle.FLOOR)
            assert Puzzle.is_empty_floor(Puzzle.VISIBLE_FLOOR)
            assert Puzzle.is_empty_floor(Puzzle.ALT_VISIBLE_FLOOR1)

    class Describe_is_wall_chr:
        def it_correctly_categorizes(self):
            assert Puzzle.is_wall(Puzzle.WALL)

    class describe_is_board:
        input = "0123456789\n\t bB$*p_pmM@+#_-|"

        def it_recognizes_board_string(self):
            assert Puzzle.is_board(self.input)

        def it_fails_on_illegal_characters(self):
            assert not Puzzle.is_board(self.input + "z")

        def it_fails_on_numeric_string(self):
            assert not Puzzle.is_board("42")

        def it_fails_on_blank_string(self):
            assert not Puzzle.is_board("")
            assert not Puzzle.is_board("    ")
            assert not Puzzle.is_board("   \r\n ")
