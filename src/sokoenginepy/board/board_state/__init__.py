try:
    from sokoenginecpp import BoardState
except ImportError:
    from .board_state import BoardState

from .board_state import BoxGoalSwitchError, CellAlreadyOccupiedError
