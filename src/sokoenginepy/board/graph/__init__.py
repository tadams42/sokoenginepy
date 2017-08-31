try:
    from sokoenginepyext import BoardGraph, GraphType
except ImportError:
    from .board_graph import BoardGraph, GraphType
