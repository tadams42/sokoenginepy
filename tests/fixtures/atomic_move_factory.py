import factory

from sokoenginepy.game import AtomicMove, Direction

from .misc import fake


class AtomicMoveFactory(factory.Factory):
    class Meta:
        model = AtomicMove

    box_moved = factory.LazyAttribute(lambda x: fake.boolean())
    direction = factory.LazyAttribute(lambda x: fake.random_element(list(Direction)))
