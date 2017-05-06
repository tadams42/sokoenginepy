from copy import deepcopy

from sokoenginepy import DEFAULT_PIECE_ID


class DescribeHashedBoardState:
    def it_hashes_board_layout(self, hashed_board_state):
        assert hashed_board_state.boxes_layout_hash is not None
        assert hashed_board_state.boxes_and_pushers_layout_hash is not None
        assert hashed_board_state.boxes_layout_hash != hashed_board_state.boxes_and_pushers_layout_hash

    def test_moving_box_modifies_hashes_consistently(self, hashed_board_state):
        initial_box_hash = hashed_board_state.boxes_layout_hash
        initial_pus_hash = hashed_board_state.boxes_and_pushers_layout_hash

        initial_box_position = hashed_board_state.box_position(DEFAULT_PIECE_ID)
        new_box_position = initial_box_position + 1

        hashed_board_state.move_box_from(initial_box_position, new_box_position)
        assert hashed_board_state.boxes_layout_hash != initial_box_hash
        assert hashed_board_state.boxes_and_pushers_layout_hash != initial_pus_hash

        hashed_board_state.move_box_from(new_box_position, initial_box_position)
        assert hashed_board_state.boxes_layout_hash == initial_box_hash
        assert hashed_board_state.boxes_and_pushers_layout_hash == initial_pus_hash

        hashed_board_state.move_box(DEFAULT_PIECE_ID, new_box_position)
        assert hashed_board_state.boxes_layout_hash != initial_box_hash
        assert hashed_board_state.boxes_and_pushers_layout_hash != initial_pus_hash

        hashed_board_state.move_box(DEFAULT_PIECE_ID, initial_box_position)
        assert hashed_board_state.boxes_layout_hash == initial_box_hash
        assert hashed_board_state.boxes_and_pushers_layout_hash == initial_pus_hash

    def test_moving_pusher_modifies_hashes_consistently(
        self, hashed_board_state
    ):
        initial_box_hash = hashed_board_state.boxes_layout_hash
        initial_pus_hash = hashed_board_state.boxes_and_pushers_layout_hash

        initial_pusher_position = hashed_board_state.pusher_position(
            DEFAULT_PIECE_ID
        )
        new_pusher_position = initial_pusher_position - 1

        hashed_board_state.move_pusher_from(
            initial_pusher_position, new_pusher_position
        )
        assert hashed_board_state.boxes_layout_hash == initial_box_hash
        assert hashed_board_state.boxes_and_pushers_layout_hash != initial_pus_hash

        hashed_board_state.move_pusher_from(
            new_pusher_position, initial_pusher_position
        )
        assert hashed_board_state.boxes_layout_hash == initial_box_hash
        assert hashed_board_state.boxes_and_pushers_layout_hash == initial_pus_hash

        hashed_board_state.move_pusher(DEFAULT_PIECE_ID, new_pusher_position)
        assert hashed_board_state.boxes_layout_hash == initial_box_hash
        assert hashed_board_state.boxes_and_pushers_layout_hash != initial_pus_hash

        hashed_board_state.move_pusher(
            DEFAULT_PIECE_ID, initial_pusher_position
        )
        assert hashed_board_state.boxes_layout_hash == initial_box_hash
        assert hashed_board_state.boxes_and_pushers_layout_hash == initial_pus_hash

    def test_setting_boxorder_or_goalorder_on_enabled_sokoban_plus_rehashes_board(
        self, hashed_board_state
    ):
        initial_box_hash = hashed_board_state.boxes_layout_hash
        initial_pus_hash = hashed_board_state.boxes_and_pushers_layout_hash
        hashed_board_state.enable_sokoban_plus()
        assert hashed_board_state.is_sokoban_plus_enabled is True
        hashed_board_state.boxorder = '1 2 3'
        assert hashed_board_state.boxes_layout_hash != initial_box_hash
        assert hashed_board_state.boxes_and_pushers_layout_hash != initial_pus_hash

        hashed_board_state.boxorder = None
        initial_box_hash = hashed_board_state.boxes_layout_hash
        initial_pus_hash = hashed_board_state.boxes_and_pushers_layout_hash
        hashed_board_state.enable_sokoban_plus()
        assert hashed_board_state.is_sokoban_plus_enabled is True
        hashed_board_state.goalorder = '1 2 3'
        assert hashed_board_state.boxes_layout_hash != initial_box_hash
        assert hashed_board_state.boxes_and_pushers_layout_hash != initial_pus_hash

    def test_setting_equal_boxorder_or_goalorder_on_enabled_sokoban_plus_doesnt_rehash_board(
        self, hashed_board_state
    ):
        hashed_board_state.boxorder = '1 2 3'
        hashed_board_state.goalorder = '3 2 1'
        hashed_board_state.enable_sokoban_plus()
        initial_box_hash = hashed_board_state.boxes_layout_hash
        initial_pus_hash = hashed_board_state.boxes_and_pushers_layout_hash

        hashed_board_state.boxorder = '1 2 3'
        assert hashed_board_state.boxes_layout_hash == initial_box_hash
        assert hashed_board_state.boxes_and_pushers_layout_hash == initial_pus_hash

        hashed_board_state.goalorder = '3 2 1'
        assert hashed_board_state.boxes_layout_hash == initial_box_hash
        assert hashed_board_state.boxes_and_pushers_layout_hash == initial_pus_hash

    def test_setting_boxorder_or_goalorder_on_disabled_sokoban_plus_doesnt_rehash_board(
        self, hashed_board_state
    ):
        hashed_board_state.disable_sokoban_plus()
        initial_box_hash = hashed_board_state.boxes_layout_hash
        initial_pus_hash = hashed_board_state.boxes_and_pushers_layout_hash

        hashed_board_state.boxorder = '1 2 3'
        assert hashed_board_state.boxes_layout_hash == initial_box_hash
        assert hashed_board_state.boxes_and_pushers_layout_hash == initial_pus_hash

        hashed_board_state.goalorder = '3 2 1'
        assert hashed_board_state.boxes_layout_hash == initial_box_hash
        assert hashed_board_state.boxes_and_pushers_layout_hash == initial_pus_hash

    def test_changing_enabled_state_of_sokoban_plus_rehashes_board(
        self, hashed_board_state
    ):
        hashed_board_state.disable_sokoban_plus()

        initial_box_hash = hashed_board_state.boxes_layout_hash
        initial_pus_hash = hashed_board_state.boxes_and_pushers_layout_hash
        hashed_board_state.enable_sokoban_plus()
        assert hashed_board_state.boxes_layout_hash != initial_box_hash
        assert hashed_board_state.boxes_and_pushers_layout_hash != initial_pus_hash

        initial_box_hash = hashed_board_state.boxes_layout_hash
        initial_pus_hash = hashed_board_state.boxes_and_pushers_layout_hash
        hashed_board_state.disable_sokoban_plus()
        assert hashed_board_state.boxes_layout_hash != initial_box_hash
        assert hashed_board_state.boxes_and_pushers_layout_hash != initial_pus_hash

    def test_enabling_enabled_sokoban_plus_doesnt_rehash_board(
        self, hashed_board_state
    ):
        hashed_board_state.enable_sokoban_plus()

        initial_box_hash = hashed_board_state.boxes_layout_hash
        initial_pus_hash = hashed_board_state.boxes_and_pushers_layout_hash
        hashed_board_state.enable_sokoban_plus()
        assert hashed_board_state.boxes_layout_hash == initial_box_hash
        assert hashed_board_state.boxes_and_pushers_layout_hash == initial_pus_hash

    def test_disabling_disabled_sokoban_plus_doesnt_rehash_board(
        self, hashed_board_state
    ):
        hashed_board_state.disable_sokoban_plus()

        initial_box_hash = hashed_board_state.boxes_layout_hash
        initial_pus_hash = hashed_board_state.boxes_and_pushers_layout_hash
        hashed_board_state.disable_sokoban_plus()
        assert hashed_board_state.boxes_layout_hash == initial_box_hash
        assert hashed_board_state.boxes_and_pushers_layout_hash == initial_pus_hash

    def it_solution_hashes_are_different_for_enabled_and_disabled_sokoban_plus(
        self, hashed_board_state
    ):
        disabled_hashes = deepcopy(hashed_board_state.solution_hashes)

        hashed_board_state.boxorder = '1 3 2'
        hashed_board_state.goalorder = '3 2 1'
        hashed_board_state.enable_sokoban_plus()

        enabled_hashes = deepcopy(hashed_board_state.solution_hashes)

        assert len(disabled_hashes) != 0
        assert len(enabled_hashes) != 0
        assert enabled_hashes != disabled_hashes

    def test_switching_boxes_and_goals_preserves_position_hashes(
        self, hashed_board_state
    ):
        initial_hash = hashed_board_state.boxes_layout_hash
        hashed_board_state.switch_boxes_and_goals()
        after_switch_hash = hashed_board_state.boxes_layout_hash
        assert initial_hash != after_switch_hash

        hashed_board_state.switch_boxes_and_goals()
        assert hashed_board_state.boxes_layout_hash == initial_hash
        hashed_board_state.switch_boxes_and_goals()
        assert hashed_board_state.boxes_layout_hash == after_switch_hash
        hashed_board_state.switch_boxes_and_goals()
        assert hashed_board_state.boxes_layout_hash == initial_hash

    def test_switching_boxes_and_goals_invalidates_solution_hashes(
        self, hashed_board_state
    ):
        initial_solution_hashes = hashed_board_state.solution_hashes
        hashed_board_state.switch_boxes_and_goals()
        after_switch_solution_hashes = hashed_board_state.solution_hashes
        assert initial_solution_hashes != after_switch_solution_hashes

        hashed_board_state.switch_boxes_and_goals()
        assert hashed_board_state.solution_hashes == initial_solution_hashes

        hashed_board_state.switch_boxes_and_goals()
        assert hashed_board_state.solution_hashes == after_switch_solution_hashes
