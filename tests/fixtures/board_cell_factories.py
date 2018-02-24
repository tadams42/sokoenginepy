import factory
import pytest

from sokoenginepy import BoardCell, BoardCellCharacters


class BoardCellFactory(factory.Factory):
    class Meta:
        model = BoardCell

    character = factory.LazyAttribute(
        lambda x: BoardCellCharacters.FLOOR.value
    )


@pytest.fixture
def board_cell():
    return BoardCellFactory()
