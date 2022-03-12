try:
    from sokoenginepyext import BoardGraph
except ImportError:
    from .board_graph import BoardCellOrStr, BoardGraph, Directions, Positions
