from factories import AtomicMoveFactory
from sokoenginepy.common import DEFAULT_PIECE_ID, Direction


class DescribeAtomicMove:

    class Describe_init:

        def it_sets_all_attributes(self):
            atomic_move = AtomicMoveFactory(
                direction=Direction.RIGHT, box_moved=True
            )

            assert atomic_move.direction == Direction.RIGHT
            assert atomic_move._box_moved
            assert not atomic_move._pusher_selected
            assert not atomic_move._pusher_jumped
            assert atomic_move._pusher_id == DEFAULT_PIECE_ID
            assert atomic_move._moved_box_id is None
            assert atomic_move.group_id == 0

    class Describe_moved_box_id:

        def test_get_returns_none_if_move_is_not_push_or_pull(
            self, atomic_move
        ):
            atomic_move.moved_box_id = DEFAULT_PIECE_ID
            atomic_move.is_push_or_pull = False
            assert atomic_move.moved_box_id is None

        def test_get_returns_box_that_moved_if_move_is_push_or_pull(
            self, atomic_move
        ):
            atomic_move.is_push_or_pull = True
            atomic_move.moved_box_id = DEFAULT_PIECE_ID + 42
            assert atomic_move.moved_box_id == DEFAULT_PIECE_ID + 42

        def test_when_setting_to_none_it_also_resets_push_or_pull_flag(
            self, atomic_move
        ):
            atomic_move.is_push_or_pull = True
            atomic_move.moved_box_id = None

            assert atomic_move.moved_box_id is None
            assert not atomic_move.is_push_or_pull
            assert atomic_move.is_move

        def test_when_setting_to_not_none_it_also_sets_push_or_pull_flag(
            self, atomic_move
        ):
            atomic_move.is_push_or_pull = False
            atomic_move.moved_box_id = DEFAULT_PIECE_ID + 42

            assert atomic_move.moved_box_id == DEFAULT_PIECE_ID + 42
            assert atomic_move.is_push_or_pull
            assert not atomic_move.is_move

    class Describe_pusher_id:

        def it_returns_id_of_pusher_that_performed_movement(self, atomic_move):
            atomic_move.pusher_id = DEFAULT_PIECE_ID + 42
            assert atomic_move.pusher_id == DEFAULT_PIECE_ID + 42

    class Describe_is_move:

        def it_returns_true_if_box_was_not_moved(self, atomic_move):
            atomic_move.is_move = True
            assert atomic_move.is_move

        def it_returns_false_if_box_was_moved(self, atomic_move):
            atomic_move.is_move = True
            atomic_move.is_push_or_pull = True
            assert not atomic_move.is_move

        def it_returns_false_if_pusher_jumped(self, atomic_move):
            atomic_move.is_move = True
            atomic_move.is_jump = True
            assert not atomic_move.is_move

        def it_returns_false_if_pusher_was_selected(self, atomic_move):
            atomic_move.is_move = True
            atomic_move.is_pusher_selection = True
            assert not atomic_move.is_move

        def test_setter_sets_to_state_of_box_not_moved(self, atomic_move):
            atomic_move.is_move = True
            assert atomic_move.is_move

        def test_setter_sets_moved_box_id_to_none_when_setting_to_true(
            self, atomic_move
        ):
            atomic_move.is_move = True
            assert atomic_move.moved_box_id is None

        def test_setter_resets_other_flags_when_setting_to_true(
            self, atomic_move
        ):
            atomic_move.is_push_or_pull = True
            atomic_move.is_move = True
            assert not atomic_move.is_push_or_pull

            atomic_move.is_pusher_selection = True
            atomic_move.is_move = True
            assert not atomic_move.is_pusher_selection

            atomic_move.is_jump = True
            atomic_move.is_move = True
            assert not atomic_move.is_jump

        def test_setter_assumes_push_when_setting_to_false(self, atomic_move):
            atomic_move.is_move = False
            assert atomic_move.is_push_or_pull
            assert not atomic_move.is_pusher_selection
            assert not atomic_move.is_jump

    class Describe_is_push_or_pull:

        def it_returns_true_if_box_was_moved(self, atomic_move):
            atomic_move.is_push_or_pull = True
            assert atomic_move.is_push_or_pull

        def it_returns_false_if_box_was_not_moved(self, atomic_move):
            atomic_move.is_push_or_pull = True
            atomic_move.is_move = True
            assert not atomic_move.is_push_or_pull

        def it_returns_false_if_pusher_jumped(self, atomic_move):
            atomic_move.is_push_or_pull = True
            atomic_move.is_jump = True
            assert not atomic_move.is_push_or_pull

        def it_returns_false_if_pusher_was_selected(self, atomic_move):
            atomic_move.is_push_or_pull = True
            atomic_move.is_pusher_selection = True
            assert not atomic_move.is_push_or_pull

        def test_setter_sets_to_state_of_box_moved(self, atomic_move):
            atomic_move.is_push_or_pull = True
            assert atomic_move.is_push_or_pull

        def test_setter_sets_moved_box_id_to_none_when_setting_to_false(
            self, atomic_move
        ):
            atomic_move.is_push_or_pull = False
            assert atomic_move.moved_box_id is None

        def test_setter_resets_other_flags_when_setting_to_true(
            self, atomic_move
        ):
            atomic_move.is_move = True
            atomic_move.is_push_or_pull = True
            assert not atomic_move.is_move

            atomic_move.is_pusher_selection = True
            atomic_move.is_push_or_pull = True
            assert not atomic_move.is_pusher_selection

            atomic_move.is_jump = True
            atomic_move.is_push_or_pull = True
            assert not atomic_move.is_jump

        def test_setter_doesnt_touch_other_flags_when_setting_to_false(
            self, atomic_move
        ):
            atomic_move.is_move = True
            atomic_move.is_push_or_pull = False
            assert atomic_move.is_move

            atomic_move.is_pusher_selection = True
            atomic_move.is_push_or_pull = False
            assert atomic_move.is_pusher_selection

            atomic_move.is_jump = True
            atomic_move.is_push_or_pull = False
            assert atomic_move.is_jump

    class Describe_is_pusher_selection:

        def it_returns_true_if_pusher_was_selected(self, atomic_move):
            atomic_move.is_pusher_selection = True
            assert atomic_move.is_pusher_selection

        def it_returns_false_if_pusher_was_not_selected(self, atomic_move):
            atomic_move.is_pusher_selection = True
            atomic_move.is_move = True
            assert not atomic_move.is_pusher_selection

        def it_returns_false_if_pusher_jumped(self, atomic_move):
            atomic_move.is_pusher_selection = True
            atomic_move.is_jump = True
            assert not atomic_move.is_pusher_selection

        def it_returns_false_if_pusher_was_selected(self, atomic_move):
            atomic_move.is_pusher_selection = True
            atomic_move.is_push_or_pull = True
            assert not atomic_move.is_pusher_selection

        def test_setter_sets_to_state_of_pusher_was_selected(self, atomic_move):
            atomic_move.is_pusher_selection = True
            assert atomic_move.is_pusher_selection

        def test_setter_sets_moved_box_id_to_none_when_setting_to_true(
            self, atomic_move
        ):
            atomic_move.is_pusher_selection = True
            assert atomic_move.moved_box_id is None

        def test_setter_resets_other_flags_when_setting_to_true(
            self, atomic_move
        ):
            atomic_move.is_move = True
            atomic_move.is_pusher_selection = True
            assert not atomic_move.is_move

            atomic_move.is_push_or_pull = True
            atomic_move.is_pusher_selection = True
            assert not atomic_move.is_push_or_pull

            atomic_move.is_jump = True
            atomic_move.is_pusher_selection = True
            assert not atomic_move.is_jump

        def test_setter_doesnt_touch_other_flags_when_setting_to_false(
            self, atomic_move
        ):
            atomic_move.is_move = True
            atomic_move.is_pusher_selection = False
            assert atomic_move.is_move

            atomic_move.is_push_or_pull = True
            atomic_move.is_pusher_selection = False
            assert atomic_move.is_push_or_pull

            atomic_move.is_jump = True
            atomic_move.is_pusher_selection = False
            assert atomic_move.is_jump

    class Describe_is_jump:

        def it_returns_true_if_pusher_jumped(self, atomic_move):
            atomic_move.is_jump = True
            assert atomic_move.is_jump

        def it_returns_false_if_pusher_moved_insted_of_jumping(
            self, atomic_move
        ):
            atomic_move.is_jump = True
            atomic_move.is_move = True
            assert not atomic_move.is_jump

        def it_returns_false_if_pusher_was_selected(self, atomic_move):
            atomic_move.is_jump = True
            atomic_move.is_pusher_selection = True
            assert not atomic_move.is_jump

        def it_returns_false_if_box_was_moved(self, atomic_move):
            atomic_move.is_jump = True
            atomic_move.is_push_or_pull = True
            assert not atomic_move.is_jump

        def test_setter_sets_to_state_of_pusher_jumped(self, atomic_move):
            atomic_move.is_jump = True
            assert atomic_move.is_jump

        def test_setter_sets_moved_box_id_to_none_when_setting_to_true(
            self, atomic_move
        ):
            atomic_move.is_jump = True
            assert atomic_move.moved_box_id is None

        def test_setter_resets_other_flags_when_setting_to_true(
            self, atomic_move
        ):
            atomic_move.is_move = True
            atomic_move.is_jump = True
            assert not atomic_move.is_move

            atomic_move.is_push_or_pull = True
            atomic_move.is_jump = True
            assert not atomic_move.is_push_or_pull

            atomic_move.is_pusher_selection = True
            atomic_move.is_jump = True
            assert not atomic_move.is_pusher_selection

        def test_setter_doesnt_touch_other_flags_when_setting_to_false(
            self, atomic_move
        ):
            atomic_move.is_move = True
            atomic_move.is_jump = False
            assert atomic_move.is_move

            atomic_move.is_push_or_pull = True
            atomic_move.is_jump = False
            assert atomic_move.is_push_or_pull

            atomic_move.is_pusher_selection = True
            atomic_move.is_jump = False
            assert atomic_move.is_pusher_selection
