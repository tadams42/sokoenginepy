import copy

import pytest

from factories import BoardCellFactory
from sokoenginepy import BoardCell, SokoengineError, settings


class DescribeBoardCell:
    class Describe_is_pusher_chr:

        def it_correctly_categorizes(self):
            assert BoardCell.is_pusher_chr(BoardCell.Characters.PUSHER)
            assert BoardCell.is_pusher_chr(BoardCell.Characters.ALT_PUSHER1)
            assert BoardCell.is_pusher_chr(BoardCell.Characters.ALT_PUSHER2)
            assert BoardCell.is_pusher_chr(BoardCell.Characters.PUSHER_ON_GOAL)
            assert BoardCell.is_pusher_chr(BoardCell.Characters.ALT_PUSHER_ON_GOAL1)
            assert BoardCell.is_pusher_chr(BoardCell.Characters.ALT_PUSHER_ON_GOAL2)

    class Describe_is_box_chr:

        def it_correctly_categorizes(self):
            assert BoardCell.is_box_chr(BoardCell.Characters.BOX)
            assert BoardCell.is_box_chr(BoardCell.Characters.ALT_BOX1)
            assert BoardCell.is_box_chr(BoardCell.Characters.BOX_ON_GOAL)
            assert BoardCell.is_box_chr(BoardCell.Characters.ALT_BOX_ON_GOAL1)

    class Describe_is_goal_chr:

        def it_correctly_categorizes(self):
            assert BoardCell.is_goal_chr(BoardCell.Characters.GOAL)
            assert BoardCell.is_goal_chr(BoardCell.Characters.ALT_GOAL1)
            assert BoardCell.is_goal_chr(BoardCell.Characters.PUSHER_ON_GOAL)
            assert BoardCell.is_goal_chr(BoardCell.Characters.ALT_PUSHER_ON_GOAL1)
            assert BoardCell.is_goal_chr(BoardCell.Characters.ALT_PUSHER_ON_GOAL2)
            assert BoardCell.is_goal_chr(BoardCell.Characters.BOX_ON_GOAL)
            assert BoardCell.is_goal_chr(BoardCell.Characters.ALT_BOX_ON_GOAL1)

    class Describe_is_empty_floor_chr:

        def it_correctly_categorizes(self):
            assert BoardCell.is_empty_floor_chr(BoardCell.Characters.FLOOR)
            assert BoardCell.is_empty_floor_chr(BoardCell.Characters.VISIBLE_FLOOR)
            assert BoardCell.is_empty_floor_chr(BoardCell.Characters.ALT_VISIBLE_FLOOR1)

    class Describe_is_wall_chr:

        def it_correctly_categorizes(self):
            assert BoardCell.is_wall_chr(BoardCell.Characters.WALL)

    class Describe_init:

        def it_sets_all_attributes(self):
            board_cell = BoardCellFactory(
                character=BoardCell.Characters.PUSHER
            )

            assert not board_cell._has_box
            assert board_cell._has_pusher
            assert not board_cell._has_goal
            assert not board_cell._is_wall
            assert not board_cell.is_in_playable_area
            assert not board_cell.is_deadlock

        def it_createst_empty_floor_by_default(self):
            board_cell = BoardCell()
            assert board_cell.is_empty_floor

        def it_initializes_secondary_flags_to_false_by_default(self):
            board_cell = BoardCell()
            assert not board_cell.is_in_playable_area
            assert not board_cell.is_deadlock

            board_cell = BoardCellFactory(
                character=BoardCell.Characters.PUSHER
            )
            assert not board_cell.is_in_playable_area
            assert not board_cell.is_deadlock

        def it_raises_on_illegal_character(self):
            with pytest.raises(SokoengineError):
                BoardCell(character="4")

    class Describe_equality_comparisson:

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

        def test_setter_replaces_box_but_not_goal_if_setting_to_true(
            self, board_cell
        ):
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

        def test_setter_replaces_box_with_wall_if_setting_to_true(
            self, board_cell
        ):
            board_cell.has_box = True
            board_cell.is_wall = True
            assert not board_cell.has_box

        def test_setter_replaces_pusher_with_wall_if_setting_to_true(
            self, board_cell
        ):
            board_cell.has_pusher = True
            board_cell.is_wall = True
            assert not board_cell.has_pusher

        def test_setter_replaces_goal_with_wall_if_setting_to_true(
            self, board_cell
        ):
            board_cell.has_goal = True
            board_cell.is_wall = True
            assert not board_cell.has_goal

        def test_setter_doesnt_change_secondary_flags(self, board_cell):
            board_cell.is_deadlock = True
            board_cell.is_in_playable_area = True
            board_cell.is_wall = True
            assert board_cell.is_deadlock
            assert board_cell.is_in_playable_area

    class Describe_switch_box_and_goal:

        def it_switches_box_for_goal(self, board_cell):
            board_cell.has_box = True
            board_cell.has_goal = False
            board_cell.switch_box_and_goal()
            assert not board_cell.has_box
            assert board_cell.has_goal

        def it_switches_goal_for_box(self, board_cell):
            board_cell.has_box = False
            board_cell.has_goal = True
            board_cell.switch_box_and_goal()
            assert board_cell.has_box
            assert not board_cell.has_goal

        def it_doesnt_switch_goal_if_pusher_is_standing_on_it(self, board_cell):
            board_cell.has_goal = True
            board_cell.has_pusher = True
            board_cell.switch_box_and_goal()
            assert board_cell.has_goal
            assert board_cell.has_pusher
            assert not board_cell.has_box

        def it_doesnt_change_secondary_flags(self, board_cell):
            board_cell.has_box = True
            board_cell.is_deadlock = True
            board_cell.is_in_playable_area = True
            board_cell.switch_box_and_goal()
            assert board_cell.is_in_playable_area
            assert board_cell.is_deadlock

        def it_fails_silently_if_no_switch_can_be_performed(self, board_cell):
            board_cell.is_wall = True
            board_cell.switch_box_and_goal()
            assert board_cell.is_wall
            assert not board_cell.has_goal
            assert not board_cell.has_box

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
            assert str(board_cell) == BoardCell.Characters.PUSHER.value
            board_cell.clear()
            board_cell.has_pusher = True
            board_cell.has_goal = True
            assert str(board_cell) == BoardCell.Characters.PUSHER_ON_GOAL.value
            board_cell.clear()
            board_cell.has_box = True
            assert str(board_cell) == BoardCell.Characters.BOX.value
            board_cell.clear()
            board_cell.has_box = True
            board_cell.has_goal = True
            assert str(board_cell) == BoardCell.Characters.BOX_ON_GOAL.value
            board_cell.clear()
            board_cell.has_goal = True
            assert str(board_cell) == BoardCell.Characters.GOAL.value
            board_cell.clear()
            board_cell.is_wall = True
            assert str(board_cell) == BoardCell.Characters.WALL.value

            board_cell.clear()

            settings.OUTPUT_BOARDS_WITH_VISIBLE_FLOORS = False
            assert str(board_cell) == BoardCell.Characters.FLOOR.value

            settings.OUTPUT_BOARDS_WITH_VISIBLE_FLOORS = True
            assert str(board_cell) == BoardCell.Characters.VISIBLE_FLOOR.value
