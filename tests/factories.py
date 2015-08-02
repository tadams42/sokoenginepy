import pytest
import factory

from helpers import fake

from sokoenginepy import (
    AtomicMove, Direction, BoardCell, GameSnapshot, Variant,
    GameSolvingMode, SokobanPlus, Piece, OutputSettings
)
from sokoenginepy.game import SokobanPlusValidator
from sokoenginepy.io import BoardEncodingCharacters
from sokoenginepy.variant import SokobanBoard
from sokoenginepy.core import Tessellation


class PieceFactory(factory.Factory):
    class Meta:
        model = Piece

    position = factory.LazyAttribute(
        lambda x: fake.random_int(min=-100, max=100)
    )
    id = factory.LazyAttribute(
        lambda x: fake.random_int(
            min=Piece.DEFAULT_ID, max=Piece.DEFAULT_ID + 100
        )
    )
    plus_id = factory.LazyAttribute(
        lambda x: fake.random_int(
            min=Piece.DEFAULT_PLUS_ID, max=Piece.DEFAULT_PLUS_ID + 100
        )
    )

@pytest.fixture
def piece():
    return PieceFactory()


class AtomicMoveFactory(factory.Factory):
    class Meta:
        model = AtomicMove

    box_moved = factory.LazyAttribute(
        lambda x: fake.boolean()
    )
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

    chr = factory.LazyAttribute(
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

    pieces_count = factory.LazyAttribute(
        lambda x: 5
    )

    boxorder = factory.LazyAttribute(
        lambda x: "42 24 4 2"
    )

    goalorder = factory.LazyAttribute(
        lambda x: "2 24 42 4"
    )

@pytest.fixture
def sokoban_plus():
    return SokobanPlusFactory()

@pytest.fixture
def sokoban_plus_validator(sokoban_plus):
    sokoban_plus._parse()
    return SokobanPlusValidator(sokoban_plus)

@pytest.fixture
def board_str():
    return "\n".join([
        # 123456789012345678
        "    #####",            # 0
        "    #   #",            # 1
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
