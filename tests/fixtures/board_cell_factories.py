import factory
import pytest

from sokoenginepy import BoardCell


class BoardCellFactory(factory.Factory):
    class Meta:
        model = BoardCell

    character = factory.LazyAttribute(lambda x: BoardCell.Characters.FLOOR)


@pytest.fixture
def board_cell():
    return BoardCellFactory()
