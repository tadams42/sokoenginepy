import textwrap
from copy import deepcopy

import pytest

from sokoenginepy.game import BoardGraph, Config, HashedBoardManager
from sokoenginepy.io import SokobanPuzzle


@pytest.fixture
def puzzle():
    #   0123456789012345678
    data = """
        ----#####----------
        ----#--@#----------
        ----#$--#----------
        --###--$##---------
        --#--$-$-#---------
        ###-#-##-#---######
        #---#-##-#####--..#
        #-$--$----------..#
        #####-###-#@##--..#
        ----#-----#########
        ----#######--------
    """
    data = textwrap.dedent(data)
    return SokobanPuzzle(board=data)


@pytest.fixture
def board_graph(puzzle):
    return BoardGraph(puzzle)


class DescribeHashedBoardManager:
    def it_hashes_board_layout(self, board_graph):
        hashed_board_manager = HashedBoardManager(board_graph)

        assert hashed_board_manager.state_hash is not None

    def test_moving_box_modifies_hashes_consistently(self, board_graph):
        hashed_board_manager = HashedBoardManager(board_graph)

        initial_state_hash = hashed_board_manager.state_hash

        initial_box_position = hashed_board_manager.box_position(Config.DEFAULT_ID)
        new_box_position = initial_box_position + 1

        hashed_board_manager.move_box_from(initial_box_position, new_box_position)
        assert hashed_board_manager.state_hash != initial_state_hash

        hashed_board_manager.move_box_from(new_box_position, initial_box_position)
        assert hashed_board_manager.state_hash == initial_state_hash

        hashed_board_manager.move_box(Config.DEFAULT_ID, new_box_position)
        assert hashed_board_manager.state_hash != initial_state_hash

        hashed_board_manager.move_box(Config.DEFAULT_ID, initial_box_position)
        assert hashed_board_manager.state_hash == initial_state_hash

    def test_moving_pusher_modifies_hashes_consistently(self, board_graph):
        hashed_board_manager = HashedBoardManager(board_graph)

        initial_state_hash = hashed_board_manager.state_hash

        initial_pusher_position = hashed_board_manager.pusher_position(
            Config.DEFAULT_ID
        )
        new_pusher_position = initial_pusher_position - 1

        hashed_board_manager.move_pusher_from(
            initial_pusher_position, new_pusher_position
        )
        hashed_board_manager.move_pusher_from(
            new_pusher_position, initial_pusher_position
        )
        assert hashed_board_manager.state_hash == initial_state_hash

        hashed_board_manager.move_pusher(Config.DEFAULT_ID, new_pusher_position)
        hashed_board_manager.move_pusher(Config.DEFAULT_ID, initial_pusher_position)
        assert hashed_board_manager.state_hash == initial_state_hash

    def test_setting_boxorder_or_goalorder_on_enabled_sokoban_plus_rehashes_board(
        self, board_graph
    ):
        hashed_board_manager = HashedBoardManager(board_graph)

        initial_state_hash = hashed_board_manager.state_hash
        hashed_board_manager.enable_sokoban_plus()
        assert hashed_board_manager.is_sokoban_plus_enabled is True
        hashed_board_manager.boxorder = "1 2 3"
        assert hashed_board_manager.state_hash != initial_state_hash

        hashed_board_manager.boxorder = ""
        initial_state_hash = hashed_board_manager.state_hash
        hashed_board_manager.enable_sokoban_plus()
        assert hashed_board_manager.is_sokoban_plus_enabled is True
        hashed_board_manager.goalorder = "1 2 3"
        assert hashed_board_manager.state_hash != initial_state_hash

    def test_setting_equal_boxorder_or_goalorder_on_enabled_sokoban_plus_doesnt_rehash_board(
        self, board_graph
    ):
        hashed_board_manager = HashedBoardManager(board_graph)

        hashed_board_manager.boxorder = "1 2 3"
        hashed_board_manager.goalorder = "3 2 1"
        hashed_board_manager.enable_sokoban_plus()
        initial_state_hash = hashed_board_manager.state_hash

        hashed_board_manager.boxorder = "1 2 3"
        assert hashed_board_manager.state_hash == initial_state_hash

        hashed_board_manager.goalorder = "3 2 1"
        assert hashed_board_manager.state_hash == initial_state_hash

    def test_setting_boxorder_or_goalorder_on_disabled_sokoban_plus_doesnt_rehash_board(
        self, board_graph
    ):
        hashed_board_manager = HashedBoardManager(board_graph)

        hashed_board_manager.disable_sokoban_plus()
        initial_state_hash = hashed_board_manager.state_hash

        hashed_board_manager.boxorder = "1 2 3"
        assert hashed_board_manager.state_hash == initial_state_hash

        hashed_board_manager.goalorder = "3 2 1"
        assert hashed_board_manager.state_hash == initial_state_hash

    def test_changing_enabled_state_of_sokoban_plus_rehashes_board(self, board_graph):
        hashed_board_manager = HashedBoardManager(board_graph)

        hashed_board_manager.disable_sokoban_plus()

        initial_state_hash = hashed_board_manager.state_hash
        hashed_board_manager.enable_sokoban_plus()
        assert hashed_board_manager.state_hash != initial_state_hash

        initial_state_hash = hashed_board_manager.state_hash
        hashed_board_manager.disable_sokoban_plus()
        assert hashed_board_manager.state_hash != initial_state_hash

    def test_enabling_enabled_sokoban_plus_doesnt_rehash_board(self, board_graph):
        hashed_board_manager = HashedBoardManager(board_graph)

        hashed_board_manager.enable_sokoban_plus()

        initial_state_hash = hashed_board_manager.state_hash
        hashed_board_manager.enable_sokoban_plus()
        assert hashed_board_manager.state_hash == initial_state_hash

    def test_disabling_disabled_sokoban_plus_doesnt_rehash_board(self, board_graph):
        hashed_board_manager = HashedBoardManager(board_graph)

        hashed_board_manager.disable_sokoban_plus()

        initial_state_hash = hashed_board_manager.state_hash
        hashed_board_manager.disable_sokoban_plus()
        assert hashed_board_manager.state_hash == initial_state_hash

    def test_solutions_hashes_are_different_for_enabled_and_disabled_sokoban_plus(
        self, board_graph
    ):
        hashed_board_manager = HashedBoardManager(board_graph)

        disabled_hashes = deepcopy(hashed_board_manager.solutions_hashes)

        hashed_board_manager.boxorder = "1 3 2"
        hashed_board_manager.goalorder = "3 2 1"
        hashed_board_manager.enable_sokoban_plus()

        enabled_hashes = deepcopy(hashed_board_manager.solutions_hashes)

        assert len(disabled_hashes) != 0
        assert len(enabled_hashes) != 0
        assert enabled_hashes != disabled_hashes

    def test_switching_boxes_and_goals_switches_between_positions_hashes(
        self, board_graph
    ):
        hashed_board_manager = HashedBoardManager(board_graph)

        initial_hash = hashed_board_manager.state_hash
        hashed_board_manager.switch_boxes_and_goals()
        after_switch_hash = hashed_board_manager.state_hash
        assert initial_hash != after_switch_hash

        hashed_board_manager.switch_boxes_and_goals()
        assert hashed_board_manager.state_hash == initial_hash
        hashed_board_manager.switch_boxes_and_goals()
        assert hashed_board_manager.state_hash == after_switch_hash
        hashed_board_manager.switch_boxes_and_goals()
        assert hashed_board_manager.state_hash == initial_hash
