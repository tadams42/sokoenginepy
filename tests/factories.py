import pytest
import factory

from helpers import fake

from unittest.mock import MagicMock, Mock

from bosp.core import Piece, AtomicMove, Direction, BoardCell
from bosp.io import BoardEncodingCharacters


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
    return AtomicMoveFactory()


class BoardCellFactory(factory.Factory):
    class Meta:
        model = BoardCell

    chr = factory.LazyAttribute(
        lambda x: BoardEncodingCharacters.FLOOR.value
    )
@pytest.fixture
def board_cell():
    return BoardCellFactory()
