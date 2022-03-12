try:
    from sokoenginepyext import IllegalMoveError, Mover, NonPlayableBoardError
except ImportError:
    from .mover import IllegalMoveError, Mover, NonPlayableBoardError
