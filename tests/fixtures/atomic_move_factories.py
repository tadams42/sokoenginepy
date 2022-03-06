import factory
import pytest

from sokoenginepy import AtomicMove, Direction

from .misc import fake


class AtomicMoveFactory(factory.Factory):
    class Meta:
        model = AtomicMove

    box_moved = factory.LazyAttribute(lambda x: fake.boolean())
    direction = factory.LazyAttribute(lambda x: fake.random_element(list(Direction)))


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
