from itertools import permutations

import pytest

from sokoenginepy import (
    DEFAULT_PIECE_ID, BoardState, CellAlreadyOccupiedError, SokobanBoard,
    SokobanPlus
)


class DescribeBoardState:
    def it_memoizes_pushers(
        self, board_state, pushers_positions, invalid_pusher_position
    ):
        assert board_state.pushers_count == 2
        assert sorted(board_state.pushers_ids) == list(pushers_positions.keys())
        assert board_state.pushers_positions == pushers_positions

        for pusher_id, pusher_position in pushers_positions.items():
            assert board_state.pusher_position(pusher_id) == pusher_position
            assert board_state.pusher_id_on(pusher_position) == pusher_id
            assert board_state.has_pusher(pusher_id) == True
            assert board_state.has_pusher_on(pusher_position) == True

        with pytest.raises(KeyError):
            board_state.pusher_position(
                DEFAULT_PIECE_ID + board_state.pushers_count
            )
        with pytest.raises(KeyError):
            board_state.pusher_id_on(invalid_pusher_position)

        assert board_state.has_pusher(
            DEFAULT_PIECE_ID + board_state.pushers_count
        ) == False
        assert board_state.has_pusher_on(invalid_pusher_position) == False

    def it_memoizes_boxes(
        self, board_state, boxes_positions, boxes_ids, invalid_box_position
    ):
        assert board_state.boxes_count == 6
        assert sorted(board_state.boxes_ids) == boxes_ids
        assert board_state.boxes_positions == boxes_positions

        for box_id, box_position in boxes_positions.items():
            assert board_state.box_position(box_id) == box_position
            assert board_state.box_id_on(box_position) == box_id
            assert board_state.has_box(box_id) == True
            assert board_state.has_box_on(box_position) == True

        with pytest.raises(KeyError):
            board_state.box_position(DEFAULT_PIECE_ID + board_state.boxes_count)
        with pytest.raises(KeyError):
            board_state.box_id_on(invalid_box_position)

        assert board_state.has_box(
            DEFAULT_PIECE_ID + board_state.boxes_count
        ) == False
        assert board_state.has_box_on(invalid_box_position) == False

        for box_id, box_position in boxes_positions.items():
            assert board_state.box_plus_id(
                box_id
            ) == SokobanPlus.DEFAULT_PLUS_ID

        # Doesn't rise KeyError if plus is disabled...
        assert board_state.box_plus_id(
            DEFAULT_PIECE_ID + board_state.boxes_count
        ) == SokobanPlus.DEFAULT_PLUS_ID

        board_state.boxorder = '1 3 2'
        board_state.goalorder = '3 2 1'
        board_state.is_sokoban_plus_enabled = True

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
            ) == SokobanPlus.DEFAULT_PLUS_ID

    def it_memoizes_goals(
        self, board_state, goals_positions, goals_ids, invalid_goal_position
    ):
        assert board_state.goals_count == 6
        assert sorted(board_state.goals_ids) == goals_ids
        assert board_state.goals_positions == goals_positions

        for goal_id, goal_position in goals_positions.items():
            assert board_state.goal_position(goal_id) == goal_position
            assert board_state.goal_id_on(goal_position) == goal_id
            assert board_state.has_goal(goal_id) == True
            assert board_state.has_goal_on(goal_position) == True

        with pytest.raises(KeyError):
            board_state.goal_position(
                DEFAULT_PIECE_ID + board_state.goals_count
            )
        with pytest.raises(KeyError):
            board_state.goal_id_on(invalid_goal_position)

        assert board_state.has_goal(
            DEFAULT_PIECE_ID + board_state.goals_count
        ) == False
        assert board_state.has_goal_on(invalid_goal_position) == False

        for goal_id, goal_position in goals_positions.items():
            assert board_state.goal_plus_id(
                goal_id
            ) == SokobanPlus.DEFAULT_PLUS_ID

        # Doesn't rise KeyError if plus is disabled...
        assert board_state.goal_plus_id(
            DEFAULT_PIECE_ID + board_state.goals_count
        ) == SokobanPlus.DEFAULT_PLUS_ID

        board_state.boxorder = '1 3 2'
        board_state.goalorder = '3 2 1'
        board_state.is_sokoban_plus_enabled = True

        assert board_state.goal_plus_id(DEFAULT_PIECE_ID) == 3
        assert board_state.goal_plus_id(DEFAULT_PIECE_ID + 1) == 2
        assert board_state.goal_plus_id(DEFAULT_PIECE_ID + 2) == 1
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
            ) == SokobanPlus.DEFAULT_PLUS_ID

    def it_calculates_all_valid_board_solutions(self, board_state):
        assert list(board_state.solutions()) == [
            dict((index + DEFAULT_PIECE_ID, box_position)
                 for index, box_position in enumerate(boxes_positions))
            for boxes_positions in
            permutations(board_state.goals_positions.values())
        ]

        board_state.boxorder = '1 3 2'
        board_state.goalorder = '3 2 1'
        board_state.is_sokoban_plus_enabled = True

        assert list(board_state.solutions()) == [{
            1: 149,
            2: 130,
            3: 131,
            4: 150,
            5: 168,
            6: 169
        }, {
            1: 149,
            2: 130,
            3: 131,
            4: 150,
            5: 169,
            6: 168
        }, {
            1: 149,
            2: 130,
            3: 131,
            4: 168,
            5: 150,
            6: 169
        }, {
            1: 149,
            2: 130,
            3: 131,
            4: 168,
            5: 169,
            6: 150
        }, {
            1: 149,
            2: 130,
            3: 131,
            4: 169,
            5: 150,
            6: 168
        }, {
            1: 149,
            2: 130,
            3: 131,
            4: 169,
            5: 168,
            6: 150
        }]

    def test_moving_box_onto_obstacle_raises_exception(self, board_state):
        box_id = DEFAULT_PIECE_ID
        box_position = board_state.box_position(box_id)

        board_state.board[0].put_box()
        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_box(box_id, 0)
        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_box_from(box_position, 0)

        board_state.board[0].put_pusher()
        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_box(box_id, 0)
        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_box_from(box_position, 0)

        board_state.board[0].is_wall = True
        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_box(box_id, 0)
        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_box_from(box_position, 0)

    def test_moving_pusher_onto_obstacle_raises_exception(self, board_state):
        pusher_id = DEFAULT_PIECE_ID
        pusher_position = board_state.pusher_position(pusher_id)

        board_state.board[0].put_box()
        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_pusher(pusher_id, 0)
        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_pusher_from(pusher_position, 0)

        board_state.board[0].put_pusher()
        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_pusher(pusher_id, 0)
        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_pusher_from(pusher_position, 0)

        board_state.board[0].is_wall = True
        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_pusher(pusher_id, 0)
        with pytest.raises(CellAlreadyOccupiedError):
            board_state.move_pusher_from(pusher_position, 0)

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
        board_state.is_sokoban_plus_enabled = True

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

        board_state = BoardState(SokobanBoard(board_str=board_str))

        board_state.switch_boxes_and_goals()
        assert str(board_state.board) == switched_board_str
        board_state.switch_boxes_and_goals()
        assert str(board_state.board) == board_str
