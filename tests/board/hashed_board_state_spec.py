from sokoenginepy.common import DEFAULT_PIECE_ID


class DescribeHashedBoardState:

    def it_hashes_board_layout(self, hashed_board_state):
        assert hashed_board_state.position_hash is not None
        assert hashed_board_state._position_with_pushers_hash is not None
        assert hashed_board_state.position_hash != hashed_board_state._position_with_pushers_hash

    def test_moving_box_modifies_hashes_consistently(self, hashed_board_state):
        initial_box_hash = hashed_board_state.position_hash
        initial_pus_hash = hashed_board_state._position_with_pushers_hash

        initial_box_position = hashed_board_state.box_position(DEFAULT_PIECE_ID)
        new_box_position = initial_box_position + 1

        hashed_board_state.move_box(initial_box_position, new_box_position)
        assert hashed_board_state.position_hash != initial_box_hash
        assert hashed_board_state._position_with_pushers_hash != initial_pus_hash

        hashed_board_state.move_box(new_box_position, initial_box_position)
        assert hashed_board_state.position_hash == initial_box_hash
        assert hashed_board_state._position_with_pushers_hash == initial_pus_hash

        hashed_board_state.move_box_id(DEFAULT_PIECE_ID, new_box_position)
        assert hashed_board_state.position_hash != initial_box_hash
        assert hashed_board_state._position_with_pushers_hash != initial_pus_hash

        hashed_board_state.move_box_id(DEFAULT_PIECE_ID, initial_box_position)
        assert hashed_board_state.position_hash == initial_box_hash
        assert hashed_board_state._position_with_pushers_hash == initial_pus_hash

    def test_moving_pusher_modifies_hashes_consistently(self, hashed_board_state):
        initial_box_hash = hashed_board_state.position_hash
        initial_pus_hash = hashed_board_state._position_with_pushers_hash

        initial_pusher_position = hashed_board_state.pusher_position(DEFAULT_PIECE_ID)
        new_pusher_position = initial_pusher_position + 1

        hashed_board_state.move_pusher(initial_pusher_position, new_pusher_position)
        assert hashed_board_state.position_hash == initial_box_hash
        assert hashed_board_state._position_with_pushers_hash != initial_pus_hash

        hashed_board_state.move_pusher(new_pusher_position, initial_pusher_position)
        assert hashed_board_state.position_hash == initial_box_hash
        assert hashed_board_state._position_with_pushers_hash == initial_pus_hash

        hashed_board_state.move_pusher_id(DEFAULT_PIECE_ID, new_pusher_position)
        assert hashed_board_state.position_hash == initial_box_hash
        assert hashed_board_state._position_with_pushers_hash != initial_pus_hash

        hashed_board_state.move_pusher_id(DEFAULT_PIECE_ID, initial_pusher_position)
        assert hashed_board_state.position_hash == initial_box_hash
        assert hashed_board_state._position_with_pushers_hash == initial_pus_hash

    def test_setting_boxorder_or_goalorder_on_enabled_sokoban_plus_rehashes_board(
        self, hashed_board_state
    ):
        initial_box_hash = hashed_board_state.position_hash
        initial_pus_hash = hashed_board_state._position_with_pushers_hash
        hashed_board_state.is_sokoban_plus_enabled = True
        assert hashed_board_state.is_sokoban_plus_enabled == True
        hashed_board_state.boxorder = '1 2 3'
        assert hashed_board_state.position_hash != initial_box_hash
        assert hashed_board_state._position_with_pushers_hash != initial_pus_hash

        hashed_board_state.boxorder = None
        initial_box_hash = hashed_board_state.position_hash
        initial_pus_hash = hashed_board_state._position_with_pushers_hash
        hashed_board_state.is_sokoban_plus_enabled = True
        assert hashed_board_state.is_sokoban_plus_enabled == True
        hashed_board_state.goalorder = '1 2 3'
        assert hashed_board_state.position_hash != initial_box_hash
        assert hashed_board_state._position_with_pushers_hash != initial_pus_hash

    def test_setting_equal_boxorder_or_goalorder_on_enabled_sokoban_plus_doesnt_rehash_board(
        self, hashed_board_state
    ):
        hashed_board_state.boxorder = '1 2 3'
        hashed_board_state.goalorder = '3 2 1'
        hashed_board_state.is_sokoban_plus_enabled = True
        initial_box_hash = hashed_board_state.position_hash
        initial_pus_hash = hashed_board_state._position_with_pushers_hash

        hashed_board_state.boxorder = '1 2 3'
        assert hashed_board_state.position_hash == initial_box_hash
        assert hashed_board_state._position_with_pushers_hash == initial_pus_hash

        hashed_board_state.goalorder = '3 2 1'
        assert hashed_board_state.position_hash == initial_box_hash
        assert hashed_board_state._position_with_pushers_hash == initial_pus_hash

    def test_setting_boxorder_or_goalorder_on_disabled_sokoban_plus_doesnt_rehash_board(
        self, hashed_board_state
    ):
        hashed_board_state.is_sokoban_plus_enabled = False
        initial_box_hash = hashed_board_state.position_hash
        initial_pus_hash = hashed_board_state._position_with_pushers_hash

        hashed_board_state.boxorder = '1 2 3'
        assert hashed_board_state.position_hash == initial_box_hash
        assert hashed_board_state._position_with_pushers_hash == initial_pus_hash

        hashed_board_state.goalorder = '3 2 1'
        assert hashed_board_state.position_hash == initial_box_hash
        assert hashed_board_state._position_with_pushers_hash == initial_pus_hash

    def test_changing_enabled_state_of_sokoban_plus_rehashes_board(
        self, hashed_board_state
    ):
        hashed_board_state.is_sokoban_plus_enabled = False

        initial_box_hash = hashed_board_state.position_hash
        initial_pus_hash = hashed_board_state._position_with_pushers_hash
        hashed_board_state.is_sokoban_plus_enabled = True
        assert hashed_board_state.position_hash != initial_box_hash
        assert hashed_board_state._position_with_pushers_hash != initial_pus_hash

        initial_box_hash = hashed_board_state.position_hash
        initial_pus_hash = hashed_board_state._position_with_pushers_hash
        hashed_board_state.is_sokoban_plus_enabled = False
        assert hashed_board_state.position_hash != initial_box_hash
        assert hashed_board_state._position_with_pushers_hash != initial_pus_hash

    def test_enabling_enabled_sokoban_plus_doesnt_rehash_board(
        self, hashed_board_state
    ):
        hashed_board_state.is_sokoban_plus_enabled = True

        initial_box_hash = hashed_board_state.position_hash
        initial_pus_hash = hashed_board_state._position_with_pushers_hash
        hashed_board_state.is_sokoban_plus_enabled = True
        assert hashed_board_state.position_hash == initial_box_hash
        assert hashed_board_state._position_with_pushers_hash == initial_pus_hash

    def test_disbling_disabled_sokoban_plus_doesnt_rehash_board(
        self, hashed_board_state
    ):
        hashed_board_state.is_sokoban_plus_enabled = False

        initial_box_hash = hashed_board_state.position_hash
        initial_pus_hash = hashed_board_state._position_with_pushers_hash
        hashed_board_state.is_sokoban_plus_enabled = False
        assert hashed_board_state.position_hash == initial_box_hash
        assert hashed_board_state._position_with_pushers_hash == initial_pus_hash
