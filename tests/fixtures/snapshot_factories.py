import factory
import pytest

from sokoenginepy.game import Snapshot, SolvingMode, Tessellation

from .misc import fake


class SnapshotFactory(factory.Factory):
    class Meta:
        model = Snapshot

    tessellation_or_description = factory.LazyAttribute(
        lambda x: fake.random_element(
            [
                Tessellation.SOKOBAN,
                Tessellation.TRIOBAN,
                Tessellation.OCTOBAN,
                Tessellation.HEXOBAN,
            ]
        )
    )
    solving_mode = factory.LazyAttribute(
        lambda x: fake.random_element([SolvingMode.FORWARD, SolvingMode.REVERSE])
    )


@pytest.fixture
def game_snapshot():
    return Snapshot.from_data("lurdLURD{lurd}LURD")
