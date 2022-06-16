import factory

from sokoenginepy.game import PusherStep, Direction

from .misc import fake


class PusherStepFactory(factory.Factory):
    class Meta:
        model = PusherStep

    box_moved = factory.LazyAttribute(lambda x: fake.boolean())
    direction = factory.LazyAttribute(lambda x: fake.random_element(list(Direction)))
