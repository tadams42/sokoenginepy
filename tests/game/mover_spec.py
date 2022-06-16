from copy import deepcopy
from itertools import permutations

import pytest

from sokoenginepy.game import (
    Config,
    PusherStep,
    BoardGraph,
    Direction,
    IllegalMoveError,
    Mover,
    NonPlayableBoardError,
    SolvingMode,
    index_1d,
)
from sokoenginepy.io import SokobanPuzzle


@pytest.fixture
def non_playable_board():
    return BoardGraph(SokobanPuzzle(5, 5))


@pytest.fixture
def off_board_position():
    return index_1d(42, 42, 42)


@pytest.fixture
def forward_board():
    data = "\n".join(
        [
            # 12345678
            "#########",  # 0
            "#$  .  .#",  # 1
            "#   @$# #",  # 2
            "#.$    @#",  # 3
            "#########",  # 4
        ]
    )
    return BoardGraph(SokobanPuzzle(board=data))


@pytest.fixture
def reverse_board():
    data = "\n".join(
        [
            # 12345678
            "#########",  # 0
            "#.  $  $#",  # 1
            "#   @.# #",  # 2
            "#$.    @#",  # 3
            "#########",  # 4
        ]
    )
    return BoardGraph(SokobanPuzzle(board=data))


@pytest.fixture
def forward_mover_moves_cycle():
    return [
        Direction.LEFT,
        Direction.LEFT,
        Direction.LEFT,
        Direction.DOWN,
        Direction.RIGHT,
        Direction.UP,
        Direction.RIGHT,
        Direction.RIGHT,
        Direction.DOWN,
        Direction.LEFT,
        Direction.UP,
        Direction.RIGHT,
    ]


@pytest.fixture
def reverse_mover_moves_cycle():
    return [
        Direction.LEFT,
        Direction.UP,
        Direction.LEFT,
        Direction.DOWN,
        Direction.RIGHT,
        Direction.RIGHT,
        Direction.UP,
        Direction.RIGHT,
        Direction.DOWN,
        Direction.LEFT,
    ]


@pytest.fixture
def jumps():
    return [
        [PusherStep(direction, is_jump=True) for direction in permutation]
        for permutation in permutations(
            [Direction.UP, Direction.LEFT, Direction.LEFT, Direction.LEFT]
        )
    ]


@pytest.fixture
def undone_jumps():
    return [
        [PusherStep(direction, is_jump=True) for direction in permutation]
        for permutation in permutations(
            [Direction.DOWN, Direction.RIGHT, Direction.RIGHT, Direction.RIGHT]
        )
    ]


@pytest.fixture
def pusher_selections():
    return [
        [PusherStep(direction, is_pusher_selection=True) for direction in permutation]
        for permutation in permutations(
            [Direction.DOWN, Direction.RIGHT, Direction.RIGHT, Direction.RIGHT]
        )
    ]


@pytest.fixture
def undone_pusher_selections():
    return [
        [PusherStep(direction, is_pusher_selection=True) for direction in permutation]
        for permutation in permutations(
            [Direction.UP, Direction.LEFT, Direction.LEFT, Direction.LEFT]
        )
    ]


@pytest.fixture
def jump_dest(reverse_board):
    return index_1d(1, 1, reverse_board.board_width)


@pytest.fixture
def jump_obstacle_position(reverse_board):
    return index_1d(0, 0, reverse_board.board_width)


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
            assert mover.selected_pusher == Config.DEFAULT_PIECE_ID

        def it_can_select_pusher_that_will_perform_next_move(self, forward_board):
            forward_mover = Mover(forward_board)

            forward_mover.select_pusher(Config.DEFAULT_PIECE_ID + 1)
            assert forward_mover.selected_pusher == Config.DEFAULT_PIECE_ID + 1
            for am in forward_mover.last_move:
                assert am.pusher_id == Config.DEFAULT_PIECE_ID
                assert am.moved_box_id == None

        def it_raises_if_trying_to_select_non_existent_pusher(self, forward_board):
            forward_mover = Mover(forward_board)

            with pytest.raises(KeyError):
                forward_mover.select_pusher(Config.DEFAULT_PIECE_ID + 42)

        def it_updates_last_move_with_pusher_selection_sequence(
            self, forward_board, pusher_selections
        ):
            forward_mover = Mover(forward_board)

            forward_mover.select_pusher(Config.DEFAULT_PIECE_ID + 1)
            assert forward_mover.last_move in pusher_selections

        def when_re_selecting_same_pusher_it_doesnt_update_last_move(
            self, forward_board, pusher_selections
        ):
            forward_mover = Mover(forward_board)

            forward_mover.select_pusher(Config.DEFAULT_PIECE_ID + 1)
            last_move = deepcopy(forward_mover.last_move)
            assert last_move in pusher_selections
            forward_mover.select_pusher(Config.DEFAULT_PIECE_ID + 1)
            assert forward_mover.last_move == last_move

        def it_doesnt_update_last_move_for_failed_pusher_selection(self, forward_board):
            forward_mover = Mover(forward_board)

            last_move = deepcopy(forward_mover.last_move)
            with pytest.raises(KeyError):
                forward_mover.select_pusher(Config.DEFAULT_PIECE_ID + 2)
            assert forward_mover.last_move == last_move

            forward_mover.select_pusher(Config.DEFAULT_PIECE_ID + 1)
            last_move = deepcopy(forward_mover.last_move)
            with pytest.raises(KeyError):
                forward_mover.select_pusher(Config.DEFAULT_PIECE_ID + 2)
            assert forward_mover.last_move == last_move

        def it_undoes_pusher_selection_and_updates_last_move(
            self, forward_board, undone_pusher_selections
        ):
            forward_mover = Mover(forward_board)

            assert forward_mover.selected_pusher == Config.DEFAULT_PIECE_ID
            forward_mover.select_pusher(Config.DEFAULT_PIECE_ID + 1)
            assert forward_mover.selected_pusher == Config.DEFAULT_PIECE_ID + 1
            forward_mover.undo_last_move()

            assert forward_mover.selected_pusher == Config.DEFAULT_PIECE_ID
            assert forward_mover.last_move in undone_pusher_selections
            for am in forward_mover.last_move:
                assert am.pusher_id == Config.DEFAULT_PIECE_ID
                assert am.moved_box_id == None

    class DescribeJumping:
        def it_performs_jumps(self, forward_board, jump_dest):
            reverse_mover = Mover(forward_board, SolvingMode.REVERSE)

            reverse_mover.jump(jump_dest)
            assert (
                reverse_mover.board_manager.pusher_position(Config.DEFAULT_PIECE_ID)
                == jump_dest
            )
            for am in reverse_mover.last_move:
                assert am.pusher_id == Config.DEFAULT_PIECE_ID
                assert am.moved_box_id == None

        def it_refuses_to_jump_in_forward_solving_mode(self, forward_board, jump_dest):
            forward_mover = Mover(forward_board)

            with pytest.raises(IllegalMoveError):
                forward_mover.jump(jump_dest)
            assert not forward_mover.last_move

        def it_refuses_to_jump_after_first_pull(self, forward_board, jump_dest):
            reverse_mover = Mover(forward_board, SolvingMode.REVERSE)

            reverse_mover.pulls_boxes = True
            reverse_mover.move(Direction.DOWN)
            reverse_mover.last_move = None
            with pytest.raises(IllegalMoveError):
                reverse_mover.jump(jump_dest)
            assert not reverse_mover.last_move

        def it_allows_jumps_after_first_pull_is_undone(self, forward_board, jump_dest):
            reverse_mover = Mover(forward_board, SolvingMode.REVERSE)

            reverse_mover.pulls_boxes = True
            reverse_mover.move(Direction.DOWN)
            assert reverse_mover.last_move[0].is_push_or_pull
            reverse_mover.undo_last_move()
            reverse_mover.jump(jump_dest)
            assert reverse_mover.board[jump_dest].has_pusher
            for am in reverse_mover.last_move:
                assert am.pusher_id == Config.DEFAULT_PIECE_ID
                assert am.moved_box_id == None

        def it_refuses_to_jump_onto_obstacles(
            self, forward_board, jump_obstacle_position
        ):
            reverse_mover = Mover(forward_board, SolvingMode.REVERSE)

            with pytest.raises(IllegalMoveError):
                reverse_mover.jump(jump_obstacle_position)
            assert not reverse_mover.last_move

        def it_refuses_to_jump_off_the_board(self, forward_board, off_board_position):
            reverse_mover = Mover(forward_board, SolvingMode.REVERSE)

            with pytest.raises(IndexError):
                reverse_mover.jump(off_board_position)
            assert not reverse_mover.last_move

        def it_updates_last_move_with_jump_sequence(
            self, forward_board, jump_dest, jumps
        ):
            reverse_mover = Mover(forward_board, SolvingMode.REVERSE)

            reverse_mover.jump(jump_dest)
            assert reverse_mover.last_move in jumps
            for am in reverse_mover.last_move:
                assert am.pusher_id == Config.DEFAULT_PIECE_ID
                assert am.moved_box_id == None

        def when_jumping_to_same_position_it_doesnt_update_last_move(
            self, forward_board, jump_dest
        ):
            reverse_mover = Mover(forward_board, SolvingMode.REVERSE)

            reverse_mover.jump(jump_dest)
            reverse_mover.last_move = None
            reverse_mover.jump(jump_dest)
            assert not reverse_mover.last_move

        def it_doesnt_update_last_move_for_failed_jumps(
            self, forward_board, jump_dest, jump_obstacle_position
        ):
            reverse_mover = Mover(forward_board, SolvingMode.REVERSE)

            reverse_mover.jump(jump_dest)
            last_move = deepcopy(reverse_mover.last_move)
            with pytest.raises(IllegalMoveError):
                reverse_mover.jump(jump_obstacle_position)
            assert reverse_mover.last_move == last_move

        def it_raises_when_undoing_jump_for_forward_mover(self, forward_board, jumps):
            forward_mover = Mover(forward_board)

            forward_mover.last_move = jumps[0]
            with pytest.raises(IllegalMoveError):
                forward_mover.undo_last_move()
            assert forward_mover.last_move == jumps[0]

        def it_undoes_jump_and_updates_last_move(
            self, forward_board, jump_dest, undone_jumps
        ):
            reverse_mover = Mover(forward_board, SolvingMode.REVERSE)

            src = index_1d(4, 2, reverse_mover.board.board_width)
            reverse_mover.jump(jump_dest)

            reverse_mover.undo_last_move()
            assert reverse_mover.board_manager.pusher_position(Config.DEFAULT_PIECE_ID) == src
            assert reverse_mover.board[src].has_pusher is True
            assert reverse_mover.board[jump_dest].has_pusher is False

            assert reverse_mover.last_move in undone_jumps

    class DescribeForwardMovement:
        def it_forward_moves_pusher_in_requested_direction(self):
            board = BoardGraph(
                SokobanPuzzle(
                    board="\n".join(
                        [
                            # 12345678
                            "#########",  # 0
                            "#@      #",  # 1
                            "#  @ $. #",  # 2
                            "#       #",  # 3
                            "#########",  # 4
                        ]
                    )
                )
            )
            src = index_1d(3, 2, board.board_width)
            dest = index_1d(4, 2, board.board_width)
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover = Mover(board)
            mover.select_pusher(selected_pusher)

            mover.move(Direction.RIGHT)
            assert mover.board_manager.pusher_position(selected_pusher) == dest
            assert not board[src].has_pusher
            assert board[dest].has_pusher
            assert mover.last_move == [PusherStep(Direction.RIGHT)]
            assert mover.last_move[0].pusher_id == selected_pusher
            assert mover.last_move[0].moved_box_id == None

        def when_forward_moving_pusher_doesnt_pull_box_behind_it(self):
            board = BoardGraph(
                SokobanPuzzle(
                    board="\n".join(
                        [
                            # 12345678
                            "#########",  # 0
                            "#@      #",  # 1
                            "# $@ .  #",  # 2
                            "#       #",  # 3
                            "#########",  # 4
                        ]
                    )
                )
            )
            src = index_1d(3, 2, board.board_width)
            dest = index_1d(4, 2, board.board_width)
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover = Mover(board)
            mover.select_pusher(selected_pusher)

            mover.move(Direction.RIGHT)
            assert mover.board_manager.pusher_position(selected_pusher) == dest
            assert not board[src].has_pusher
            assert board[dest].has_pusher
            assert mover.last_move == [PusherStep(Direction.RIGHT)]
            assert mover.last_move[0].pusher_id == selected_pusher
            assert mover.last_move[0].moved_box_id == None

        def it_refuses_to_forward_move_pusher_into_obstacles_or_off_board(self):
            board = BoardGraph(
                SokobanPuzzle(
                    board="\n".join(
                        [
                            # 12345678
                            "#########",  # 0
                            "#@      #",  # 1
                            "@$   .  #",  # 2
                            "@       #",  # 3
                            "#########",  # 4
                        ]
                    )
                )
            )
            src = index_1d(0, 2, board.board_width)
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover = Mover(board)
            mover.select_pusher(selected_pusher)
            last_move = mover.last_move

            for direction in [Direction.UP, Direction.DOWN, Direction.LEFT]:
                with pytest.raises(IllegalMoveError):
                    mover.move(direction)
                assert mover.board_manager.pusher_position(selected_pusher) == src
                assert board[src].has_pusher
                assert mover.last_move == last_move

        def it_undoes_forward_move(self):
            board = BoardGraph(
                SokobanPuzzle(
                    board="\n".join(
                        [
                            # 12345678
                            "#########",  # 0
                            "#@      #",  # 1
                            "#  @ $. #",  # 2
                            "#       #",  # 3
                            "#########",  # 4
                        ]
                    )
                )
            )
            src = index_1d(3, 2, board.board_width)
            dest = index_1d(2, 2, board.board_width)
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover = Mover(board)
            mover.select_pusher(selected_pusher)

            mover.last_move = [PusherStep(Direction.RIGHT)]
            mover.undo_last_move()
            assert mover.board_manager.pusher_position(selected_pusher) == dest
            assert not board[src].has_pusher
            assert board[dest].has_pusher
            assert mover.last_move == [PusherStep(Direction.LEFT)]
            assert mover.last_move[0].pusher_id == selected_pusher
            assert mover.last_move[0].moved_box_id == None

        def when_undoing_forward_move_doesnt_pull_box_from_behind_pusher(self):
            board = BoardGraph(
                SokobanPuzzle(
                    board="\n".join(
                        [
                            # 12345678
                            "#########",  # 0
                            "#@      #",  # 1
                            "#  @$.  #",  # 2
                            "#       #",  # 3
                            "#########",  # 4
                        ]
                    )
                )
            )
            src = index_1d(3, 2, board.board_width)
            dest = index_1d(2, 2, board.board_width)
            mover = Mover(board)
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover.select_pusher(selected_pusher)

            mover.last_move = [PusherStep(Direction.RIGHT)]
            mover.undo_last_move()
            assert mover.board_manager.pusher_position(selected_pusher) == dest
            assert not board[src].has_pusher
            assert board[src + 1].has_box
            assert board[dest].has_pusher
            assert mover.last_move == [PusherStep(Direction.LEFT)]
            assert mover.last_move[0].pusher_id == selected_pusher
            assert mover.last_move[0].moved_box_id == None

        def it_refuses_to_undo_forward_move_by_moving_pusher_into_obstacles_or_off_board(
            self,
        ):
            board = BoardGraph(
                SokobanPuzzle(
                    board="\n".join(
                        [
                            # 12345678
                            "#########",  # 0
                            "#@      #",  # 1
                            "@$   .  #",  # 2
                            "@       #",  # 3
                            "#########",  # 4
                        ]
                    )
                )
            )
            src = index_1d(0, 2, board.board_width)
            mover = Mover(board)
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover.select_pusher(selected_pusher)

            for direction in [
                Direction.DOWN,
                Direction.UP,
                Direction.LEFT,
                Direction.RIGHT,
            ]:
                mover.last_move = [PusherStep(direction)]
                with pytest.raises(IllegalMoveError):
                    mover.undo_last_move()
                assert mover.board_manager.pusher_position(selected_pusher) == src
                assert board[src].has_pusher
                # last move shuould be unchanged
                assert mover.last_move == [PusherStep(direction)]
                assert mover.last_move[0].pusher_id == Config.DEFAULT_PIECE_ID
                assert mover.last_move[0].moved_box_id == None

        def it_pushes_box_in_front_of_pusher(self):
            board = BoardGraph(
                SokobanPuzzle(
                    board="\n".join(
                        [
                            # 12345678
                            "#########",  # 0
                            "#@      #",  # 1
                            "#   @$. #",  # 2
                            "#       #",  # 3
                            "#########",  # 4
                        ]
                    )
                )
            )
            box_src = index_1d(5, 2, board.board_width)
            box_dest = index_1d(6, 2, board.board_width)
            pusher_src = index_1d(4, 2, board.board_width)
            pusher_dest = box_src
            mover = Mover(board)
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover.select_pusher(selected_pusher)

            mover.move(Direction.RIGHT)

            assert mover.board_manager.box_position(Config.DEFAULT_PIECE_ID) == box_dest
            assert mover.board_manager.pusher_position(selected_pusher) == pusher_dest
            assert not mover.board[box_src].has_box
            assert not mover.board[pusher_src].has_pusher
            assert mover.board[box_dest].has_box
            assert mover.board[pusher_dest].has_pusher
            assert mover.last_move == [PusherStep(Direction.RIGHT, box_moved=True)]
            assert mover.last_move[0].pusher_id == selected_pusher
            assert mover.last_move[0].moved_box_id == Config.DEFAULT_PIECE_ID

        def when_pushing_box_doesnt_pull_box_from_behind_pusher(self):
            board = BoardGraph(
                SokobanPuzzle(
                    board="\n".join(
                        [
                            # 12345678
                            "#########",  # 0
                            "#@      #",  # 1
                            "#  $@$..#",  # 2
                            "#       #",  # 3
                            "#########",  # 4
                        ]
                    )
                )
            )
            box_src = index_1d(5, 2, board.board_width)
            box_dest = index_1d(6, 2, board.board_width)
            pusher_src = index_1d(4, 2, board.board_width)
            pusher_dest = box_src
            mover = Mover(board)
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover.select_pusher(selected_pusher)

            mover.move(Direction.RIGHT)

            assert mover.board_manager.box_position(Config.DEFAULT_PIECE_ID + 1) == box_dest
            assert mover.board_manager.pusher_position(selected_pusher) == pusher_dest
            assert not mover.board[box_src].has_box
            assert not mover.board[pusher_src].has_pusher
            assert mover.board[box_dest].has_box
            assert mover.board[pusher_dest].has_pusher
            assert not mover.board[pusher_src].has_box
            assert mover.last_move == [PusherStep(Direction.RIGHT, box_moved=True)]
            assert mover.last_move[0].pusher_id == selected_pusher
            assert mover.last_move[0].moved_box_id == Config.DEFAULT_PIECE_ID + 1

        def it_refuses_to_push_box_into_obstacles_or_off_board(self):
            board = BoardGraph(
                SokobanPuzzle(
                    board="\n".join(
                        [
                            # 12345678
                            "#####$###",  # 0
                            "#@ $$@$##",  # 1
                            "#..  $  #",  # 2
                            "#... @  #",  # 3
                            "#########",  # 4
                        ]
                    )
                )
            )
            pusher_src = index_1d(5, 1, board.board_width)
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover = Mover(board)
            mover.select_pusher(selected_pusher)
            last_move = mover.last_move

            for direction in [
                Direction.UP,
                Direction.DOWN,
                Direction.LEFT,
                Direction.RIGHT,
            ]:
                with pytest.raises(IllegalMoveError):
                    mover.move(direction)

                assert (
                    mover.board_manager.pusher_position(selected_pusher) == pusher_src
                )
                assert board[pusher_src].has_pusher
                assert board[board.neighbor(pusher_src, direction)].has_box
                assert board[board.neighbor(pusher_src, direction.opposite)].has_box
                assert mover.last_move == last_move

        def it_undoes_push(self):
            board = BoardGraph(
                SokobanPuzzle(
                    board="\n".join(
                        [
                            # 12345678
                            "#########",  # 0
                            "#@      #",  # 1
                            "#   @$. #",  # 2
                            "#       #",  # 3
                            "#########",  # 4
                        ]
                    )
                )
            )
            box_src = index_1d(5, 2, board.board_width)
            pusher_src = index_1d(4, 2, board.board_width)
            pusher_dest = pusher_src - 1
            box_dest = box_src - 1
            mover = Mover(board)
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover.select_pusher(selected_pusher)

            mover.last_move = [PusherStep(Direction.RIGHT, box_moved=True)]
            mover.undo_last_move()

            assert mover.board_manager.box_position(Config.DEFAULT_PIECE_ID) == box_dest
            assert mover.board_manager.pusher_position(selected_pusher) == pusher_dest
            assert not mover.board[box_src].has_box
            assert not mover.board[pusher_src].has_pusher
            assert mover.board[box_dest].has_box
            assert mover.board[pusher_dest].has_pusher
            assert mover.last_move == [PusherStep(Direction.LEFT, box_moved=True)]
            assert mover.last_move[0].pusher_id == selected_pusher
            assert mover.last_move[0].moved_box_id == Config.DEFAULT_PIECE_ID

        def it_refuses_to_undo_push_moving_pusher_into_obstacles_or_off_board(self):
            board = BoardGraph(
                SokobanPuzzle(
                    board="\n".join(
                        [
                            # 12345678
                            "#########",  # 0
                            "#@   $..#",  # 1
                            "@$  @@$.#",  # 2
                            "$    $..#",  # 3
                            "#########",  # 4
                        ]
                    )
                )
            )
            pusher_src = index_1d(0, 2, board.board_width)
            mover = Mover(board)
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover.select_pusher(selected_pusher)

            # Undo into off board
            mover.last_move = [PusherStep(Direction.RIGHT, box_moved=True)]
            with pytest.raises(IllegalMoveError):
                mover.undo_last_move()
            assert mover.board_manager.pusher_position(selected_pusher) == pusher_src
            assert board[pusher_src].has_pusher
            assert board[board.neighbor(pusher_src, Direction.RIGHT)].has_box
            assert mover.last_move == [PusherStep(Direction.RIGHT, box_moved=True)]
            assert mover.last_move[0].pusher_id == Config.DEFAULT_PIECE_ID
            assert mover.last_move[0].moved_box_id == None

            # Undo into wall
            mover.last_move = [PusherStep(Direction.DOWN, box_moved=True)]
            with pytest.raises(IllegalMoveError):
                mover.undo_last_move()
            assert mover.board_manager.pusher_position(selected_pusher) == pusher_src
            assert board[pusher_src].has_pusher
            assert board[board.neighbor(pusher_src, Direction.DOWN)].has_box
            assert mover.last_move == [PusherStep(Direction.DOWN, box_moved=True)]
            assert mover.last_move[0].pusher_id == Config.DEFAULT_PIECE_ID
            assert mover.last_move[0].moved_box_id == None

            selected_pusher = Config.DEFAULT_PIECE_ID + 3
            mover.select_pusher(selected_pusher)
            pusher_src = index_1d(5, 2, board.board_width)

            # Undo into pusher
            mover.last_move = [PusherStep(Direction.RIGHT, box_moved=True)]
            with pytest.raises(IllegalMoveError):
                mover.undo_last_move()
            assert mover.board_manager.pusher_position(selected_pusher) == pusher_src
            assert board[pusher_src].has_pusher
            assert board[board.neighbor(pusher_src, Direction.RIGHT)].has_box
            assert mover.last_move == [PusherStep(Direction.RIGHT, box_moved=True)]
            assert mover.last_move[0].pusher_id == Config.DEFAULT_PIECE_ID
            assert mover.last_move[0].moved_box_id == None

            # Undo into box
            mover.last_move = [PusherStep(Direction.DOWN, box_moved=True)]
            with pytest.raises(IllegalMoveError):
                mover.undo_last_move()
            assert mover.board_manager.pusher_position(selected_pusher) == pusher_src
            assert board[pusher_src].has_pusher
            assert board[board.neighbor(pusher_src, Direction.DOWN)].has_box
            assert mover.last_move == [PusherStep(Direction.DOWN, box_moved=True)]
            assert mover.last_move[0].pusher_id == Config.DEFAULT_PIECE_ID
            assert mover.last_move[0].moved_box_id == None

        def it_refuses_to_undo_push_if_there_is_no_box_behind_pusher(self):
            board = BoardGraph(
                SokobanPuzzle(
                    board="\n".join(
                        [
                            # 12345678
                            "#########",  # 0
                            "#@      #",  # 1
                            "#   @ .$#",  # 2
                            "#       #",  # 3
                            "#########",  # 4
                        ]
                    )
                )
            )
            mover = Mover(board)
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover.select_pusher(selected_pusher)

            mover.last_move = [PusherStep(Direction.RIGHT, box_moved=True)]
            with pytest.raises(IllegalMoveError):
                mover.undo_last_move()
            assert mover.last_move == [PusherStep(Direction.RIGHT, box_moved=True)]

    class DescribeReverseMovement:
        def it_moves_pusher_in_requested_direction(self):
            board = BoardGraph(
                SokobanPuzzle(
                    board="\n".join(
                        [
                            # 12345678
                            "#########",  # 0
                            "#@      #",  # 1
                            "#  @ $. #",  # 2
                            "#       #",  # 3
                            "#########",  # 4
                        ]
                    )
                )
            )
            src = index_1d(3, 2, board.board_width)
            dest = index_1d(4, 2, board.board_width)
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover = Mover(board, SolvingMode.REVERSE)
            mover.select_pusher(selected_pusher)

            mover.move(Direction.RIGHT)
            assert mover.board_manager.pusher_position(selected_pusher) == dest
            assert not board[src].has_pusher
            assert board[dest].has_pusher
            assert mover.last_move == [PusherStep(Direction.RIGHT)]
            assert mover.last_move[0].pusher_id == selected_pusher
            assert mover.last_move[0].moved_box_id == None

        def when_reverse_moving_it_doesnt_pull_box_behind_pusher(self):
            board = BoardGraph(
                SokobanPuzzle(
                    board="\n".join(
                        [
                            # 12345678
                            "#########",  # 0
                            "#@      #",  # 1
                            "#  @. $ #",  # 2
                            "#       #",  # 3
                            "#########",  # 4
                        ]
                    )
                )
            )
            src = index_1d(3, 2, board.board_width)
            dest = index_1d(2, 2, board.board_width)
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover = Mover(board, SolvingMode.REVERSE)
            mover.select_pusher(selected_pusher)
            mover.pulls_boxes = False

            mover.move(Direction.LEFT)
            assert mover.board_manager.pusher_position(selected_pusher) == dest
            assert not board[src].has_pusher
            assert board[dest].has_pusher
            assert mover.last_move == [PusherStep(Direction.LEFT)]
            assert mover.last_move[0].pusher_id == selected_pusher
            assert mover.last_move[0].moved_box_id == None

        def it_refuses_to_reverse_move_pusher_into_obstacles_or_off_board(self):
            board = BoardGraph(
                SokobanPuzzle(
                    board="\n".join(
                        [
                            # 12345678
                            "#########",  # 0
                            "#@      #",  # 1
                            "@.   $  #",  # 2
                            "@       #",  # 3
                            "#########",  # 4
                        ]
                    )
                )
            )
            src = index_1d(0, 2, board.board_width)
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover = Mover(board, SolvingMode.REVERSE)
            mover.select_pusher(selected_pusher)
            last_move = mover.last_move

            for direction in [
                Direction.UP,
                Direction.DOWN,
                Direction.LEFT,
                Direction.RIGHT,
            ]:
                with pytest.raises(IllegalMoveError):
                    mover.move(direction)
                assert mover.board_manager.pusher_position(selected_pusher) == src
                assert board[src].has_pusher
                assert mover.last_move == last_move

        def it_undoes_reverse_move(self):
            board = BoardGraph(
                SokobanPuzzle(
                    board="\n".join(
                        [
                            # 12345678
                            "#########",  # 0
                            "#@      #",  # 1
                            "#  @ $. #",  # 2
                            "#       #",  # 3
                            "#########",  # 4
                        ]
                    )
                )
            )
            src = index_1d(3, 2, board.board_width)
            dest = index_1d(4, 2, board.board_width)
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover = Mover(board, SolvingMode.REVERSE)
            mover.select_pusher(selected_pusher)

            mover.last_move = [PusherStep(Direction.LEFT)]
            mover.undo_last_move()
            assert mover.board_manager.pusher_position(selected_pusher) == dest
            assert not board[src].has_pusher
            assert board[dest].has_pusher
            assert mover.last_move == [PusherStep(Direction.RIGHT)]
            assert mover.last_move[0].pusher_id == selected_pusher
            assert mover.last_move[0].moved_box_id == None

        def when_undoing_reverse_move_it_doesnt_pull_box_behind_pusher(self):
            board_str = "\n".join(
                [
                    # 12345678
                    "#########",  # 0
                    "#@      #",  # 1
                    "#  @.$  #",  # 2
                    "#       #",  # 3
                    "#########",  # 4
                ]
            )

            # pulls_boxes == False
            board = BoardGraph(SokobanPuzzle(board=board_str))
            src = index_1d(3, 2, board.board_width)
            dest = index_1d(2, 2, board.board_width)
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover = Mover(board, SolvingMode.REVERSE)
            mover.select_pusher(selected_pusher)

            mover.last_move = [PusherStep(Direction.RIGHT)]
            mover.pulls_boxes = False
            mover.undo_last_move()

            assert mover.board_manager.pusher_position(selected_pusher) == dest
            assert not board[src].has_pusher
            assert not board[src].has_box
            assert board[dest].has_pusher
            assert mover.last_move == [PusherStep(Direction.LEFT)]
            assert mover.last_move[0].pusher_id == selected_pusher
            assert mover.last_move[0].moved_box_id == None

            # pulls_boxes == True
            board = BoardGraph(SokobanPuzzle(board=board_str))
            src = index_1d(3, 2, board.board_width)
            dest = index_1d(2, 2, board.board_width)
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover = Mover(board, SolvingMode.REVERSE)
            mover.select_pusher(selected_pusher)

            mover.last_move = [PusherStep(Direction.RIGHT)]
            mover.pulls_boxes = True
            mover.undo_last_move()

            assert mover.board_manager.pusher_position(selected_pusher) == dest
            assert not board[src].has_pusher
            assert not board[src].has_box
            assert board[dest].has_pusher
            assert mover.last_move == [PusherStep(Direction.LEFT)]
            assert mover.last_move[0].pusher_id == selected_pusher
            assert mover.last_move[0].moved_box_id == None

        def it_pulls_box_behind_pusher_if_pulls_boxes_is_set(self):
            board = BoardGraph(
                SokobanPuzzle(
                    board="\n".join(
                        [
                            # 12345678
                            "#########",  # 0
                            "#@      #",  # 1
                            "#  @.$  #",  # 2
                            "#       #",  # 3
                            "#########",  # 4
                        ]
                    )
                )
            )
            pusher_src = index_1d(3, 2, board.board_width)
            pusher_dest = index_1d(2, 2, board.board_width)
            box_src = index_1d(4, 2, board.board_width)
            box_dest = pusher_src
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover = Mover(board, SolvingMode.REVERSE)
            mover.select_pusher(selected_pusher)

            mover.pulls_boxes = True
            mover.move(Direction.LEFT)

            assert mover.board_manager.pusher_position(selected_pusher) == pusher_dest
            assert mover.board_manager.box_position(Config.DEFAULT_PIECE_ID) == box_dest
            assert board[pusher_dest].has_pusher
            assert not board[pusher_src].has_pusher
            assert board[box_dest].has_box
            assert not board[box_src].has_box
            assert mover.last_move == [PusherStep(Direction.LEFT, box_moved=True)]
            assert mover.last_move[0].pusher_id == selected_pusher
            assert mover.last_move[0].moved_box_id == Config.DEFAULT_PIECE_ID

        def it_refuses_to_pull_box_if_pusher_would_move_into_obstacle_or_off_board(
            self,
        ):
            board = BoardGraph(
                SokobanPuzzle(
                    board="\n".join(
                        [
                            # 12345678
                            "#########",  # 0
                            "#@ $  .$#",  # 1
                            "@. $ @@.#",  # 2
                            ".  $  .$#",  # 3
                            "#########",  # 4
                        ]
                    )
                )
            )
            pusher_src = index_1d(3, 2, board.board_width)
            mover = Mover(board, SolvingMode.REVERSE)
            mover.pulls_boxes = True
            mover.select_pusher(Config.DEFAULT_PIECE_ID + 1)
            mover.last_move = []

            with pytest.raises(IllegalMoveError):
                mover.move(Direction.LEFT)
            assert mover.last_move == []

            with pytest.raises(IllegalMoveError):
                mover.move(Direction.UP)
            assert mover.last_move == []

            mover.select_pusher(Config.DEFAULT_PIECE_ID + 3)
            mover.last_move = []

            with pytest.raises(IllegalMoveError):
                mover.move(Direction.LEFT)
            assert mover.last_move == []

            with pytest.raises(IllegalMoveError):
                mover.move(Direction.UP)
            assert mover.last_move == []

        def it_undoes_pull(self):
            board = BoardGraph(
                SokobanPuzzle(
                    board="\n".join(
                        [
                            # 12345678
                            "#########",  # 0
                            "#@      #",  # 1
                            "#  @.$  #",  # 2
                            "#       #",  # 3
                            "#########",  # 4
                        ]
                    )
                )
            )
            pusher_src = index_1d(3, 2, board.board_width)
            pusher_dest = index_1d(4, 2, board.board_width)
            box_src = pusher_dest
            box_dest = index_1d(5, 2, board.board_width)
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover = Mover(board, SolvingMode.REVERSE)
            mover.select_pusher(selected_pusher)

            mover.last_move = [PusherStep(Direction.LEFT, box_moved=True)]
            mover.undo_last_move()

            assert mover.board_manager.pusher_position(selected_pusher) == pusher_dest
            assert mover.board_manager.box_position(Config.DEFAULT_PIECE_ID) == box_dest
            assert board[pusher_dest].has_pusher
            assert not board[pusher_src].has_pusher
            assert board[box_dest].has_box
            assert not board[box_src].has_box
            assert mover.last_move == [PusherStep(Direction.RIGHT, box_moved=True)]
            assert mover.last_move[0].pusher_id == selected_pusher
            assert mover.last_move[0].moved_box_id == Config.DEFAULT_PIECE_ID

        def it_undoes_pull_not_moving_box_behind_pusher(self):
            board_str = "\n".join(
                [
                    # 12345678
                    "#########",  # 0
                    "#@     $#",  # 1
                    "# .@.$  #",  # 2
                    "#       #",  # 3
                    "#########",  # 4
                ]
            )

            # pulls_boxes == False
            board = BoardGraph(SokobanPuzzle(board=board_str))
            pusher_src = index_1d(3, 2, board.board_width)
            pusher_dest = index_1d(4, 2, board.board_width)
            box_src = pusher_dest
            box_dest = index_1d(5, 2, board.board_width)
            behind_pusher = pusher_src - 1
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover = Mover(board, SolvingMode.REVERSE)
            mover.select_pusher(selected_pusher)

            mover.last_move = [PusherStep(Direction.LEFT, box_moved=True)]
            mover.pulls_boxes = False
            mover.undo_last_move()

            assert mover.board_manager.pusher_position(selected_pusher) == pusher_dest
            assert mover.board_manager.box_position(Config.DEFAULT_PIECE_ID + 1) == box_dest
            assert board[pusher_dest].has_pusher
            assert not board[pusher_src].has_pusher
            assert board[box_dest].has_box
            assert not board[box_src].has_box
            assert board[behind_pusher].has_box
            assert not board[pusher_src].has_box
            assert mover.last_move == [PusherStep(Direction.RIGHT, box_moved=True)]
            assert mover.last_move[0].pusher_id == selected_pusher
            assert mover.last_move[0].moved_box_id == Config.DEFAULT_PIECE_ID + 1

            # pulls_boxes == True
            board = BoardGraph(SokobanPuzzle(board=board_str))
            pusher_src = index_1d(3, 2, board.board_width)
            pusher_dest = index_1d(4, 2, board.board_width)
            box_src = pusher_dest
            box_dest = index_1d(5, 2, board.board_width)
            behind_pusher = pusher_src - 1
            selected_pusher = Config.DEFAULT_PIECE_ID + 1
            mover = Mover(board, SolvingMode.REVERSE)
            mover.select_pusher(selected_pusher)

            mover.last_move = [PusherStep(Direction.LEFT, box_moved=True)]
            mover.pulls_boxes = True
            mover.undo_last_move()

            assert mover.board_manager.pusher_position(selected_pusher) == pusher_dest
            assert mover.board_manager.box_position(Config.DEFAULT_PIECE_ID + 1) == box_dest
            assert board[pusher_dest].has_pusher
            assert not board[pusher_src].has_pusher
            assert board[box_dest].has_box
            assert not board[box_src].has_box
            assert board[behind_pusher].has_box
            assert not board[pusher_src].has_box
            assert mover.last_move == [PusherStep(Direction.RIGHT, box_moved=True)]
            assert mover.last_move[0].pusher_id == selected_pusher
            assert mover.last_move[0].moved_box_id == Config.DEFAULT_PIECE_ID + 1

        def it_refuses_to_undo_pull_moving_into_obstacles_or_off_board(self):
            board = BoardGraph(
                SokobanPuzzle(
                    board="\n".join(
                        [
                            # 12345678
                            "#########",  # 0
                            "#@ $$$$$#",  # 1
                            "@. ..@.@#",  # 2
                            ".       #",  # 3
                            "#########",  # 4
                        ]
                    )
                )
            )
            mover = Mover(board, SolvingMode.REVERSE)
            mover.select_pusher(Config.DEFAULT_PIECE_ID + 1)

            # undo into off board
            mover.last_move = [PusherStep(Direction.RIGHT, box_moved=True)]
            with pytest.raises(IllegalMoveError):
                mover.undo_last_move()
            assert mover.last_move == [PusherStep(Direction.RIGHT, box_moved=True)]
            assert mover.last_move[0].pusher_id == Config.DEFAULT_PIECE_ID
            assert mover.last_move[0].moved_box_id == None

            # undo into wall
            mover.last_move = [PusherStep(Direction.DOWN, box_moved=True)]
            with pytest.raises(IllegalMoveError):
                mover.undo_last_move()
            assert mover.last_move == [PusherStep(Direction.DOWN, box_moved=True)]
            assert mover.last_move[0].pusher_id == Config.DEFAULT_PIECE_ID
            assert mover.last_move[0].moved_box_id == None

            mover.select_pusher(Config.DEFAULT_PIECE_ID + 2)

            # undo into box
            mover.last_move = [PusherStep(Direction.RIGHT, box_moved=True)]
            with pytest.raises(IllegalMoveError):
                mover.undo_last_move()
            assert mover.last_move == [PusherStep(Direction.RIGHT, box_moved=True)]
            assert mover.last_move[0].pusher_id == Config.DEFAULT_PIECE_ID
            assert mover.last_move[0].moved_box_id == None

            # undo into pusher
            mover.last_move = [PusherStep(Direction.LEFT, box_moved=True)]
            with pytest.raises(IllegalMoveError):
                mover.undo_last_move()
            assert mover.last_move == [PusherStep(Direction.LEFT, box_moved=True)]
            assert mover.last_move[0].pusher_id == Config.DEFAULT_PIECE_ID
            assert mover.last_move[0].moved_box_id == None

    class DescribeUndoLastMove:
        def it_can_undo_random_sequence_of_moves_stored_in_last_move(
            self, forward_board, jump_dest, undone_jumps
        ):
            reverse_mover = Mover(forward_board, SolvingMode.REVERSE)

            initial_board = str(reverse_mover.board)
            moves = []
            reverse_mover.jump(jump_dest)
            moves += reverse_mover.last_move
            jump = deepcopy(reverse_mover.last_move)

            reverse_mover.select_pusher(Config.DEFAULT_PIECE_ID + 1)
            moves += reverse_mover.last_move
            selection = deepcopy(reverse_mover.last_move)
            undone_selections = [
                [
                    PusherStep(
                        direction=am.direction.opposite, is_pusher_selection=True
                    )
                    for am in permutation
                ]
                for permutation in permutations(selection)
            ]

            reverse_mover.move(Direction.UP)
            moves += reverse_mover.last_move
            reverse_mover.move(Direction.DOWN)
            moves += reverse_mover.last_move
            reverse_mover.move(Direction.LEFT)
            moves += reverse_mover.last_move

            board_after_moving = str(reverse_mover.board)

            reverse_mover.last_move = moves

            reverse_mover.undo_last_move()

            assert reverse_mover.last_move[0] == PusherStep(Direction.RIGHT)
            assert reverse_mover.last_move[1] == PusherStep(
                Direction.UP, box_moved=True
            )
            assert reverse_mover.last_move[2] == PusherStep(Direction.DOWN)
            assert reverse_mover.last_move[3 : 3 + len(selection)] in undone_selections
            assert reverse_mover.last_move[3 + len(selection) :] in undone_jumps

            assert str(reverse_mover.board) == initial_board

        def when_undoing_moves_it_raises_on_first_illegal_move(self):
            # TODO
            pass

        def when_fails_it_leaves_successful_moves_in_last_move(self):
            # TODO
            pass
