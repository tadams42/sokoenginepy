import factory
import pytest
from helpers import fake

from sokoenginepy import (DEFAULT_PIECE_ID, AtomicMove, BoardCell, BoardState,
                          Direction, HashedBoardState, Mover, Snapshot,
                          SokobanBoard, SokobanPlus, SolvingMode, Tessellation,
                          index_1d, settings)


@pytest.fixture(scope='function', autouse=True)
def preserved_settings(request):
    backup_flag1 = settings.OUTPUT_BOARDS_WITH_VISIBLE_FLOORS

    def teardown():
        settings.OUTPUT_BOARDS_WITH_VISIBLE_FLOORS = backup_flag1

    request.addfinalizer(teardown)


class AtomicMoveFactory(factory.Factory):
    class Meta:
        model = AtomicMove

    box_moved = factory.LazyAttribute(lambda x: fake.boolean())
    direction = factory.LazyAttribute(
        lambda x: fake.random_element(list(Direction))
    )


@pytest.fixture
def atomic_move():
    return AtomicMoveFactory(direction=Direction.LEFT, box_moved=False)


@pytest.fixture
def atomic_push():
    return AtomicMoveFactory(direction=Direction.LEFT, box_moved=True)


@pytest.fixture
def atomic_jump():
    retv = AtomicMoveFactory(direction=Direction.LEFT)
    retv.is_jump = True
    return retv


@pytest.fixture
def atomic_pusher_selection():
    retv = AtomicMoveFactory(direction=Direction.LEFT)
    retv.is_pusher_selection = True
    return retv


class BoardCellFactory(factory.Factory):
    class Meta:
        model = BoardCell

    character = factory.LazyAttribute(lambda x: BoardCell.Characters.FLOOR)


@pytest.fixture
def board_cell():
    return BoardCellFactory()


class SnapshotFactory(factory.Factory):
    class Meta:
        model = Snapshot

    tessellation_or_description = factory.LazyAttribute(
        lambda x: fake.random_element(list(Tessellation))
    )
    solving_mode = factory.LazyAttribute(
        lambda x: fake.random_element(list(SolvingMode))
    )
    moves_data = ""


@pytest.fixture
def game_snapshot():
    return SnapshotFactory(moves_data="lurdLURD{lurd}LURD")


class SokobanPlusFactory(factory.Factory):
    class Meta:
        model = SokobanPlus

    pieces_count = factory.LazyAttribute(lambda x: 5)
    boxorder = factory.LazyAttribute(lambda x: "42 24 4 2")
    goalorder = factory.LazyAttribute(lambda x: "2 24 42 4")


@pytest.fixture
def sokoban_plus():
    return SokobanPlusFactory()


@pytest.fixture
def board_str():
    # yapf: disable
    return "\n".join([
        # 123456789012345678
        "    #####",            # 0
        "    #  @#",            # 1
        "    #$  #",            # 2
        "  ###  $##",           # 3
        "  #  $ $ #",           # 4
        "### # ## #   ######",  # 5
        "#   # ## #####  ..#",  # 6
        "# $  $          ..#",  # 7
        "##### ### #@##  ..#",  # 8
        "    #     #########",  # 9
        "    #######",          # 0
    ])
    # yapf: enable


@pytest.fixture
def switched_board_str():
    # yapf: disable
    return "\n".join([
        "    #####",
        "    #  @#",
        "    #.  #",
        "  ###  .##",
        "  #  . . #",
        "### # ## #   ######",
        "#   # ## #####  $$#",
        "# .  .          $$#",
        "##### ### #@##  $$#",
        "    #     #########",
        "    #######",
    ])
    # yapf: enable


@pytest.fixture
def board_width():
    return 19


@pytest.fixture
def board_height():
    return 11


@pytest.fixture
def variant_board(board_str):
    # We could use mock here, but it is not neccessary as long as we test only
    # common behavior."
    return SokobanBoard(board_str=board_str)


@pytest.fixture
def board_graph(variant_board):
    return variant_board._graph


@pytest.fixture
def sokoban_tessellation():
    return Tessellation.SOKOBAN.value


@pytest.fixture
def trioban_tessellation():
    return Tessellation.TRIOBAN.value


@pytest.fixture
def board_state(variant_board):
    return BoardState(variant_board)


@pytest.fixture
def hashed_board_state(variant_board):
    return HashedBoardState(variant_board)


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
        DEFAULT_PIECE_ID, DEFAULT_PIECE_ID + 1, DEFAULT_PIECE_ID + 2,
        DEFAULT_PIECE_ID + 3, DEFAULT_PIECE_ID + 4, DEFAULT_PIECE_ID + 5
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
        DEFAULT_PIECE_ID, DEFAULT_PIECE_ID + 1, DEFAULT_PIECE_ID + 2,
        DEFAULT_PIECE_ID + 3, DEFAULT_PIECE_ID + 4, DEFAULT_PIECE_ID + 5
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
def non_playable_board():
    return SokobanBoard(5, 5)


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
        Direction.LEFT, Direction.LEFT, Direction.LEFT, Direction.DOWN,
        Direction.RIGHT, Direction.UP, Direction.RIGHT, Direction.RIGHT,
        Direction.DOWN, Direction.LEFT, Direction.UP, Direction.RIGHT
    ]


@pytest.fixture
def reverse_mover_moves_cycle():
    return [
        Direction.LEFT, Direction.UP, Direction.LEFT, Direction.DOWN,
        Direction.RIGHT, Direction.RIGHT, Direction.UP, Direction.RIGHT,
        Direction.DOWN, Direction.LEFT
    ]
