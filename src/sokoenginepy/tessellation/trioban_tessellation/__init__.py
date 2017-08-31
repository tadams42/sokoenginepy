try:
    from sokoenginepyext import TriobanTessellation
except ImportError:
    from .trioban_tessellation import TriobanTessellation
