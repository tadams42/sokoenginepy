import factory
import pytest

from sokoenginepy.game import BoardCell
from sokoenginepy.io import Puzzle


class BoardCellFactory(factory.Factory):
    class Meta:
        model = BoardCell

    character = factory.LazyAttribute(lambda x: Puzzle.FLOOR)


@pytest.fixture
def board_cell():
    return BoardCellFactory()
