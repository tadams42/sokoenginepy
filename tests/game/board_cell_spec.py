import pytest
import copy
from hamcrest import assert_that, equal_to
from factories import BoardCellFactory
from sokoenginepy import BoardCell, SokoengineError
from sokoenginepy.io import BoardEncodingCharacters


class DescribeBoardCell(object):

    class Describe_init(object):
        def test_it_sets_all_attributes(self):
            board_cell = BoardCellFactory(chr = BoardEncodingCharacters.PUSHER)

            assert_that(board_cell._has_box, equal_to(False))
            assert_that(board_cell._has_pusher, equal_to(True))
            assert_that(board_cell._has_goal, equal_to(False))
            assert_that(board_cell._is_wall, equal_to(False))
            assert_that(board_cell.is_in_playable_area, equal_to(False))
            assert_that(board_cell.is_deadlock, equal_to(False))

        def test_it_createst_empty_floor_by_default(self):
            board_cell = BoardCell()
            assert_that(board_cell.is_empty_floor, equal_to(True))

        def test_it_initializes_secondary_flags_to_false_by_default(self):
            board_cell = BoardCell()
            assert_that(board_cell.is_in_playable_area, equal_to(False))
            assert_that(board_cell.is_deadlock, equal_to(False))

            board_cell = BoardCellFactory(chr = BoardEncodingCharacters.PUSHER)
            assert_that(board_cell.is_in_playable_area, equal_to(False))
            assert_that(board_cell.is_deadlock, equal_to(False))

        def test_it_raises_on_illegal_character(self):
            with pytest.raises(SokoengineError):
                BoardCell(chr="4")


    class Describe_equality_comparisson(object):
        def test_it_doesnt_compare_secondary_flags(self, board_cell):
            board_cell2 = copy.copy(board_cell)
            assert_that(board_cell, equal_to(board_cell2))
            board_cell.is_deadlock = True
            board_cell2.is_deadlock = False
            board_cell.is_in_playable_area = True
            board_cell2.is_in_playable_area = False
            assert_that(board_cell, equal_to(board_cell2))


    class Describe_has_pusher(object):
        def test_setter_puts_or_removes_pusher_on_cell(self, board_cell):
            board_cell.has_pusher = False
            assert_that(board_cell.has_pusher, equal_to(False))
            board_cell.has_pusher = True
            assert_that(board_cell.has_pusher, equal_to(True))
            board_cell.has_pusher = False
            assert_that(board_cell.has_pusher, equal_to(False))

        def test_setter_replaces_box_if_setting_to_true(self, board_cell):
            board_cell.has_box = True
            board_cell.has_pusher = True
            assert_that(board_cell.has_box, equal_to(False))

        def test_setter_replaces_box_but_not_goal_if_setting_to_true(self, board_cell):
            board_cell.has_goal = True
            board_cell.has_box = True
            board_cell.has_pusher = True
            assert_that(board_cell.has_box, equal_to(False))
            assert_that(board_cell.has_goal, equal_to(True))

        def test_setter_replaces_wall_if_setting_to_true(self, board_cell):
            board_cell.is_wall = True
            board_cell.has_pusher = True
            assert_that(board_cell.is_wall, equal_to(False))
            assert_that(board_cell.has_pusher, equal_to(True))

        def test_setter_doesnt_change_secondary_flags(self, board_cell):
            board_cell.is_deadlock = True
            board_cell.is_in_playable_area = True
            board_cell.has_pusher = True
            assert_that(board_cell.is_deadlock, equal_to(True))
            assert_that(board_cell.is_in_playable_area, equal_to(True))


    class Describe_has_box(object):
        def test_setter_puts_or_removes_box_on_cell(self, board_cell):
            board_cell.has_box = False
            assert_that(board_cell.has_box, equal_to(False))
            board_cell.has_box = True
            assert_that(board_cell.has_box, equal_to(True))
            board_cell.has_box = False
            assert_that(board_cell.has_box, equal_to(False))

        def test_setter_replaces_pusher_if_setting_to_true(self, board_cell):
            board_cell.has_pusher = True
            board_cell.has_box = True
            assert_that(board_cell.has_pusher, equal_to(False))

        def test_setter_replaces_pusher_but_not_goal_if_setting_to_true(self, board_cell):
            board_cell.has_goal = True
            board_cell.has_pusher = True
            board_cell.has_box = True
            assert_that(board_cell.has_pusher, equal_to(False))
            assert_that(board_cell.has_goal, equal_to(True))

        def test_setter_replaces_wall_if_setting_to_true(self, board_cell):
            board_cell.is_wall = True
            board_cell.has_box = True
            assert_that(board_cell.is_wall, equal_to(False))
            assert_that(board_cell.has_box, equal_to(True))

        def test_setter_doesnt_change_secondary_flags(self, board_cell):
            board_cell.is_deadlock = True
            board_cell.is_in_playable_area = True
            board_cell.has_box = True
            assert_that(board_cell.is_deadlock, equal_to(True))
            assert_that(board_cell.is_in_playable_area, equal_to(True))


    class Describe_has_goal(object):
        def test_setter_puts_or_removes_goal_on_cell(self, board_cell):
            board_cell.has_goal = False
            assert_that(board_cell.has_goal, equal_to(False))
            board_cell.has_goal = True
            assert_that(board_cell.has_goal, equal_to(True))
            board_cell.has_goal = False
            assert_that(board_cell.has_goal, equal_to(False))

        def test_setter_adds_or_removes_goal_under_pusher(self, board_cell):
            board_cell.has_pusher = True
            board_cell.has_goal = True
            assert_that(board_cell.has_pusher, equal_to(True))
            assert_that(board_cell.has_goal, equal_to(True))
            board_cell.has_goal = False
            assert_that(board_cell.has_pusher, equal_to(True))
            assert_that(board_cell.has_goal, equal_to(False))

        def test_setter_adds_or_removes_goal_under_box(self, board_cell):
            board_cell.has_box = True
            board_cell.has_goal = True
            assert_that(board_cell.has_box, equal_to(True))
            assert_that(board_cell.has_goal, equal_to(True))
            board_cell.has_goal = False
            assert_that(board_cell.has_box, equal_to(True))
            assert_that(board_cell.has_goal, equal_to(False))

        def test_setter_replaces_wall_if_setting_to_true(self, board_cell):
            board_cell.is_wall = True
            board_cell.has_goal = True
            assert_that(board_cell.is_wall, equal_to(False))
            assert_that(board_cell.has_goal, equal_to(True))

        def test_setter_doesnt_change_secondary_flags(self, board_cell):
            board_cell.is_deadlock = True
            board_cell.is_in_playable_area = True
            board_cell.has_goal = True
            assert_that(board_cell.is_deadlock, equal_to(True))
            assert_that(board_cell.is_in_playable_area, equal_to(True))


    class Describe_is_wall(object):
        def test_setter_puts_wall_on_cell_if_setting_to_true(self, board_cell):
            board_cell.is_wall = False
            assert_that(board_cell.is_wall, equal_to(False))
            board_cell.is_wall = True
            assert_that(board_cell.is_wall, equal_to(True))
            board_cell.is_wall = False
            assert_that(board_cell.is_wall, equal_to(False))

        def test_setter_replaces_box_with_wall_if_setting_to_true(self, board_cell):
            board_cell.has_box = True
            board_cell.is_wall = True
            assert_that(board_cell.has_box, equal_to(False))

        def test_setter_replaces_pusher_with_wall_if_setting_to_true(self, board_cell):
            board_cell.has_pusher = True
            board_cell.is_wall = True
            assert_that(board_cell.has_pusher, equal_to(False))

        def test_setter_replaces_goal_with_wall_if_setting_to_true(self, board_cell):
            board_cell.has_goal = True
            board_cell.is_wall = True
            assert_that(board_cell.has_goal, equal_to(False))

        def test_setter_doesnt_change_secondary_flags(self, board_cell):
            board_cell.is_deadlock = True
            board_cell.is_in_playable_area = True
            board_cell.is_wall = True
            assert_that(board_cell.is_deadlock, equal_to(True))
            assert_that(board_cell.is_in_playable_area, equal_to(True))


    class Describe_switch_box_and_goal(object):
        def test_it_switches_box_for_goal(self, board_cell):
            board_cell.has_box = True
            board_cell.has_goal = False
            board_cell.switch_box_and_goal()
            assert_that(board_cell.has_box, equal_to(False))
            assert_that(board_cell.has_goal, equal_to(True))

        def test_it_switches_goal_for_box(self, board_cell):
            board_cell.has_box = False
            board_cell.has_goal = True
            board_cell.switch_box_and_goal()
            assert_that(board_cell.has_box, equal_to(True))
            assert_that(board_cell.has_goal, equal_to(False))

        def test_it_doesnt_switch_goal_if_pusher_is_standing_on_it(self, board_cell):
            board_cell.has_goal = True
            board_cell.has_pusher = True
            board_cell.switch_box_and_goal()
            assert_that(board_cell.has_goal, equal_to(True))
            assert_that(board_cell.has_pusher, equal_to(True))
            assert_that(board_cell.has_box, equal_to(False))

        def test_it_doesnt_change_secondary_flags(self, board_cell):
            board_cell.has_box = True
            board_cell.is_deadlock = True
            board_cell.is_in_playable_area = True
            board_cell.switch_box_and_goal()
            assert_that(board_cell.is_in_playable_area, equal_to(True))
            assert_that(board_cell.is_deadlock, equal_to(True))

        def test_it_fails_silently_if_no_switch_can_be_performed(self, board_cell):
            board_cell.is_wall = True
            board_cell.switch_box_and_goal()
            assert_that(board_cell.is_wall, equal_to(True))
            assert_that(board_cell.has_goal, equal_to(False))
            assert_that(board_cell.has_box, equal_to(False))


    class Describe_can_put_pusher_or_box(object):
        def test_it_returns_true_for_empty_floor(self, board_cell):
            assert_that(board_cell.can_put_pusher_or_box, equal_to(True))

        def test_it_returns_true_for_empty_goal(self, board_cell):
            board_cell.has_goal = True
            assert_that(board_cell.can_put_pusher_or_box, equal_to(True))

        def test_it_returns_false_for_wall(self, board_cell):
            board_cell.is_wall = True
            assert_that(board_cell.can_put_pusher_or_box, equal_to(False))

        def test_it_returns_false_for_box(self, board_cell):
            board_cell.has_box = True
            assert_that(board_cell.can_put_pusher_or_box, equal_to(False))

        def test_it_returns_false_for_pusher(self, board_cell):
            board_cell.has_pusher = True
            assert_that(board_cell.can_put_pusher_or_box, equal_to(False))


    class Describe_to_s(object):
        def test_converts_board_cell_to_printable_character(self, board_cell):
            board_cell.clear()
            board_cell.has_pusher = True
            assert_that(
                board_cell.to_s(),
                equal_to(BoardEncodingCharacters.PUSHER.value)
            )
            board_cell.clear()
            board_cell.has_pusher = True
            board_cell.has_goal = True
            assert_that(
                board_cell.to_s(),
                equal_to(BoardEncodingCharacters.PUSHER_ON_GOAL.value)
            )
            board_cell.clear()
            board_cell.has_box = True
            assert_that(
                board_cell.to_s(),
                equal_to(BoardEncodingCharacters.BOX.value)
            )
            board_cell.clear()
            board_cell.has_box = True
            board_cell.has_goal = True
            assert_that(
                board_cell.to_s(),
                equal_to(BoardEncodingCharacters.BOX_ON_GOAL.value)
            )
            board_cell.clear()
            board_cell.has_goal = True
            assert_that(
                board_cell.to_s(),
                equal_to(BoardEncodingCharacters.GOAL.value)
            )
            board_cell.clear()
            board_cell.is_wall = True
            assert_that(
                board_cell.to_s(),
                equal_to(BoardEncodingCharacters.WALL.value)
            )

            board_cell.clear()
            assert_that(
                board_cell.to_s(),
                equal_to(BoardEncodingCharacters.FLOOR.value)
            )
            assert_that(
                board_cell.to_s(use_visible_floor=True),
                equal_to(BoardEncodingCharacters.VISIBLE_FLOOR.value)
            )
