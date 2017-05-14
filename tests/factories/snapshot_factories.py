import factory
import pytest
from helpers import fake

from sokoenginepy import Snapshot, SolvingMode, Tessellation


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
