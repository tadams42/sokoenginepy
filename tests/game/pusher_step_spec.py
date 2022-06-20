import pytest

from sokoenginepy.game import Config, Direction, PusherStep


class DescribePusherStep:
    class Describe_init:
        def it_constructs_move(self):
            pusher_step = PusherStep(direction=Direction.RIGHT)
            assert pusher_step.direction == Direction.RIGHT
            assert pusher_step.is_move
            assert not pusher_step.is_push_or_pull
            assert not pusher_step.is_pusher_selection
            assert not pusher_step.is_jump
            assert pusher_step.pusher_id == Config.DEFAULT_ID
            assert pusher_step.moved_box_id == Config.NO_ID

        def it_constructs_push(self):
            pusher_step = PusherStep(direction=Direction.RIGHT, moved_box_id=42)
            assert pusher_step.direction == Direction.RIGHT
            assert not pusher_step.is_move
            assert pusher_step.is_push_or_pull
            assert not pusher_step.is_pusher_selection
            assert not pusher_step.is_jump
            assert pusher_step.pusher_id == Config.DEFAULT_ID
            assert pusher_step.moved_box_id == 42

        def it_constructs_jump(self):
            pusher_step = PusherStep(direction=Direction.RIGHT, is_jump=True)
            assert pusher_step.direction == Direction.RIGHT
            assert not pusher_step.is_move
            assert not pusher_step.is_push_or_pull
            assert not pusher_step.is_pusher_selection
            assert pusher_step.is_jump
            assert pusher_step.pusher_id == Config.DEFAULT_ID
            assert pusher_step.moved_box_id == Config.NO_ID

        def it_constructs_pusher_selection(self):
            pusher_step = PusherStep(
                direction=Direction.RIGHT, is_pusher_selection=True
            )
            assert pusher_step.direction == Direction.RIGHT
            assert not pusher_step.is_move
            assert not pusher_step.is_push_or_pull
            assert pusher_step.is_pusher_selection
            assert not pusher_step.is_jump
            assert pusher_step.pusher_id == Config.DEFAULT_ID
            assert pusher_step.moved_box_id == Config.NO_ID

        def it_correctly_sets_pusher_id(self):
            pusher_step = PusherStep(direction=Direction.RIGHT, pusher_id=42)
            assert pusher_step.pusher_id == 42

            pusher_step = PusherStep(direction=Direction.RIGHT, pusher_id=-42)
            assert pusher_step.pusher_id == Config.DEFAULT_ID

        def it_correctly_sets_moved_box_id(self):
            pusher_step = PusherStep(direction=Direction.RIGHT, moved_box_id=42)
            assert pusher_step.moved_box_id == 42

            pusher_step = PusherStep(direction=Direction.RIGHT, moved_box_id=-42)
            assert pusher_step.moved_box_id == Config.NO_ID

        def it_validates_parameters(self):
            with pytest.raises(ValueError):
                PusherStep(moved_box_id=42, is_pusher_selection=True, is_jump=True)

            with pytest.raises(ValueError):
                PusherStep(moved_box_id=42, is_jump=True)

            with pytest.raises(ValueError):
                PusherStep(moved_box_id=42, is_pusher_selection=True)

            with pytest.raises(ValueError):
                PusherStep(is_jump=True, is_pusher_selection=True)

    class Describe_moved_box_id:
        def test_getter_returns_no_id_if_move_is_not_push_or_pull(self):
            pusher_step = PusherStep(moved_box_id=Config.NO_ID)
            assert pusher_step.moved_box_id == Config.NO_ID

        def test_when_setting_to_no_id_it_also_resets_push_or_pull_flag(self):
            pusher_step = PusherStep(moved_box_id=42)
            assert not pusher_step.is_move
            assert pusher_step.is_push_or_pull

            pusher_step.moved_box_id = Config.NO_ID
            assert pusher_step.moved_box_id == Config.NO_ID
            assert pusher_step.is_move
            assert not pusher_step.is_push_or_pull

        def test_when_setting_to_not_no_id_it_also_sets_push_or_pull_flag(self):
            pusher_step = PusherStep()
            assert pusher_step.is_move
            assert not pusher_step.is_push_or_pull

            pusher_step.moved_box_id = 42
            assert pusher_step.moved_box_id == 42
            assert pusher_step.is_push_or_pull
            assert not pusher_step.is_move

        def it_sets_it_to_no_id_if_illegal_value_provided(self):
            pusher_step = PusherStep(moved_box_id=0)
            assert pusher_step.moved_box_id == Config.NO_ID

            pusher_step = PusherStep(moved_box_id=42)
            pusher_step.moved_box_id = 0
            assert pusher_step.moved_box_id == Config.NO_ID

            pusher_step.moved_box_id = -42
            assert pusher_step.moved_box_id == Config.NO_ID

        def test_setter_assumes_push_when_setting_to_valid_value(self):
            pusher_step = PusherStep()
            pusher_step.moved_box_id = 42
            assert pusher_step.is_push_or_pull
            assert not pusher_step.is_move

            pusher_step = PusherStep(is_jump=True)
            pusher_step.moved_box_id = 42
            assert pusher_step.is_push_or_pull
            assert not pusher_step.is_jump

            pusher_step = PusherStep(is_pusher_selection=True)
            pusher_step.moved_box_id = 42
            assert pusher_step.is_push_or_pull
            assert not pusher_step.is_pusher_selection

        def test_setter_doesnt_touch_other_flags_when_setting_to_no_id(self):
            pusher_step = PusherStep(is_jump=True)
            pusher_step.moved_box_id = Config.NO_ID
            assert pusher_step.is_jump

            pusher_step = PusherStep(is_pusher_selection=True)
            pusher_step.moved_box_id = Config.NO_ID
            assert pusher_step.is_pusher_selection

    class Describe_pusher_id:
        def it_returns_id_of_pusher_that_performed_movement(self):
            pusher_step = PusherStep(pusher_id=42)
            assert pusher_step.pusher_id == 42

        def it_sets_it_to_default_if_illegal_value_provided(self):
            pusher_step = PusherStep(pusher_id=42)
            pusher_step.pusher_id = 0
            assert pusher_step.pusher_id == Config.DEFAULT_ID

            pusher_step = PusherStep(pusher_id=42)
            pusher_step.pusher_id = Config.NO_ID
            assert pusher_step.pusher_id == Config.DEFAULT_ID

            pusher_step = PusherStep(pusher_id=42)
            pusher_step.pusher_id = -42
            assert pusher_step.pusher_id == Config.DEFAULT_ID

    class Describe_is_move:
        def it_returns_true_if_box_was_not_moved(self):
            pusher_step = PusherStep()
            assert pusher_step.is_move

        def it_returns_false_if_box_was_moved(self):
            pusher_step = PusherStep(moved_box_id=42)
            assert not pusher_step.is_move

        def it_returns_false_if_pusher_jumped(self):
            pusher_step = PusherStep(is_jump=True)
            assert not pusher_step.is_move

        def it_returns_false_if_pusher_was_selected(self):
            pusher_step = PusherStep(is_pusher_selection=True)
            assert not pusher_step.is_move

    class Describe_is_push_or_pull:
        def it_returns_true_if_box_was_moved(self):
            pusher_step = PusherStep(moved_box_id=42)
            assert pusher_step.is_push_or_pull

        def it_returns_false_if_box_was_not_moved(self):
            pusher_step = PusherStep()
            assert not pusher_step.is_push_or_pull

        def it_returns_false_if_pusher_jumped(self):
            pusher_step = PusherStep(is_jump=True)
            assert not pusher_step.is_push_or_pull

        def it_returns_false_if_pusher_was_selected(self):
            pusher_step = PusherStep(is_pusher_selection=True)
            assert not pusher_step.is_push_or_pull

    class Describe_is_pusher_selection:
        def it_returns_true_if_pusher_was_selected(self):
            pusher_step = PusherStep(is_pusher_selection=True)
            assert pusher_step.is_pusher_selection

        def it_returns_false_if_pusher_was_not_selected(self):
            pusher_step = PusherStep(is_pusher_selection=False)
            assert not pusher_step.is_pusher_selection

        def it_returns_false_if_pusher_jumped(self):
            pusher_step = PusherStep(is_jump=True)
            assert not pusher_step.is_pusher_selection

        def test_setter_sets_to_state_of_pusher_was_selected(self):
            pusher_step = PusherStep(is_pusher_selection=False)
            pusher_step.is_pusher_selection = True
            assert pusher_step.is_pusher_selection

        def test_setter_sets_moved_box_id_to_no_id_when_setting_to_true(self):
            pusher_step = PusherStep(moved_box_id=42)
            pusher_step.is_pusher_selection = True
            assert pusher_step.moved_box_id == Config.NO_ID

        def test_setter_resets_other_flags_when_setting_to_true(self):
            pusher_step = PusherStep(is_jump=True)
            pusher_step.is_pusher_selection = True
            assert not pusher_step.is_jump

            pusher_step = PusherStep(moved_box_id=42)
            pusher_step.is_pusher_selection = True
            assert not pusher_step.is_push_or_pull

            pusher_step = PusherStep()
            pusher_step.is_pusher_selection = True
            assert not pusher_step.is_move

        def test_setter_doesnt_touch_other_flags_when_setting_to_false(self):
            pusher_step = PusherStep(is_jump=True)
            pusher_step.is_pusher_selection = False
            assert pusher_step.is_jump

            pusher_step = PusherStep(moved_box_id=42)
            pusher_step.is_pusher_selection = False
            assert pusher_step.is_push_or_pull

            pusher_step = PusherStep()
            pusher_step.is_pusher_selection = False
            assert pusher_step.is_move

    class Describe_is_jump:
        def it_returns_true_if_pusher_jumped(self):
            pusher_step = PusherStep(is_jump=True)
            assert pusher_step.is_jump

        def it_returns_false_if_pusher_moved(self):
            pusher_step = PusherStep()
            assert not pusher_step.is_jump

        def it_returns_false_if_box_was_moved(self):
            pusher_step = PusherStep(moved_box_id=42)
            assert not pusher_step.is_jump

        def it_returns_false_if_pusher_was_selected(self):
            pusher_step = PusherStep(is_pusher_selection=True)
            assert not pusher_step.is_jump

        def test_setter_sets_to_state_of_pusher_jumped(self):
            pusher_step = PusherStep()
            pusher_step.is_jump = True
            assert pusher_step.is_jump

        def test_setter_sets_moved_box_id_to_no_id_when_setting_to_true(self):
            pusher_step = PusherStep(moved_box_id=42)
            pusher_step.is_jump = True
            assert pusher_step.moved_box_id == Config.NO_ID

        def test_setter_resets_other_flags_when_setting_to_true(self):
            pusher_step = PusherStep()
            pusher_step.is_jump = True
            assert not pusher_step.is_move

            pusher_step = PusherStep(moved_box_id=42)
            pusher_step.is_jump = True
            assert not pusher_step.is_push_or_pull

            pusher_step = PusherStep(is_pusher_selection=True)
            pusher_step.is_jump = True
            assert not pusher_step.is_pusher_selection

        def test_setter_doesnt_touch_other_flags_when_setting_to_false(self):
            pusher_step = PusherStep()
            pusher_step.is_jump = False
            assert pusher_step.is_move

            pusher_step = PusherStep(moved_box_id=42)
            pusher_step.is_jump = False
            assert pusher_step.is_push_or_pull

            pusher_step = PusherStep(is_pusher_selection=True)
            pusher_step.is_jump = False
            assert pusher_step.is_pusher_selection
