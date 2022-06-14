import pytest

from sokoenginepy.game import Config, Direction, PusherStep

from ..fixtures import PusherStepFactory


@pytest.fixture
def pusher_step():
    return PusherStepFactory(direction=Direction.LEFT, box_moved=False)


class DescribePusherStep:
    class Describe_init:
        def it_sets_all_attributes(self):
            pusher_step = PusherStepFactory(direction=Direction.RIGHT, box_moved=True)

            assert pusher_step.direction == Direction.RIGHT
            assert not pusher_step.is_move
            assert not pusher_step.is_pusher_selection
            assert not pusher_step.is_jump
            assert pusher_step.pusher_id == Config.DEFAULT_PIECE_ID
            assert pusher_step.moved_box_id is None

        def it_validates_parameters(self):
            with pytest.raises(ValueError):
                PusherStep(box_moved=True, is_pusher_selection=True, is_jump=True)
            with pytest.raises(ValueError):
                PusherStep(moved_box_id=42, is_pusher_selection=True, is_jump=True)

            with pytest.raises(ValueError):
                PusherStep(box_moved=True, is_jump=True)
            with pytest.raises(ValueError):
                PusherStep(moved_box_id=42, is_jump=True)

            with pytest.raises(ValueError):
                PusherStep(box_moved=True, is_pusher_selection=True)
            with pytest.raises(ValueError):
                PusherStep(moved_box_id=42, is_pusher_selection=True)

            with pytest.raises(ValueError):
                PusherStep(is_jump=True, is_pusher_selection=True)

    class Describe_moved_box_id:
        def test_get_returns_none_if_move_is_not_push_or_pull(self, pusher_step):
            pusher_step.moved_box_id = Config.DEFAULT_PIECE_ID
            pusher_step.is_push_or_pull = False
            assert pusher_step.moved_box_id is None

        def test_get_returns_box_that_moved_if_move_is_push_or_pull(self, pusher_step):
            pusher_step.is_push_or_pull = True
            pusher_step.moved_box_id = Config.DEFAULT_PIECE_ID + 42
            assert pusher_step.moved_box_id == Config.DEFAULT_PIECE_ID + 42

        def test_when_setting_to_none_it_also_resets_push_or_pull_flag(
            self, pusher_step
        ):
            pusher_step.is_push_or_pull = True
            pusher_step.moved_box_id = None

            assert pusher_step.moved_box_id is None
            assert not pusher_step.is_push_or_pull
            assert pusher_step.is_move

        def test_when_setting_to_not_none_it_also_sets_push_or_pull_flag(
            self, pusher_step
        ):
            pusher_step.is_push_or_pull = False
            pusher_step.moved_box_id = Config.DEFAULT_PIECE_ID + 42

            assert pusher_step.moved_box_id == Config.DEFAULT_PIECE_ID + 42
            assert pusher_step.is_push_or_pull
            assert not pusher_step.is_move

        def it_sets_it_to_none_if_illegal_value_provided(self, pusher_step):
            pusher_step.moved_box_id = 4
            assert pusher_step.moved_box_id == 4
            pusher_step.moved_box_id = -42
            assert pusher_step.moved_box_id is None

            pusher_step.moved_box_id = 4
            assert pusher_step.moved_box_id == 4
            pusher_step.moved_box_id = None
            assert pusher_step.moved_box_id is None

            pusher_step.moved_box_id = 4
            assert pusher_step.moved_box_id == 4
            pusher_step.moved_box_id = "ZOMG!"
            assert pusher_step.moved_box_id is None

            pusher_step.moved_box_id = 4
            assert pusher_step.moved_box_id == 4
            pusher_step.moved_box_id = 0
            assert pusher_step.moved_box_id is None

            m = PusherStep(moved_box_id=-42)
            assert m.moved_box_id is None

            m = PusherStep(moved_box_id=None)
            assert m.moved_box_id is None

            m = PusherStep(moved_box_id="ZOMG")
            assert m.moved_box_id is None

            m = PusherStep(moved_box_id=0)
            assert m.moved_box_id is None

    class Describe_pusher_id:
        def it_returns_id_of_pusher_that_performed_movement(self, pusher_step):
            pusher_step.pusher_id = Config.DEFAULT_PIECE_ID + 42
            assert pusher_step.pusher_id == Config.DEFAULT_PIECE_ID + 42

        def it_sets_it_to_default_if_illegal_value_provided(self, pusher_step):
            pusher_step.pusher_id = 4
            assert pusher_step.pusher_id == 4
            pusher_step.pusher_id = -42
            assert pusher_step.pusher_id == Config.DEFAULT_PIECE_ID

            pusher_step.pusher_id = 4
            assert pusher_step.pusher_id == 4
            pusher_step.pusher_id = None
            assert pusher_step.pusher_id == Config.DEFAULT_PIECE_ID

            pusher_step.pusher_id = 4
            assert pusher_step.pusher_id == 4
            pusher_step.pusher_id = "ZOMG!"
            assert pusher_step.pusher_id == Config.DEFAULT_PIECE_ID

    class Describe_is_move:
        def it_returns_true_if_box_was_not_moved(self, pusher_step):
            pusher_step.is_move = True
            assert pusher_step.is_move

        def it_returns_false_if_box_was_moved(self, pusher_step):
            pusher_step.is_move = True
            pusher_step.is_push_or_pull = True
            assert not pusher_step.is_move

        def it_returns_false_if_pusher_jumped(self, pusher_step):
            pusher_step.is_move = True
            pusher_step.is_jump = True
            assert not pusher_step.is_move

        def it_returns_false_if_pusher_was_selected(self, pusher_step):
            pusher_step.is_move = True
            pusher_step.is_pusher_selection = True
            assert not pusher_step.is_move

        def test_setter_sets_to_state_of_box_not_moved(self, pusher_step):
            pusher_step.is_move = True
            assert pusher_step.is_move

        def test_setter_sets_moved_box_id_to_none_when_setting_to_true(
            self, pusher_step
        ):
            pusher_step.is_move = True
            assert pusher_step.moved_box_id is None

        def test_setter_resets_other_flags_when_setting_to_true(self, pusher_step):
            pusher_step.is_push_or_pull = True
            pusher_step.is_move = True
            assert not pusher_step.is_push_or_pull

            pusher_step.is_pusher_selection = True
            pusher_step.is_move = True
            assert not pusher_step.is_pusher_selection

            pusher_step.is_jump = True
            pusher_step.is_move = True
            assert not pusher_step.is_jump

        def test_setter_assumes_push_when_setting_to_false(self, pusher_step):
            pusher_step.is_move = False
            assert pusher_step.is_push_or_pull
            assert not pusher_step.is_pusher_selection
            assert not pusher_step.is_jump

    class Describe_is_push_or_pull:
        def it_returns_true_if_box_was_moved(self, pusher_step):
            pusher_step.is_push_or_pull = True
            assert pusher_step.is_push_or_pull

        def it_returns_false_if_box_was_not_moved(self, pusher_step):
            pusher_step.is_push_or_pull = True
            pusher_step.is_move = True
            assert not pusher_step.is_push_or_pull

        def it_returns_false_if_pusher_jumped(self, pusher_step):
            pusher_step.is_push_or_pull = True
            pusher_step.is_jump = True
            assert not pusher_step.is_push_or_pull

        def it_returns_false_if_pusher_was_selected(self, pusher_step):
            pusher_step.is_push_or_pull = True
            pusher_step.is_pusher_selection = True
            assert not pusher_step.is_push_or_pull

        def test_setter_sets_to_state_of_box_moved(self, pusher_step):
            pusher_step.is_push_or_pull = True
            assert pusher_step.is_push_or_pull

        def test_setter_sets_moved_box_id_to_none_when_setting_to_false(
            self, pusher_step
        ):
            pusher_step.is_push_or_pull = False
            assert pusher_step.moved_box_id is None

        def test_setter_resets_other_flags_when_setting_to_true(self, pusher_step):
            pusher_step.is_move = True
            pusher_step.is_push_or_pull = True
            assert not pusher_step.is_move

            pusher_step.is_pusher_selection = True
            pusher_step.is_push_or_pull = True
            assert not pusher_step.is_pusher_selection

            pusher_step.is_jump = True
            pusher_step.is_push_or_pull = True
            assert not pusher_step.is_jump

        def test_setter_doesnt_touch_other_flags_when_setting_to_false(
            self, pusher_step
        ):
            pusher_step.is_move = True
            pusher_step.is_push_or_pull = False
            assert pusher_step.is_move

            pusher_step.is_pusher_selection = True
            pusher_step.is_push_or_pull = False
            assert pusher_step.is_pusher_selection

            pusher_step.is_jump = True
            pusher_step.is_push_or_pull = False
            assert pusher_step.is_jump

    class Describe_is_pusher_selection:
        def it_returns_true_if_pusher_was_selected(self, pusher_step):
            pusher_step.is_pusher_selection = True
            assert pusher_step.is_pusher_selection

        def it_returns_false_if_pusher_was_not_selected(self, pusher_step):
            pusher_step.is_pusher_selection = True
            pusher_step.is_move = True
            assert not pusher_step.is_pusher_selection

        def it_returns_false_if_pusher_jumped(self, pusher_step):
            pusher_step.is_pusher_selection = True
            pusher_step.is_jump = True
            assert not pusher_step.is_pusher_selection

        def it_returns_false_if_pusher_was_selected(self, pusher_step):
            pusher_step.is_pusher_selection = True
            pusher_step.is_push_or_pull = True
            assert not pusher_step.is_pusher_selection

        def test_setter_sets_to_state_of_pusher_was_selected(self, pusher_step):
            pusher_step.is_pusher_selection = True
            assert pusher_step.is_pusher_selection

        def test_setter_sets_moved_box_id_to_none_when_setting_to_true(
            self, pusher_step
        ):
            pusher_step.is_pusher_selection = True
            assert pusher_step.moved_box_id is None

        def test_setter_resets_other_flags_when_setting_to_true(self, pusher_step):
            pusher_step.is_move = True
            pusher_step.is_pusher_selection = True
            assert not pusher_step.is_move

            pusher_step.is_push_or_pull = True
            pusher_step.is_pusher_selection = True
            assert not pusher_step.is_push_or_pull

            pusher_step.is_jump = True
            pusher_step.is_pusher_selection = True
            assert not pusher_step.is_jump

        def test_setter_doesnt_touch_other_flags_when_setting_to_false(
            self, pusher_step
        ):
            pusher_step.is_move = True
            pusher_step.is_pusher_selection = False
            assert pusher_step.is_move

            pusher_step.is_push_or_pull = True
            pusher_step.is_pusher_selection = False
            assert pusher_step.is_push_or_pull

            pusher_step.is_jump = True
            pusher_step.is_pusher_selection = False
            assert pusher_step.is_jump

    class Describe_is_jump:
        def it_returns_true_if_pusher_jumped(self, pusher_step):
            pusher_step.is_jump = True
            assert pusher_step.is_jump

        def it_returns_false_if_pusher_moved_insted_of_jumping(self, pusher_step):
            pusher_step.is_jump = True
            pusher_step.is_move = True
            assert not pusher_step.is_jump

        def it_returns_false_if_pusher_was_selected(self, pusher_step):
            pusher_step.is_jump = True
            pusher_step.is_pusher_selection = True
            assert not pusher_step.is_jump

        def it_returns_false_if_box_was_moved(self, pusher_step):
            pusher_step.is_jump = True
            pusher_step.is_push_or_pull = True
            assert not pusher_step.is_jump

        def test_setter_sets_to_state_of_pusher_jumped(self, pusher_step):
            pusher_step.is_jump = True
            assert pusher_step.is_jump

        def test_setter_sets_moved_box_id_to_none_when_setting_to_true(
            self, pusher_step
        ):
            pusher_step.is_jump = True
            assert pusher_step.moved_box_id is None

        def test_setter_resets_other_flags_when_setting_to_true(self, pusher_step):
            pusher_step.is_move = True
            pusher_step.is_jump = True
            assert not pusher_step.is_move

            pusher_step.is_push_or_pull = True
            pusher_step.is_jump = True
            assert not pusher_step.is_push_or_pull

            pusher_step.is_pusher_selection = True
            pusher_step.is_jump = True
            assert not pusher_step.is_pusher_selection

        def test_setter_doesnt_touch_other_flags_when_setting_to_false(
            self, pusher_step
        ):
            pusher_step.is_move = True
            pusher_step.is_jump = False
            assert pusher_step.is_move

            pusher_step.is_push_or_pull = True
            pusher_step.is_jump = False
            assert pusher_step.is_push_or_pull

            pusher_step.is_pusher_selection = True
            pusher_step.is_jump = False
            assert pusher_step.is_pusher_selection
