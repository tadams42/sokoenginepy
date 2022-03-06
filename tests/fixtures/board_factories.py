from itertools import permutations

import factory
import pytest

from sokoenginepy import (
    DEFAULT_PIECE_ID,
    BoardManager,
    BoardState,
    Direction,
    HashedBoardManager,
    SokobanBoard,
    SokobanPlus,
    Tessellation,
)
from sokoenginepy.utilities import index_1d

from .misc import fake


@pytest.fixture
def board_str():
    # yapf: disable
    return "\n".join([
        # 123456789012345678
        "    #####          ",  # 0
        "    #  @#          ",  # 1
        "    #$  #          ",  # 2
        "  ###  $##         ",  # 3
        "  #  $ $ #         ",  # 4
        "### # ## #   ######",  # 5
        "#   # ## #####  ..#",  # 6
        "# $  $          ..#",  # 7
        "##### ### #@##  ..#",  # 8
        "    #     #########",  # 9
        "    #######        ",  # 0
    ])
    # yapf: enable


@pytest.fixture
def switched_board_str():
    # yapf: disable
    return "\n".join([
        "    #####          ",
        "    #  @#          ",
        "    #.  #          ",
        "  ###  .##         ",
        "  #  . . #         ",
        "### # ## #   ######",
        "#   # ## #####  $$#",
        "# .  .          $$#",
        "##### ### #@##  $$#",
        "    #     #########",
        "    #######        ",
    ])
    # yapf: enable


@pytest.fixture
def solved_board_str():
    # yapf: disable
    return "\n".join([
        # 123456789012345678
        "    #####          ",  # 0
        "    #  @#          ",  # 1
        "    #   #          ",  # 2
        "  ###   ##         ",  # 3
        "  #      #         ",  # 4
        "### # ## #   ######",  # 5
        "#   # ## #####  **#",  # 6
        "#               **#",  # 7
        "##### ### #@##  **#",  # 8
        "    #     #########",  # 9
        "    #######        ",  # 0
    ])
    # yapf: enable


@pytest.fixture
def positions_path(board_width):
    return [
        index_1d(7, 1, board_width),
        index_1d(6, 1, board_width),
        index_1d(6, 2, board_width),
        index_1d(6, 3, board_width),
        index_1d(6, 4, board_width),
        index_1d(5, 4, board_width),
    ]


@pytest.fixture
def directions_path():
    return [
        Direction.LEFT,
        Direction.DOWN,
        Direction.DOWN,
        Direction.DOWN,
        Direction.LEFT,
    ]


@pytest.fixture
def board_width():
    return 19


@pytest.fixture
def board_height():
    return 11


@pytest.fixture
def variant_board(board_str):
    # We could use mock here, but it is not necessary as long as we test only
    # common behavior."
    return SokobanBoard(board_str=board_str)


@pytest.fixture
def solved_board(solved_board_str):
    return SokobanBoard(board_str=solved_board_str)


@pytest.fixture
def board_graph(variant_board):
    return variant_board.graph


@pytest.fixture
def sokoban_tessellation():
    return Tessellation.SOKOBAN.value


@pytest.fixture
def trioban_tessellation():
    return Tessellation.TRIOBAN.value


@pytest.fixture
def board_manager(variant_board):
    return BoardManager(variant_board)


@pytest.fixture
def hashed_board_manager(variant_board):
    return HashedBoardManager(variant_board)


@pytest.fixture
def wall_position(board_width):
    return index_1d(4, 0, board_width)


@pytest.fixture
def pusher_ids():
    return [DEFAULT_PIECE_ID, DEFAULT_PIECE_ID + 1]


@pytest.fixture
def pushers_positions(board_width):
    return {
        DEFAULT_PIECE_ID: index_1d(7, 1, board_width),
        DEFAULT_PIECE_ID + 1: index_1d(11, 8, board_width),
    }


@pytest.fixture
def invalid_pusher_position():
    return index_1d(11, 8, 42)


@pytest.fixture
def normalized_pushers_positions(board_width):
    return {
        DEFAULT_PIECE_ID: index_1d(5, 1, board_width),
        DEFAULT_PIECE_ID + 1: index_1d(8, 4, board_width),
    }


@pytest.fixture
def boxes_positions(board_width):
    return {
        DEFAULT_PIECE_ID: index_1d(5, 2, board_width),
        DEFAULT_PIECE_ID + 1: index_1d(7, 3, board_width),
        DEFAULT_PIECE_ID + 2: index_1d(5, 4, board_width),
        DEFAULT_PIECE_ID + 3: index_1d(7, 4, board_width),
        DEFAULT_PIECE_ID + 4: index_1d(2, 7, board_width),
        DEFAULT_PIECE_ID + 5: index_1d(5, 7, board_width),
    }


@pytest.fixture
def invalid_box_position():
    return index_1d(5, 7, 42)


@pytest.fixture
def boxes_ids():
    return [
        DEFAULT_PIECE_ID,
        DEFAULT_PIECE_ID + 1,
        DEFAULT_PIECE_ID + 2,
        DEFAULT_PIECE_ID + 3,
        DEFAULT_PIECE_ID + 4,
        DEFAULT_PIECE_ID + 5,
    ]


@pytest.fixture
def goals_positions(board_width):
    return {
        DEFAULT_PIECE_ID: index_1d(16, 6, board_width),
        DEFAULT_PIECE_ID + 1: index_1d(17, 6, board_width),
        DEFAULT_PIECE_ID + 2: index_1d(16, 7, board_width),
        DEFAULT_PIECE_ID + 3: index_1d(17, 7, board_width),
        DEFAULT_PIECE_ID + 4: index_1d(16, 8, board_width),
        DEFAULT_PIECE_ID + 5: index_1d(17, 8, board_width),
    }


@pytest.fixture
def invalid_goal_position():
    return index_1d(17, 8, 42)


@pytest.fixture
def goals_ids():
    return [
        DEFAULT_PIECE_ID,
        DEFAULT_PIECE_ID + 1,
        DEFAULT_PIECE_ID + 2,
        DEFAULT_PIECE_ID + 3,
        DEFAULT_PIECE_ID + 4,
        DEFAULT_PIECE_ID + 5,
    ]


@pytest.fixture
def switched_goals(boxes_positions):
    return {
        DEFAULT_PIECE_ID: boxes_positions[DEFAULT_PIECE_ID],
        DEFAULT_PIECE_ID + 1: boxes_positions[DEFAULT_PIECE_ID + 1],
        DEFAULT_PIECE_ID + 2: boxes_positions[DEFAULT_PIECE_ID + 2],
        DEFAULT_PIECE_ID + 3: boxes_positions[DEFAULT_PIECE_ID + 3],
        DEFAULT_PIECE_ID + 4: boxes_positions[DEFAULT_PIECE_ID + 4],
        DEFAULT_PIECE_ID + 5: boxes_positions[DEFAULT_PIECE_ID + 5],
    }


@pytest.fixture
def switched_boxes(goals_positions):
    return {
        DEFAULT_PIECE_ID: goals_positions[DEFAULT_PIECE_ID],
        DEFAULT_PIECE_ID + 1: goals_positions[DEFAULT_PIECE_ID + 1],
        DEFAULT_PIECE_ID + 2: goals_positions[DEFAULT_PIECE_ID + 2],
        DEFAULT_PIECE_ID + 3: goals_positions[DEFAULT_PIECE_ID + 3],
        DEFAULT_PIECE_ID + 4: goals_positions[DEFAULT_PIECE_ID + 4],
        DEFAULT_PIECE_ID + 5: goals_positions[DEFAULT_PIECE_ID + 5],
    }


@pytest.fixture
def switched_goals_plus(boxes_positions):
    # boxorder 1 3 2
    # goalorder 3 2 1
    # (box, goal) id pairs [(2, 1), (3, 2), (1, 3), (4, 4), (5, 5), (6, 6)]
    return {
        DEFAULT_PIECE_ID: boxes_positions[DEFAULT_PIECE_ID + 1],
        DEFAULT_PIECE_ID + 1: boxes_positions[DEFAULT_PIECE_ID + 2],
        DEFAULT_PIECE_ID + 2: boxes_positions[DEFAULT_PIECE_ID],
        DEFAULT_PIECE_ID + 3: boxes_positions[DEFAULT_PIECE_ID + 3],
        DEFAULT_PIECE_ID + 4: boxes_positions[DEFAULT_PIECE_ID + 4],
        DEFAULT_PIECE_ID + 5: boxes_positions[DEFAULT_PIECE_ID + 5],
    }


@pytest.fixture
def switched_boxes_plus(goals_positions):
    # boxorder 1 3 2
    # goalorder 3 2 1
    # (box, goal) id pairs [(2, 1), (3, 2), (1, 3), (4, 4), (5, 5), (6, 6)]
    return {
        DEFAULT_PIECE_ID: goals_positions[DEFAULT_PIECE_ID + 2],
        DEFAULT_PIECE_ID + 1: goals_positions[DEFAULT_PIECE_ID],
        DEFAULT_PIECE_ID + 2: goals_positions[DEFAULT_PIECE_ID + 1],
        DEFAULT_PIECE_ID + 3: goals_positions[DEFAULT_PIECE_ID + 3],
        DEFAULT_PIECE_ID + 4: goals_positions[DEFAULT_PIECE_ID + 4],
        DEFAULT_PIECE_ID + 5: goals_positions[DEFAULT_PIECE_ID + 5],
    }


@pytest.fixture
def all_solutions(goals_positions):
    def calc():
        for boxes_positions in permutations(goals_positions.values()):
            yield BoardState(
                boxes_positions=list(boxes_positions), pushers_positions=[]
            )

    return list(calc())


@pytest.fixture
def sokoban_plus_solutions():
    return [
        BoardState(
            boxes_positions=[149, 130, 131, 150, 168, 169], pushers_positions=[]
        ),
        BoardState(
            boxes_positions=[149, 130, 131, 150, 169, 168], pushers_positions=[]
        ),
        BoardState(
            boxes_positions=[149, 130, 131, 168, 150, 169], pushers_positions=[]
        ),
        BoardState(
            boxes_positions=[149, 130, 131, 168, 169, 150], pushers_positions=[]
        ),
        BoardState(
            boxes_positions=[149, 130, 131, 169, 150, 168], pushers_positions=[]
        ),
        BoardState(
            boxes_positions=[149, 130, 131, 169, 168, 150], pushers_positions=[]
        ),
    ]


@pytest.fixture
def non_playable_board():
    return SokobanBoard(5, 5)


class SokobanPlusFactory(factory.Factory):
    class Meta:
        model = SokobanPlus

    pieces_count = factory.LazyAttribute(lambda x: 5)
    boxorder = factory.LazyAttribute(lambda x: "42 24 4 2")
    goalorder = factory.LazyAttribute(lambda x: "2 24 42 4")


@pytest.fixture
def sokoban_plus():
    return SokobanPlusFactory()
