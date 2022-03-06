try:
    from sokoenginepyext import (
        IllegalMoveError,
        Mover,
        NonPlayableBoardError,
        SolvingMode,
    )
except ImportError:
    from .mover import IllegalMoveError, Mover, NonPlayableBoardError, SolvingMode
