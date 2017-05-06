from copy import deepcopy

import pytest

from sokoenginepy import (DEFAULT_PIECE_ID, AtomicMove, Direction,
                          IllegalMoveError, Mover, NonPlayableBoardError,
                          SolvingMode, index_1d)


class DescribeMover:
    def it_raises_if_board_is_not_playable(self, non_playable_board):
        with pytest.raises(NonPlayableBoardError):
            mover = Mover(non_playable_board)

    def it_assumes_forward_solving_mode(self, forward_board):
        mover = Mover(forward_board)
        assert mover.solving_mode == SolvingMode.FORWARD

    def it_switches_boxes_and_goals_if_reverse_solving_mode_requested(
        self, forward_board, reverse_board
    ):
        mover = Mover(forward_board, SolvingMode.REVERSE)
        assert str(mover.board) == str(reverse_board)

    class DescribeSelectingPusher:
        def it_pre_selects_first_pusher(self, forward_board):
            mover = Mover(forward_board)
            assert mover.selected_pusher == DEFAULT_PIECE_ID

        def it_can_select_pusher_that_will_perform_next_move(
            self, forward_mover
        ):
            forward_mover.selected_pusher = DEFAULT_PIECE_ID
            assert forward_mover.selected_pusher == DEFAULT_PIECE_ID
            forward_mover.selected_pusher = DEFAULT_PIECE_ID + 1
            assert forward_mover.selected_pusher == DEFAULT_PIECE_ID + 1

        def it_raises_if_trying_to_select_non_existant_pusher(
            self, forward_mover
        ):
            with pytest.raises(KeyError):
                forward_mover.selected_pusher = DEFAULT_PIECE_ID + 42

    class DescribeJumping:
        def it_performs_jumps(self, reverse_mover):
            reverse_mover.jump(index_1d(1, 1, reverse_mover.board.width))
            assert (
                reverse_mover.state.pusher_position(DEFAULT_PIECE_ID) ==
                index_1d(1, 1, reverse_mover.board.width)
            )

        def it_refuses_to_jump_in_forward_solving_mode(self, forward_mover):
            with pytest.raises(IllegalMoveError):
                forward_mover.jump(index_1d(1, 1, forward_mover.board.width))

        def it_refuses_to_jump_after_first_pull(self, reverse_mover):
            reverse_mover._pull_count = 42
            with pytest.raises(IllegalMoveError):
                reverse_mover.jump(index_1d(1, 1, reverse_mover.board.width))

        def it_refuses_to_jump_onto_obstacles(self, reverse_mover):
            with pytest.raises(IllegalMoveError):
                reverse_mover.jump(index_1d(0, 0, reverse_mover.board.width))

        def it_refuses_to_jump_off_the_board(self, reverse_mover):
            with pytest.raises(IndexError):
                reverse_mover.jump(index_1d(42, 42, reverse_mover.board.width))

    class DescribeForwardSolwingModeMovement:
        def it_moves_pusher_in_requested_direction(self, forward_mover):
            src = index_1d(4, 2, forward_mover.board.width)
            dest = index_1d(3, 2, forward_mover.board.width)

            forward_mover.move(Direction.LEFT)
            assert forward_mover.state.pusher_position(DEFAULT_PIECE_ID) == dest
            assert not forward_mover.board[src].has_pusher
            assert forward_mover.board[dest].has_pusher

        def it_pushes_box_in_front_of_pusher(self, forward_mover):
            forward_mover.move(Direction.DOWN)
            forward_mover.move(Direction.RIGHT)

            box_src = index_1d(5, 2, forward_mover.board.width)
            box_dest = index_1d(5, 1, forward_mover.board.width)
            pusher_src = index_1d(5, 3, forward_mover.board.width)
            pusher_dest = box_src
            forward_mover.move(Direction.UP)

            assert forward_mover.state.box_position(
                DEFAULT_PIECE_ID + 1
            ) == box_dest
            assert forward_mover.state.pusher_position(
                DEFAULT_PIECE_ID
            ) == pusher_dest

            assert not forward_mover.board[box_src].has_box
            assert not forward_mover.board[pusher_src].has_pusher
            assert forward_mover.board[box_dest].has_box
            assert forward_mover.board[pusher_dest].has_pusher

        def it_refuses_to_move_pusher_into_obstacles(self, forward_mover):
            forward_mover.move(Direction.UP)
            with pytest.raises(IllegalMoveError):
                forward_mover.move(Direction.UP)

        def it_refuses_to_push_two_boxes(self, forward_mover):
            forward_mover.move(Direction.UP)
            forward_mover.move(Direction.RIGHT)
            forward_mover.move(Direction.DOWN)
            forward_mover.selected_pusher = DEFAULT_PIECE_ID + 1
            forward_mover.move(Direction.LEFT)
            forward_mover.move(Direction.LEFT)
            forward_mover.move(Direction.LEFT)
            with pytest.raises(IllegalMoveError):
                forward_mover.move(Direction.LEFT)

        def it_refuses_to_push_box_into_obstacle(self, forward_mover):
            with pytest.raises(IllegalMoveError):
                forward_mover.move(Direction.RIGHT)

    class DescribeReverseSolvingMode:
        def it_moves_pusher_in_requested_direction(self, reverse_mover):
            src = index_1d(4, 2, reverse_mover.board.width)
            dest = index_1d(3, 2, reverse_mover.board.width)

            reverse_mover.move(Direction.LEFT)
            assert reverse_mover.state.pusher_position(DEFAULT_PIECE_ID) == dest
            assert not reverse_mover.board[src].has_pusher
            assert reverse_mover.board[dest].has_pusher

        def it_pulls_box_behind_pusher(self, reverse_mover):
            reverse_mover.pulls_boxes = True

            box_src = index_1d(4, 1, reverse_mover.board.width)
            box_dest = index_1d(4, 2, reverse_mover.board.width)
            pusher_src = box_dest
            pusher_dest = index_1d(4, 3, reverse_mover.board.width)
            reverse_mover.move(Direction.DOWN)

            assert reverse_mover.state.box_position(
                DEFAULT_PIECE_ID
            ) == box_dest
            assert reverse_mover.state.pusher_position(
                DEFAULT_PIECE_ID
            ) == pusher_dest

            assert not reverse_mover.board[box_src].has_box
            assert not reverse_mover.board[pusher_src].has_pusher
            assert reverse_mover.board[box_dest].has_box
            assert reverse_mover.board[pusher_dest].has_pusher

        def it_doesnt_pull_boxes_if_flag_is_not_set(self, reverse_mover):
            reverse_mover.pulls_boxes = False

            box_src = index_1d(4, 1, reverse_mover.board.width)
            pusher_src = index_1d(4, 2, reverse_mover.board.width)
            pusher_dest = index_1d(4, 3, reverse_mover.board.width)

            reverse_mover.move(Direction.DOWN)

            assert reverse_mover.state.box_position(DEFAULT_PIECE_ID) == box_src
            assert reverse_mover.state.pusher_position(
                DEFAULT_PIECE_ID
            ) == pusher_dest

            assert reverse_mover.board[box_src].has_box
            assert not reverse_mover.board[pusher_src].has_box
            assert not reverse_mover.board[pusher_src].has_pusher
            assert reverse_mover.board[pusher_dest].has_pusher

        def it_refuses_to_push_boxes(self, reverse_mover):
            reverse_mover.pulls_boxes = False
            reverse_mover.move(Direction.LEFT)
            reverse_mover.move(Direction.UP)
            with pytest.raises(IllegalMoveError):
                reverse_mover.move(Direction.RIGHT)

        def it_refuses_to_move_pusher_into_obstacles(self, reverse_mover):
            reverse_mover.move(Direction.RIGHT)
            with pytest.raises(IllegalMoveError):
                reverse_mover.move(Direction.RIGHT)

    class DescribePusherSelectionHistory:
        def it_memoizes_last_pusher_selection_into_movement_history(
            self, forward_mover
        ):
            expected_directions = [
                [
                    Direction.DOWN, Direction.RIGHT, Direction.RIGHT,
                    Direction.RIGHT
                ],
                [
                    Direction.RIGHT, Direction.DOWN, Direction.RIGHT,
                    Direction.RIGHT
                ],
                [
                    Direction.RIGHT, Direction.RIGHT, Direction.DOWN,
                    Direction.RIGHT
                ],
                [
                    Direction.RIGHT, Direction.RIGHT, Direction.RIGHT,
                    Direction.DOWN
                ],
            ]

            def initializer(direction):
                retv = AtomicMove(direction)
                retv.is_pusher_selection = True
                return retv

            expected = [
                [initializer(direction) for direction in directions]
                for directions in expected_directions
            ]

            forward_mover.selected_pusher = DEFAULT_PIECE_ID + 1
            assert (
                forward_mover.last_move == expected[0] or
                forward_mover.last_move == expected[1] or
                forward_mover.last_move == expected[2] or
                forward_mover.last_move == expected[3]
            )

        def it_can_undo_and_record_last_pusher_selection(self, forward_mover):
            assert forward_mover.selected_pusher == DEFAULT_PIECE_ID
            forward_mover.selected_pusher = DEFAULT_PIECE_ID + 1
            assert forward_mover.selected_pusher == DEFAULT_PIECE_ID + 1
            forward_mover.undo()

            expected_directions = [
                [
                    Direction.UP, Direction.LEFT, Direction.LEFT, Direction.LEFT
                ],
                [
                    Direction.LEFT, Direction.UP, Direction.LEFT, Direction.LEFT
                ],
                [
                    Direction.LEFT, Direction.LEFT, Direction.UP, Direction.LEFT
                ],
                [
                    Direction.LEFT, Direction.LEFT, Direction.LEFT, Direction.UP
                ],
            ]

            def initializer(direction):
                retv = AtomicMove(direction)
                retv.is_pusher_selection = True
                return retv

            expected = [
                [initializer(direction) for direction in directions]
                for directions in expected_directions
            ]

            assert forward_mover.selected_pusher == DEFAULT_PIECE_ID
            assert (
                forward_mover.last_move == expected[0] or
                forward_mover.last_move == expected[1] or
                forward_mover.last_move == expected[2] or
                forward_mover.last_move == expected[3]
            )

        def it_re_selecting_same_pusher_doesnt_change_last_move(
            self, forward_mover
        ):
            assert forward_mover.selected_pusher == DEFAULT_PIECE_ID

            forward_mover.selected_pusher = DEFAULT_PIECE_ID + 1
            assert forward_mover.selected_pusher == DEFAULT_PIECE_ID + 1
            assert len(forward_mover.last_move) != 0
            last_move = deepcopy(forward_mover.last_move)

            forward_mover.selected_pusher = DEFAULT_PIECE_ID + 1
            assert forward_mover.selected_pusher == DEFAULT_PIECE_ID + 1
            assert forward_mover.last_move == last_move

        def it_doesnt_memoize_failed_pusher_selection(self, forward_mover):
            with pytest.raises(KeyError):
                forward_mover.selected_pusher = DEFAULT_PIECE_ID + 2
            assert forward_mover.selected_pusher == DEFAULT_PIECE_ID
            assert len(forward_mover.last_move) == 0

        def it_failed_pusher_selection_doesnt_change_last_move(
            self, forward_mover
        ):
            forward_mover.selected_pusher = DEFAULT_PIECE_ID + 1
            assert len(forward_mover.last_move) != 0
            assert forward_mover.selected_pusher == DEFAULT_PIECE_ID + 1
            last_move = deepcopy(forward_mover.last_move)

            with pytest.raises(KeyError):
                forward_mover.selected_pusher = DEFAULT_PIECE_ID + 2

            assert forward_mover.selected_pusher == DEFAULT_PIECE_ID + 1
            assert forward_mover.last_move == last_move

    class DescribeJumpingHistory:
        def it_memoizes_last_jump_into_movement_history(self, reverse_mover):
            expected_directions = [
                [
                    Direction.UP, Direction.LEFT, Direction.LEFT,
                    Direction.LEFT
                ],
                [
                    Direction.LEFT, Direction.UP, Direction.LEFT,
                    Direction.LEFT
                ],
                [
                    Direction.LEFT, Direction.LEFT, Direction.UP,
                    Direction.LEFT
                ],
                [
                    Direction.LEFT, Direction.LEFT, Direction.LEFT,
                    Direction.UP
                ]
            ]

            def initializer(direction):
                retv = AtomicMove(direction)
                retv.is_jump = True
                return retv

            expected = [
                [initializer(direction) for direction in directions]
                for directions in expected_directions
            ]

            reverse_mover.jump(index_1d(1, 1, reverse_mover.board.width))
            assert (
                reverse_mover.last_move == expected[0] or
                reverse_mover.last_move == expected[1] or
                reverse_mover.last_move == expected[2] or
                reverse_mover.last_move == expected[3]
            )

        def it_can_undo_and_record_last_jump(self, reverse_mover):
            src = index_1d(4, 2, reverse_mover.board.width)
            dest = index_1d(1, 1, reverse_mover.board.width)
            reverse_mover.jump(dest)

            reverse_mover.undo()
            assert reverse_mover.state.pusher_position(DEFAULT_PIECE_ID) == src
            assert reverse_mover.board[src].has_pusher is True
            assert reverse_mover.board[dest].has_pusher is False

            expected_directions = [
                [
                    Direction.DOWN, Direction.RIGHT, Direction.RIGHT,
                    Direction.RIGHT
                ],
                [
                    Direction.RIGHT, Direction.DOWN, Direction.RIGHT,
                    Direction.RIGHT
                ],
                [
                    Direction.RIGHT, Direction.RIGHT, Direction.DOWN,
                    Direction.RIGHT
                ],
                [
                    Direction.RIGHT, Direction.RIGHT, Direction.RIGHT,
                    Direction.DOWN
                ]
            ]

            def initializer(direction):
                retv = AtomicMove(direction)
                retv.is_jump = True
                return retv

            expected = [
                [initializer(direction) for direction in directions]
                for directions in expected_directions
            ]

            assert (
                reverse_mover.last_move == expected[0] or
                reverse_mover.last_move == expected[1] or
                reverse_mover.last_move == expected[2] or
                reverse_mover.last_move == expected[3]
            )

        def it_jump_to_same_position_doesnt_change_last_move(
            self, reverse_mover
        ):
            reverse_mover.jump(index_1d(1, 1, reverse_mover.board.width))
            assert len(reverse_mover.last_move) > 0
            last_move = deepcopy(reverse_mover.last_move)

            reverse_mover.jump(index_1d(1, 1, reverse_mover.board.width))
            assert reverse_mover.last_move == last_move

        def it_doesnt_memoize_failed_jump(self, reverse_mover):
            with pytest.raises(IllegalMoveError):
                reverse_mover.jump(index_1d(0, 0, reverse_mover.board.width))
            assert len(reverse_mover.last_move) == 0

        def it_failed_jump_doesnt_change_last_move(self, reverse_mover):
            reverse_mover.selected_pusher = DEFAULT_PIECE_ID + 1
            last_move = deepcopy(reverse_mover.last_move)

            with pytest.raises(IllegalMoveError):
                reverse_mover.jump(index_1d(0, 0, reverse_mover.board.width))

            assert reverse_mover.last_move == last_move

    class DescribeForwardMovementHistory:
        def it_memoizes_last_move_or_push(self, forward_mover):
            forward_mover.move(Direction.DOWN)
            assert forward_mover.last_move == [
                AtomicMove(Direction.DOWN, False)
            ]
            forward_mover.move(Direction.RIGHT)
            assert forward_mover.last_move == [
                AtomicMove(Direction.RIGHT, False)
            ]
            forward_mover.move(Direction.UP)
            assert forward_mover.last_move == [
                AtomicMove(Direction.UP, True)
            ]

        def it_can_undo_and_record_last_move_or_push(self, forward_mover):
            src = index_1d(4, 2, forward_mover.board.width)
            dest = index_1d(3, 2, forward_mover.board.width)

            forward_mover.move(Direction.LEFT)
            forward_mover.undo()

            assert forward_mover.state.pusher_position(DEFAULT_PIECE_ID) == src
            assert forward_mover.board[src].has_pusher is True
            assert forward_mover.board[dest].has_pusher is False
            assert forward_mover.last_move == [AtomicMove(Direction.RIGHT)]

        def it_doesnt_memoize_failed_moves_and_pushes(self, forward_mover):
            forward_mover.move(Direction.UP)
            last_move = deepcopy(forward_mover.last_move)
            with pytest.raises(IllegalMoveError):
                forward_mover.move(Direction.UP)
            assert forward_mover.last_move == last_move

            forward_mover.move(Direction.DOWN)
            last_move = deepcopy(forward_mover.last_move)
            with pytest.raises(IllegalMoveError):
                forward_mover.move(Direction.RIGHT)
            assert forward_mover.last_move == last_move

    class DescribeReverseMovementHistory:
        def it_memoizes_last_move_or_pull(self, reverse_mover):
            reverse_mover.move(Direction.RIGHT)
            assert reverse_mover.last_move == [
                AtomicMove(Direction.RIGHT, False)
            ]
            reverse_mover.undo()

            reverse_mover.pulls_boxes = True
            reverse_mover.move(Direction.DOWN)
            assert reverse_mover.last_move == [
                AtomicMove(Direction.DOWN, True)
            ]
            reverse_mover.undo()

            reverse_mover.pulls_boxes = False
            reverse_mover.move(Direction.DOWN)
            assert reverse_mover.last_move == [
                AtomicMove(Direction.DOWN, False)
            ]

        def it_can_undo_and_record_last_move_or_pull(self, reverse_mover):
            src = index_1d(4, 2, reverse_mover.board.width)
            dest = index_1d(3, 2, reverse_mover.board.width)

            reverse_mover.move(Direction.LEFT)
            reverse_mover.undo()
            assert reverse_mover.state.pusher_position(DEFAULT_PIECE_ID) == src
            assert reverse_mover.board[src].has_pusher
            assert not reverse_mover.board[dest].has_pusher
            assert reverse_mover.last_move == [AtomicMove(Direction.RIGHT)]

            reverse_mover.pulls_boxes = True
            box_src = index_1d(4, 1, reverse_mover.board.width)
            box_dest = index_1d(4, 2, reverse_mover.board.width)
            pusher_src = box_dest
            pusher_dest = index_1d(4, 3, reverse_mover.board.width)
            reverse_mover.move(Direction.DOWN)
            reverse_mover.undo()

            assert reverse_mover.state.pusher_position(
                DEFAULT_PIECE_ID
            ) == pusher_src
            assert reverse_mover.board[pusher_src].has_pusher
            assert not reverse_mover.board[pusher_dest].has_pusher

            assert reverse_mover.state.box_position(DEFAULT_PIECE_ID) == box_src
            assert reverse_mover.board[box_src].has_box
            assert not reverse_mover.board[box_dest].has_box
            assert reverse_mover.last_move == [
                AtomicMove(Direction.UP, box_moved=True)
            ]

        def it_doesnt_memoize_failed_moves_and_pulls(self, reverse_mover):
            reverse_mover.pulls_boxes = False
            reverse_mover.move(Direction.DOWN)
            last_move = deepcopy(reverse_mover.last_move)
            with pytest.raises(IllegalMoveError):
                reverse_mover.move(Direction.DOWN)
            assert reverse_mover.last_move == last_move

            reverse_mover.pulls_boxes = True
            reverse_mover.move(Direction.UP)
            reverse_mover.move(Direction.DOWN)
            last_move = deepcopy(reverse_mover.last_move)
            with pytest.raises(IllegalMoveError):
                reverse_mover.move(Direction.DOWN)
            assert reverse_mover.last_move == last_move

        def it_allows_jumps_after_first_pull_is_undone(self, reverse_mover):
            reverse_mover.pulls_boxes = True
            reverse_mover.move(Direction.DOWN)
            assert reverse_mover.last_move[0].is_push_or_pull
            reverse_mover.undo()
            jump_dest = index_1d(1, 1, reverse_mover.board.width)
            reverse_mover.jump(jump_dest)
            assert reverse_mover.board[jump_dest].has_pusher

    class DescribeMoverBenchmark:
        def it_benchmarks_forward_mover(
            self, benchmark, forward_mover, forward_mover_moves_cycle
        ):
            result = benchmark(
                lambda: [
                    forward_mover.move(d)
                    for d in 100*forward_mover_moves_cycle
                ]
            )

        def it_benchmarks_reverse_mover(
            self, benchmark, reverse_mover, reverse_mover_moves_cycle
        ):
            reverse_mover.pulls_boxes = True
            result = benchmark(
                lambda: [
                    reverse_mover.move(d)
                    for d in 100*reverse_mover_moves_cycle
                ]
            )
