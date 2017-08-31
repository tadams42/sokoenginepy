try:
    from sokoenginepyext import (BoardState, BoxGoalSwitchError,
                                 CellAlreadyOccupiedError)
except ImportError:
    from .board_state import (BoardState, BoxGoalSwitchError,
                              CellAlreadyOccupiedError)
