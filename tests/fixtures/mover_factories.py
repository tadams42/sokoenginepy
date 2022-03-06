from itertools import permutations

import pytest

from sokoenginepy import (
    DEFAULT_PIECE_ID,
    AtomicMove,
    Direction,
    Mover,
    SokobanBoard,
    SolvingMode,
)
from sokoenginepy.game import JumpCommand, SelectPusherCommand
from sokoenginepy.utilities import index_1d

from .misc import fake


@pytest.fixture
def forward_board():
    # yapf: disable
    return SokobanBoard(board_str="\n".join([
        # 12345678
        "#########",  # 0
        "#$  .  .#",  # 1
        "#   @$# #",  # 2
        "#.$    @#",  # 3
        "#########",  # 4
    ]))
    # yapf: enable


@pytest.fixture
def reverse_board():
    # yapf: disable
    return SokobanBoard(board_str="\n".join([
        # 12345678
        "#########",  # 0
        "#.  $  $#",  # 1
        "#   @.# #",  # 2
        "#$.    @#",  # 3
        "#########",  # 4
    ]))
    # yapf: enable


@pytest.fixture
def forward_mover(forward_board):
    return Mover(forward_board)


@pytest.fixture
def reverse_mover(forward_board):
    return Mover(forward_board, SolvingMode.REVERSE)


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
def forward_select_command(forward_mover):
    return SelectPusherCommand(forward_mover, DEFAULT_PIECE_ID + 1)


@pytest.fixture
def reverse_select_command(reverse_mover):
    return SelectPusherCommand(reverse_mover, DEFAULT_PIECE_ID + 1)


@pytest.fixture
def pusher_selections():
    return [
        [AtomicMove(direction, is_pusher_selection=True) for direction in permutation]
        for permutation in permutations(
            [Direction.DOWN, Direction.RIGHT, Direction.RIGHT, Direction.RIGHT]
        )
    ]


@pytest.fixture
def undone_pusher_selections():
    return [
        [AtomicMove(direction, is_pusher_selection=True) for direction in permutation]
        for permutation in permutations(
            [Direction.UP, Direction.LEFT, Direction.LEFT, Direction.LEFT]
        )
    ]


@pytest.fixture
def jump_dest(reverse_board):
    return index_1d(1, 1, reverse_board.width)


@pytest.fixture
def jump_obstacle_position(reverse_board):
    return index_1d(0, 0, reverse_board.width)


@pytest.fixture
def off_board_position():
    return index_1d(42, 42, 42)


@pytest.fixture
def jumps():
    return [
        [AtomicMove(direction, is_jump=True) for direction in permutation]
        for permutation in permutations(
            [Direction.UP, Direction.LEFT, Direction.LEFT, Direction.LEFT]
        )
    ]


@pytest.fixture
def undone_jumps():
    return [
        [AtomicMove(direction, is_jump=True) for direction in permutation]
        for permutation in permutations(
            [Direction.DOWN, Direction.RIGHT, Direction.RIGHT, Direction.RIGHT]
        )
    ]


@pytest.fixture
def jump_command(reverse_mover, jump_dest):
    return JumpCommand(reverse_mover, jump_dest)
