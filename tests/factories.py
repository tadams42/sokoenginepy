import pytest
import factory

from helpers import fake

from sokoenginepy import (
    AtomicMove, Direction, BoardCell, GameSnapshot, Variant, GameSolvingMode,
    SokobanPlus, OutputSettings
)
from sokoenginepy.core.sokoban_plus import SokobanPlusValidator
from sokoenginepy.io import BoardEncodingCharacters
from sokoenginepy.variant import SokobanBoard
from sokoenginepy.core import Tessellation, BoardState, HashedBoardState


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

    character = factory.LazyAttribute(
        lambda x: BoardEncodingCharacters.FLOOR.value
    )


@pytest.fixture
def board_cell():
    return BoardCellFactory()


class GameSnapshotFactory(factory.Factory):

    class Meta:
        model = GameSnapshot

    variant = factory.LazyAttribute(
        lambda x: fake.random_element(list(Variant))
    )
    solving_mode = factory.LazyAttribute(
        lambda x: fake.random_element(list(GameSolvingMode))
    )
    moves_data = ""


@pytest.fixture
def game_snapshot():
    return GameSnapshotFactory(moves_data="lurdLURD{lurd}LURD")


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
def sokoban_plus_validator(sokoban_plus):
    sokoban_plus._parse()
    return SokobanPlusValidator(sokoban_plus)


@pytest.fixture
def board_str():
    # yapf: disable
    return "\n".join([
        # 123456789012345678
        "    #####",           # 0
        "    #   #",           # 1
        "    #$  #",           # 2
        "  ###  $##",          # 3
        "  #  $ $ #",           # 4
        "### # ## #   ######",  # 5
        "#   # ## #####  ..#",  # 6
        "# $  $          ..#",  # 7
        "##### ### #@##  ..#",  # 8
        "    #     #########",  # 9
        "    #######",  # 0
    ])
    # yapf: enable


@pytest.fixture
def board_str_width():
    return 19


@pytest.fixture
def board_str_height():
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
    return Tessellation.factory('sokoban')


@pytest.fixture
def trioban_tessellation():
    return Tessellation.factory('trioban')


@pytest.fixture
def output_settings():
    return OutputSettings(use_visible_floors=True)


@pytest.fixture
def board_state(variant_board):
    return BoardState(variant_board)


@pytest.fixture
def hashed_board_state(variant_board):
    return HashedBoardState(variant_board)
