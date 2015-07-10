import pytest
import factory

from helpers import fake

from unittest.mock import MagicMock, Mock

from bosp.core import Piece


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
