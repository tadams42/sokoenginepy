from sokoenginepy import game
from sokoenginepy.game import BaseTessellation, Tessellation


class DescribeBaseTessellation:
    def it_provides_factory_for_subtypes(self):
        for tessellation in Tessellation.__members__.values():
            klass = getattr(game, f"{tessellation.name.capitalize()}Tessellation")

            obj = BaseTessellation.instance(tessellation)
            assert isinstance(obj, klass)
