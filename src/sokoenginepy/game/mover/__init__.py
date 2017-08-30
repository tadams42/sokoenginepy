try:
    from sokoenginecpp import Mover, SolvingMode
except ImportError:
    from .mover import Mover, SolvingMode

from .mover import IllegalMoveError, NonPlayableBoardError
