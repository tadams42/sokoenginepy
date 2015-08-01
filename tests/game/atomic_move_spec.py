import pytest
from factories import AtomicMoveFactory
from hamcrest import assert_that, equal_to, is_, none
from sokoenginepy import Direction, Pusher, Box, InvalidPieceIdError


class DescribeAtomicMove(object):

    class Describe_init(object):
        def test_it_sets_all_attributes(self):
            atomic_move = AtomicMoveFactory(
                direction=Direction.RIGHT, box_moved=True
            )

            assert_that(atomic_move.direction, equal_to(Direction.RIGHT))
            assert_that(atomic_move._box_moved, equal_to(True))
            assert_that(atomic_move._pusher_selected, equal_to(False))
            assert_that(atomic_move._pusher_jumped, equal_to(False))
            assert_that(atomic_move._pusher_id, equal_to(Pusher.DEFAULT_ID))
            assert_that(atomic_move._moved_box_id, is_(none()))
            assert_that(atomic_move.group_id, equal_to(0))

    class Describe_moved_box_id(object):
        def test_get_returns_none_if_move_is_not_push_or_pull(
            self, atomic_move
        ):
            atomic_move.moved_box_id = Box.DEFAULT_ID
            atomic_move.is_push_or_pull = False
            assert_that(atomic_move.moved_box_id, is_(none()))

        def test_get_returns_box_that_moved_if_move_is_push_or_pull(
            self, atomic_move
        ):
            atomic_move.is_push_or_pull = True
            atomic_move.moved_box_id = Box.DEFAULT_ID + 42
            assert_that(atomic_move.moved_box_id, equal_to(Box.DEFAULT_ID + 42))

        def test_when_setting_to_none_it_also_resets_push_or_pull_flag(
            self, atomic_move
        ):
            atomic_move.is_push_or_pull = True
            atomic_move.moved_box_id = None

            assert_that(atomic_move.moved_box_id, is_(none()))
            assert_that(atomic_move.is_push_or_pull, equal_to(False))
            assert_that(atomic_move.is_move, equal_to(True))

        def test_when_setting_to_not_none_it_also_sets_push_or_pull_flag(
            self, atomic_move
        ):
            atomic_move.is_push_or_pull = False
            atomic_move.moved_box_id = Box.DEFAULT_ID + 42

            assert_that(atomic_move.moved_box_id, equal_to(Box.DEFAULT_ID + 42))
            assert_that(atomic_move.is_push_or_pull, equal_to(True))
            assert_that(atomic_move.is_move, equal_to(False))

        def test_when_setting_to_not_none_raises_on_invalid_value(
            self, atomic_move):
            with pytest.raises(InvalidPieceIdError):
                atomic_move.moved_box_id = Box.DEFAULT_ID - 1

    class Describe_pusher_id(object):
        def test_it_returns_id_of_pusher_that_performed_movement(
            self, atomic_move
        ):
            atomic_move.pusher_id = Pusher.DEFAULT_ID + 42
            assert_that(atomic_move.pusher_id, equal_to(Pusher.DEFAULT_ID + 42))

        def test_it_raises_on_invalid_id(self, atomic_move):
            with pytest.raises(InvalidPieceIdError):
                atomic_move.pusher_id = None
            with pytest.raises(InvalidPieceIdError):
                atomic_move.pusher_id = Pusher.DEFAULT_ID - 1

    class Describe_is_move(object):
        def test_it_returns_true_if_box_was_not_moved(self, atomic_move):
            atomic_move.is_move = True
            assert_that(atomic_move.is_move, equal_to(True))

        def test_it_returns_false_if_box_was_moved(self, atomic_move):
            atomic_move.is_move = True
            atomic_move.is_push_or_pull = True
            assert_that(atomic_move.is_move, equal_to(False))

        def test_it_returns_false_if_pusher_jumped(self, atomic_move):
            atomic_move.is_move = True
            atomic_move.is_jump = True
            assert_that(atomic_move.is_move, equal_to(False))

        def test_it_returns_false_if_pusher_was_selected(self, atomic_move):
            atomic_move.is_move = True
            atomic_move.is_pusher_selection = True
            assert_that(atomic_move.is_move, equal_to(False))

        def test_setter_sets_to_state_of_box_not_moved(
            self, atomic_move
        ):
            atomic_move.is_move = True
            assert_that(atomic_move.is_move, equal_to(True))

        def test_setter_sets_moved_box_id_to_none_when_setting_to_true(
            self, atomic_move
        ):
            atomic_move.is_move = True
            assert_that(atomic_move.moved_box_id, is_(none()))

        def test_setter_resets_other_flags_when_setting_to_true(
            self, atomic_move
        ):
            atomic_move.is_push_or_pull = True
            atomic_move.is_move = True
            assert_that(atomic_move.is_push_or_pull, equal_to(False))

            atomic_move.is_pusher_selection = True
            atomic_move.is_move = True
            assert_that(atomic_move.is_pusher_selection, equal_to(False))

            atomic_move.is_jump = True
            atomic_move.is_move = True
            assert_that(atomic_move.is_jump, equal_to(False))

        def test_setter_doesnt_touch_other_flags_when_setting_to_false(
            self, atomic_move
        ):
            atomic_move.is_push_or_pull = True
            atomic_move.is_move = False
            assert_that(atomic_move.is_push_or_pull, equal_to(True))

            atomic_move.is_pusher_selection = True
            atomic_move.is_move = False
            assert_that(atomic_move.is_pusher_selection, equal_to(True))

            atomic_move.is_jump = True
            atomic_move.is_move = False
            assert_that(atomic_move.is_jump, equal_to(True))

    class Describe_is_push_or_pull(object):
        def test_it_returns_true_if_box_was_moved(self, atomic_move):
            atomic_move.is_push_or_pull = True
            assert_that(atomic_move.is_push_or_pull, equal_to(True))

        def test_it_returns_false_if_box_was_not_moved(self, atomic_move):
            atomic_move.is_push_or_pull = True
            atomic_move.is_move = True
            assert_that(atomic_move.is_push_or_pull, equal_to(False))

        def test_it_returns_false_if_pusher_jumped(self, atomic_move):
            atomic_move.is_push_or_pull = True
            atomic_move.is_jump = True
            assert_that(atomic_move.is_push_or_pull, equal_to(False))

        def test_it_returns_false_if_pusher_was_selected(self, atomic_move):
            atomic_move.is_push_or_pull = True
            atomic_move.is_pusher_selection = True
            assert_that(atomic_move.is_push_or_pull, equal_to(False))

        def test_setter_sets_to_state_of_box_moved(
            self, atomic_move
        ):
            atomic_move.is_push_or_pull = True
            assert_that(atomic_move.is_push_or_pull, equal_to(True))

        def test_setter_sets_moved_box_id_to_none_when_setting_to_false(
            self, atomic_move
        ):
            atomic_move.is_push_or_pull = False
            assert_that(atomic_move.moved_box_id, is_(none()))

        def test_setter_resets_other_flags_when_setting_to_true(
            self, atomic_move
        ):
            atomic_move.is_move = True
            atomic_move.is_push_or_pull = True
            assert_that(atomic_move.is_move, equal_to(False))

            atomic_move.is_pusher_selection = True
            atomic_move.is_push_or_pull = True
            assert_that(atomic_move.is_pusher_selection, equal_to(False))

            atomic_move.is_jump = True
            atomic_move.is_push_or_pull = True
            assert_that(atomic_move.is_jump, equal_to(False))

        def test_setter_doesnt_touch_other_flags_when_setting_to_false(
            self, atomic_move
        ):
            atomic_move.is_move = True
            atomic_move.is_push_or_pull = False
            assert_that(atomic_move.is_move, equal_to(True))

            atomic_move.is_pusher_selection = True
            atomic_move.is_push_or_pull = False
            assert_that(atomic_move.is_pusher_selection, equal_to(True))

            atomic_move.is_jump = True
            atomic_move.is_push_or_pull = False
            assert_that(atomic_move.is_jump, equal_to(True))

    class Describe_is_pusher_selection(object):
        def test_it_returns_true_if_pusher_was_selected(self, atomic_move):
            atomic_move.is_pusher_selection = True
            assert_that(atomic_move.is_pusher_selection, equal_to(True))

        def test_it_returns_false_if_pusher_was_not_selected(self, atomic_move):
            atomic_move.is_pusher_selection = True
            atomic_move.is_move = True
            assert_that(atomic_move.is_pusher_selection, equal_to(False))

        def test_it_returns_false_if_pusher_jumped(self, atomic_move):
            atomic_move.is_pusher_selection = True
            atomic_move.is_jump = True
            assert_that(atomic_move.is_pusher_selection, equal_to(False))

        def test_it_returns_false_if_pusher_was_selected(self, atomic_move):
            atomic_move.is_pusher_selection = True
            atomic_move.is_push_or_pull = True
            assert_that(atomic_move.is_pusher_selection, equal_to(False))

        def test_setter_sets_to_state_of_pusher_was_selected(
            self, atomic_move
        ):
            atomic_move.is_pusher_selection = True
            assert_that(atomic_move.is_pusher_selection, equal_to(True))

        def test_setter_sets_moved_box_id_to_none_when_setting_to_true(
            self, atomic_move
        ):
            atomic_move.is_pusher_selection = True
            assert_that(atomic_move.moved_box_id, is_(none()))

        def test_setter_resets_other_flags_when_setting_to_true(
            self, atomic_move
        ):
            atomic_move.is_move = True
            atomic_move.is_pusher_selection = True
            assert_that(atomic_move.is_move, equal_to(False))

            atomic_move.is_push_or_pull = True
            atomic_move.is_pusher_selection = True
            assert_that(atomic_move.is_push_or_pull, equal_to(False))

            atomic_move.is_jump = True
            atomic_move.is_pusher_selection = True
            assert_that(atomic_move.is_jump, equal_to(False))

        def test_setter_doesnt_touch_other_flags_when_setting_to_false(
            self, atomic_move
        ):
            atomic_move.is_move = True
            atomic_move.is_pusher_selection = False
            assert_that(atomic_move.is_move, equal_to(True))

            atomic_move.is_push_or_pull = True
            atomic_move.is_pusher_selection = False
            assert_that(atomic_move.is_push_or_pull, equal_to(True))

            atomic_move.is_jump = True
            atomic_move.is_pusher_selection = False
            assert_that(atomic_move.is_jump, equal_to(True))

    class Describe_is_jump(object):
        def test_it_returns_true_if_pusher_jumped(self, atomic_move):
            atomic_move.is_jump = True
            assert_that(atomic_move.is_jump, equal_to(True))

        def test_it_returns_false_if_pusher_moved_insted_of_jumping(
            self, atomic_move
        ):
            atomic_move.is_jump = True
            atomic_move.is_move = True
            assert_that(atomic_move.is_jump, equal_to(False))

        def test_it_returns_false_if_pusher_was_selected(self, atomic_move):
            atomic_move.is_jump = True
            atomic_move.is_pusher_selection = True
            assert_that(atomic_move.is_jump, equal_to(False))

        def test_it_returns_false_if_box_was_moved(self, atomic_move):
            atomic_move.is_jump = True
            atomic_move.is_push_or_pull = True
            assert_that(atomic_move.is_jump, equal_to(False))

        def test_setter_sets_to_state_of_pusher_jumped(
            self, atomic_move
        ):
            atomic_move.is_jump = True
            assert_that(atomic_move.is_jump, equal_to(True))

        def test_setter_sets_moved_box_id_to_none_when_setting_to_true(
            self, atomic_move
        ):
            atomic_move.is_jump = True
            assert_that(atomic_move.moved_box_id, is_(none()))

        def test_setter_resets_other_flags_when_setting_to_true(
            self, atomic_move
        ):
            atomic_move.is_move = True
            atomic_move.is_jump = True
            assert_that(atomic_move.is_move, equal_to(False))

            atomic_move.is_push_or_pull = True
            atomic_move.is_jump = True
            assert_that(atomic_move.is_push_or_pull, equal_to(False))

            atomic_move.is_pusher_selection = True
            atomic_move.is_jump = True
            assert_that(atomic_move.is_pusher_selection, equal_to(False))

        def test_setter_doesnt_touch_other_flags_when_setting_to_false(
            self, atomic_move
        ):
            atomic_move.is_move = True
            atomic_move.is_jump = False
            assert_that(atomic_move.is_move, equal_to(True))

            atomic_move.is_push_or_pull = True
            atomic_move.is_jump = False
            assert_that(atomic_move.is_push_or_pull, equal_to(True))

            atomic_move.is_pusher_selection = True
            atomic_move.is_jump = False
            assert_that(atomic_move.is_pusher_selection, equal_to(True))
