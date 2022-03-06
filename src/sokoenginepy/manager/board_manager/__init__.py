try:
    from sokoenginepyext import (
        BoardManager,
        BoxGoalSwitchError,
        CellAlreadyOccupiedError,
    )
except ImportError:
    from .board_manager import (
        BoardManager,
        BoxGoalSwitchError,
        CellAlreadyOccupiedError,
    )
