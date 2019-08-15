try:
    from sokoenginepyext import BoardCell, BoardConversionError
except ImportError:
    from .board_cell import BoardCell, BoardConversionError
