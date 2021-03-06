from itertools import permutations

import pytest

from sokoenginepy import (DEFAULT_PIECE_ID, BoardState,
                          CellAlreadyOccupiedError, SokobanBoard, SokobanPlus)


class DescribeBoardState:
    def it_memoizes_pushers(
        self, board_state, pushers_positions, invalid_pusher_position
    ):
        assert board_state.pushers_count == 2
        assert sorted(board_state.pushers_ids
                     ) == list(pushers_positions.keys())
        assert board_state.pushers_positions == pushers_positions

        for pusher_id, pusher_position in pushers_positions.items():
            assert board_state.pusher_position(pusher_id) == pusher_position
            assert board_state.pusher_id_on(pusher_position) == pusher_id
            assert board_state.has_pusher(pusher_id) is True
            assert board_state.has_pusher_on(pusher_position) is True

        with pytest.raises(KeyError):
            board_state.pusher_position(
                DEFAULT_PIECE_ID + board_state.pushers_count
            )
        with pytest.raises(KeyError):
            board_state.pusher_id_on(invalid_pusher_position)

        assert board_state.has_pusher(
            DEFAULT_PIECE_ID + board_state.pushers_count
        ) is False
        assert board_state.has_pusher_on(invalid_pusher_position) is False

    def it_memoizes_boxes(
        self, board_state, boxes_positions, boxes_ids, invalid_box_position
    ):
        assert board_state.boxes_count == 6
        assert sorted(board_state.boxes_ids) == boxes_ids
        assert board_state.boxes_positions == boxes_positions

        for box_id, box_position in boxes_positions.items():
            assert board_state.box_position(box_id) == box_position
            assert board_state.box_id_on(box_position) == box_id
            assert board_state.has_box(box_id) is True
            assert board_state.has_box_on(box_position) is True

        with pytest.raises(KeyError):
            board_state.box_position(
                DEFAULT_PIECE_ID + board_state.boxes_count
            )
        with pytest.raises(KeyError):
            board_state.box_id_on(invalid_box_position)

        assert board_state.has_box(
            DEFAULT_PIECE_ID + board_state.boxes_count
        ) is False
        assert board_state.has_box_on(invalid_box_position) is False

        for box_id, box_position in boxes_positions.items():
            assert board_state.box_plus_id(
                box_id
            ) == SokobanPlus.DEFAULT_PLUS_ID

        # Doesn't rise KeyError if plus is disabled...
        assert board_state.box_plus_id(
            DEFAULT_PIECE_ID + board_state.boxes_count
        ) == SokobanPlus.DEFAULT_PLUS_ID

        board_state.boxorder = '1 3 2'
        board_state.goalorder = '3 1 2'
        board_state.enable_sokoban_plus()

        assert board_state.box_plus_id(DEFAULT_PIECE_ID) == 1
        assert board_state.box_plus_id(DEFAULT_PIECE_ID + 1) == 3
        assert board_state.box_plus_id(DEFAULT_PIECE_ID + 2) == 2
        assert board_state.box_plus_id(
            DEFAULT_PIECE_ID + 3
        ) == SokobanPlus.DEFAULT_PLUS_ID
        assert board_state.box_plus_id(
            DEFAULT_PIECE_ID + 4
        ) == SokobanPlus.DEFAULT_PLUS_ID
        assert board_state.box_plus_id(
            DEFAULT_PIECE_ID + 5
        ) == SokobanPlus.DEFAULT_PLUS_ID

        with pytest.raises(KeyError):
            assert board_state.box_plus_id(
                DEFAULT_PIECE_ID + board_state.boxes_count
            )

    def it_memoizes_goals(
        self, board_state, goals_positions, goals_ids, invalid_goal_position
    ):
        assert board_state.goals_count == 6
        assert sorted(board_state.goals_ids) == goals_ids
        assert board_state.goals_positions == goals_positions

        for goal_id, goal_position in goals_positions.items():
            assert board_state.goal_position(goal_id) == goal_position
            assert board_state.goal_id_on(goal_position) == goal_id
            assert board_state.has_goal(goal_id) is True
            assert board_state.has_goal_on(goal_position) is True

        with pytest.raises(KeyError):
            board_state.goal_position(
                DEFAULT_PIECE_ID + board_state.goals_count
            )
        with pytest.raises(KeyError):
            board_state.goal_id_on(invalid_goal_position)

        assert board_state.has_goal(
            DEFAULT_PIECE_ID + board_state.goals_count
        ) is False
        assert board_state.has_goal_on(invalid_goal_position) is False

        for goal_id, goal_position in goals_positions.items():
            assert board_state.goal_plus_id(
                goal_id
            ) == SokobanPlus.DEFAULT_PLUS_ID

        # Doesn't rise KeyError if plus is disabled...
        assert board_state.goal_plus_id(
            DEFAULT_PIECE_ID + board_state.goals_count
        ) == SokobanPlus.DEFAULT_PLUS_ID

        board_state.boxorder = '1 3 2'
        board_state.goalorder = '3 1 2'
        board_state.enable_sokoban_plus()

        assert board_state.goal_plus_id(DEFAULT_PIECE_ID) == 3
        assert board_state.goal_plus_id(DEFAULT_PIECE_ID + 1) == 1
        assert board_state.goal_plus_id(DEFAULT_PIECE_ID + 2) == 2
        assert board_state.goal_plus_id(
            DEFAULT_PIECE_ID + 3
        ) == SokobanPlus.DEFAULT_PLUS_ID
        assert board_state.goal_plus_id(
            DEFAULT_PIECE_ID + 4
        ) == SokobanPlus.DEFAULT_PLUS_ID
        assert board_state.goal_plus_id(
            DEFAULT_PIECE_ID + 5
        ) == SokobanPlus.DEFAULT_PLUS_ID

        with pytest.raises(KeyError):
            assert board_state.goal_plus_id(
                DEFAULT_PIECE_ID + board_state.goals_count
            )

    def it_calculates_all_valid_board_solutions(
        self, board_state, all_solutions, sokoban_plus_solutions
    ):
        assert list(board_state.solutions()) == all_solutions

        board_state.boxorder = '1 3 2'
        board_state.goalorder = '3 2 1'
        board_state.enable_sokoban_plus()

        assert list(board_state.solutions()) == sokoban_plus_solutions

    def it_moves_boxes(self, board_state):
        old_box_position = board_state.box_position(DEFAULT_PIECE_ID)
        board_state.move_box(DEFAULT_PIECE_ID, 0)
        assert board_state.box_position(DEFAULT_PIECE_ID) == 0
        assert board_state.has_box_on(0)
        assert not board_state.has_box_on(old_box_position)
        assert board_state.board[0].has_box
        assert not board_state.board[old_box_position].has_box
        board_state.move_box(DEFAULT_PIECE_ID, old_box_position)

        board_state.move_box_from(old_box_position, 0)
        assert board_state.box_position(DEFAULT_PIECE_ID) == 0
        assert board_state.has_box_on(0)
        assert not board_state.has_box_on(old_box_position)
        assert board_state.board[0].has_box
        assert not board_state.board[old_box_position].has_box

    def it_moves_pushers(self, board_state):
        old_pusher_position = board_state.pusher_position(DEFAULT_PIECE_ID)
        board_state.move_pusher(DEFAULT_PIECE_ID, 0)
        assert board_state.pusher_position(DEFAULT_PIECE_ID) == 0
        assert board_state.has_pusher_on(0)
        assert not board_state.has_pusher_on(old_pusher_position)
        assert board_state.board[0].has_pusher
        assert not board_state.board[old_pusher_position].has_pusher
        board_state.move_pusher(DEFAULT_PIECE_ID, old_pusher_position)

        board_state.move_pusher_from(old_pusher_position, 0)
        assert board_state.pusher_position(DEFAULT_PIECE_ID) == 0
        assert board_state.has_pusher_on(0)
        assert not board_state.has_pusher_on(old_pusher_position)
        assert board_state.board[0].has_pusher
        assert not board_state.board[old_pusher_position].has_pusher

    def test_moving_box_onto_obstacle_raises_exception(
        self, board_state, wall_position, pushers_positions, boxes_positions
    ):
        box_id = DEFAULT_PIECE_ID
        box_position = board_state.box_position(box_id)

        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_box(box_id, boxes_positions[DEFAULT_PIECE_ID + 1])
        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_box_from(
                box_position, boxes_positions[DEFAULT_PIECE_ID + 1]
            )

        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_box(box_id, pushers_positions[DEFAULT_PIECE_ID])
        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_box_from(
                box_position, pushers_positions[DEFAULT_PIECE_ID]
            )

        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_box(box_id, wall_position)
        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_box_from(box_position, wall_position)

    def test_moving_pusher_onto_obstacle_raises_exception(
        self, board_state, wall_position, boxes_positions, pushers_positions
    ):
        pusher_id = DEFAULT_PIECE_ID
        pusher_position = board_state.pusher_position(pusher_id)

        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_pusher(
                pusher_id, boxes_positions[DEFAULT_PIECE_ID]
            )
        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_pusher_from(
                pusher_position, boxes_positions[DEFAULT_PIECE_ID]
            )

        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_pusher(
                pusher_id, pushers_positions[DEFAULT_PIECE_ID + 1]
            )
        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_pusher_from(
                pusher_position, pushers_positions[DEFAULT_PIECE_ID + 1]
            )

        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_pusher(pusher_id, wall_position)
        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_pusher_from(pusher_position, wall_position)

    def it_implements_switching_box_and_goal_positions(
        self, board_state, boxes_positions, switched_boxes, goals_positions,
        switched_goals, board_str, switched_board_str
    ):
        board_state.switch_boxes_and_goals()
        assert board_state.boxes_positions == switched_boxes
        assert board_state.goals_positions == switched_goals
        assert str(board_state.board) == switched_board_str

        board_state.switch_boxes_and_goals()
        assert board_state.boxes_positions == boxes_positions
        assert board_state.goals_positions == goals_positions
        assert str(board_state.board) == board_str

    def test_switching_respects_sokoban_plus_if_enabled(
        self, board_state, switched_boxes_plus, switched_goals_plus,
        boxes_positions, goals_positions
    ):
        board_state.boxorder = '1 3 2'
        board_state.goalorder = '3 2 1'
        board_state.enable_sokoban_plus()

        board_state.switch_boxes_and_goals()
        assert board_state.boxes_positions == switched_boxes_plus
        assert board_state.goals_positions == switched_goals_plus

        result = board_state.switch_boxes_and_goals()
        assert board_state.boxes_positions == boxes_positions
        assert board_state.goals_positions == goals_positions

    def test_switching_moves_pusher_out_of_the_way(self):
        board_str = "\n".join([
            "########",
            "#      #",
            "#  +   #",
            "#    $ #",
            "########",
        ])
        switched_board_str = "\n".join([
            "########",
            "#      #",
            "#  $   #",
            "#    + #",
            "########",
        ])

        b = SokobanBoard(board_str=board_str)
        board_state = BoardState(b)

        board_state.switch_boxes_and_goals()
        assert str(board_state.board) == switched_board_str
        board_state.switch_boxes_and_goals()
        assert str(board_state.board) == board_str
