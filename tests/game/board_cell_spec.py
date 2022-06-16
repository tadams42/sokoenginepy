import copy

import pytest

from sokoenginepy.game import BoardCell
from sokoenginepy.io import Puzzle


@pytest.fixture
def board_cell():
    return BoardCell()


class DescribeBoardCell:
    class Describe_init:
        def it_creates_empty_floor_by_default(self):
            board_cell = BoardCell()
            assert board_cell.is_empty_floor

        def it_initializes_secondary_flags_to_false_by_default(self):
            board_cell = BoardCell()
            assert not board_cell.is_in_playable_area
            assert not board_cell.is_deadlock

            board_cell: BoardCell = BoardCell(character=Puzzle.PUSHER)
            assert not board_cell.is_in_playable_area
            assert not board_cell.is_deadlock

        def it_raises_on_illegal_character(self):
            with pytest.raises(ValueError):
                BoardCell(character="4")
            with pytest.raises(ValueError):
                BoardCell(character="  ")
            with pytest.raises(ValueError):
                BoardCell(character=None)

    class Describe_equality_comparison:
        def it_doesnt_compare_secondary_flags(self, board_cell):
            board_cell2 = copy.copy(board_cell)
            assert board_cell == board_cell2
            board_cell.is_deadlock = True
            board_cell2.is_deadlock = False
            board_cell.is_in_playable_area = True
            board_cell2.is_in_playable_area = False
            assert board_cell == board_cell2

    class Describe_has_pusher:
        def test_setter_puts_or_removes_pusher_on_cell(self, board_cell):
            board_cell.has_pusher = False
            assert not board_cell.has_pusher
            board_cell.has_pusher = True
            assert board_cell.has_pusher
            board_cell.has_pusher = False
            assert not board_cell.has_pusher

        def test_setter_replaces_box_if_setting_to_true(self, board_cell):
            board_cell.has_box = True
            board_cell.has_pusher = True
            assert not board_cell.has_box

        def test_setter_replaces_box_but_not_goal_if_setting_to_true(self, board_cell):
            board_cell.has_goal = True
            board_cell.has_box = True
            board_cell.has_pusher = True
            assert not board_cell.has_box
            assert board_cell.has_goal

        def test_setter_replaces_wall_if_setting_to_true(self, board_cell):
            board_cell.is_wall = True
            board_cell.has_pusher = True
            assert not board_cell.is_wall
            assert board_cell.has_pusher

        def test_setter_doesnt_change_secondary_flags(self, board_cell):
            board_cell.is_deadlock = True
            board_cell.is_in_playable_area = True
            board_cell.has_pusher = True
            assert board_cell.is_deadlock
            assert board_cell.is_in_playable_area

    class Describe_has_box:
        def test_setter_puts_or_removes_box_on_cell(self, board_cell):
            board_cell.has_box = False
            assert not board_cell.has_box
            board_cell.has_box = True
            assert board_cell.has_box
            board_cell.has_box = False
            assert not board_cell.has_box

        def test_setter_replaces_pusher_if_setting_to_true(self, board_cell):
            board_cell.has_pusher = True
            board_cell.has_box = True
            assert not board_cell.has_pusher

        def test_setter_replaces_pusher_but_not_goal_if_setting_to_true(
            self, board_cell
        ):
            board_cell.has_goal = True
            board_cell.has_pusher = True
            board_cell.has_box = True
            assert not board_cell.has_pusher
            assert board_cell.has_goal

        def test_setter_replaces_wall_if_setting_to_true(self, board_cell):
            board_cell.is_wall = True
            board_cell.has_box = True
            assert not board_cell.is_wall
            assert board_cell.has_box

        def test_setter_doesnt_change_secondary_flags(self, board_cell):
            board_cell.is_deadlock = True
            board_cell.is_in_playable_area = True
            board_cell.has_box = True
            assert board_cell.is_deadlock
            assert board_cell.is_in_playable_area

    class Describe_has_goal:
        def test_setter_puts_or_removes_goal_on_cell(self, board_cell):
            board_cell.has_goal = False
            assert not board_cell.has_goal
            board_cell.has_goal = True
            assert board_cell.has_goal
            board_cell.has_goal = False
            assert not board_cell.has_goal

        def test_setter_adds_or_removes_goal_under_pusher(self, board_cell):
            board_cell.has_pusher = True
            board_cell.has_goal = True
            assert board_cell.has_pusher
            assert board_cell.has_goal
            board_cell.has_goal = False
            assert board_cell.has_pusher
            assert not board_cell.has_goal

        def test_setter_adds_or_removes_goal_under_box(self, board_cell):
            board_cell.has_box = True
            board_cell.has_goal = True
            assert board_cell.has_box
            assert board_cell.has_goal
            board_cell.has_goal = False
            assert board_cell.has_box
            assert not board_cell.has_goal

        def test_setter_replaces_wall_if_setting_to_true(self, board_cell):
            board_cell.is_wall = True
            board_cell.has_goal = True
            assert not board_cell.is_wall
            assert board_cell.has_goal

        def test_setter_doesnt_change_secondary_flags(self, board_cell):
            board_cell.is_deadlock = True
            board_cell.is_in_playable_area = True
            board_cell.has_goal = True
            assert board_cell.is_deadlock
            assert board_cell.is_in_playable_area

    class Describe_is_wall:
        def test_setter_puts_wall_on_cell_if_setting_to_true(self, board_cell):
            board_cell.is_wall = False
            assert not board_cell.is_wall
            board_cell.is_wall = True
            assert board_cell.is_wall
            board_cell.is_wall = False
            assert not board_cell.is_wall

        def test_setter_replaces_box_with_wall_if_setting_to_true(self, board_cell):
            board_cell.has_box = True
            board_cell.is_wall = True
            assert not board_cell.has_box

        def test_setter_replaces_pusher_with_wall_if_setting_to_true(self, board_cell):
            board_cell.has_pusher = True
            board_cell.is_wall = True
            assert not board_cell.has_pusher

        def test_setter_replaces_goal_with_wall_if_setting_to_true(self, board_cell):
            board_cell.has_goal = True
            board_cell.is_wall = True
            assert not board_cell.has_goal

        def test_setter_doesnt_change_secondary_flags(self, board_cell):
            board_cell.is_deadlock = True
            board_cell.is_in_playable_area = True
            board_cell.is_wall = True
            assert board_cell.is_deadlock
            assert board_cell.is_in_playable_area

    class Describe_can_put_pusher_or_box:
        def it_returns_true_for_empty_floor(self, board_cell):
            assert board_cell.can_put_pusher_or_box

        def it_returns_true_for_empty_goal(self, board_cell):
            board_cell.has_goal = True
            assert board_cell.can_put_pusher_or_box

        def it_returns_false_for_wall(self, board_cell):
            board_cell.is_wall = True
            assert not board_cell.can_put_pusher_or_box

        def it_returns_false_for_box(self, board_cell):
            board_cell.has_box = True
            assert not board_cell.can_put_pusher_or_box

        def it_returns_false_for_pusher(self, board_cell):
            board_cell.has_pusher = True
            assert not board_cell.can_put_pusher_or_box

    class Describe_str:
        def it_converts_board_cell_to_printable_character(self, board_cell):
            board_cell.clear()
            board_cell.has_pusher = True
            assert str(board_cell) == Puzzle.PUSHER
            board_cell.clear()
            board_cell.has_pusher = True
            board_cell.has_goal = True
            assert str(board_cell) == Puzzle.PUSHER_ON_GOAL
            board_cell.clear()
            board_cell.has_box = True
            assert str(board_cell) == Puzzle.BOX
            board_cell.clear()
            board_cell.has_box = True
            board_cell.has_goal = True
            assert str(board_cell) == Puzzle.BOX_ON_GOAL
            board_cell.clear()
            board_cell.has_goal = True
            assert str(board_cell) == Puzzle.GOAL
            board_cell.clear()
            board_cell.is_wall = True
            assert str(board_cell) == Puzzle.WALL

            board_cell.clear()

            assert str(board_cell) == Puzzle.FLOOR

            assert board_cell.to_str(use_visible_floor=True) == Puzzle.VISIBLE_FLOOR
