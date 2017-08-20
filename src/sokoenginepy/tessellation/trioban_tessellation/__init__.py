try:
    from libsokoengine import TriobanTessellation
except ImportError:
    from .trioban_tessellation import TriobanTessellation
