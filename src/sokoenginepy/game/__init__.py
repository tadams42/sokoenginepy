"""
Module that handles Sokoban gameplay.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base_tessellation import Tessellation
    from .board_cell import BoardCell
    from .board_graph import BoardGraph, Edge
    from .board_manager import (
        BoardManager,
        BoxGoalSwitchError,
        CellAlreadyOccupiedError,
    )
    from .board_state import BoardState
    from .config import Config, Direction, GraphType
    from .hashed_board_manager import HashedBoardManager
    from .mover import IllegalMoveError, Mover, NonPlayableBoardError, SolvingMode
    from .pusher_step import PusherStep
    from .sokoban_plus import SokobanPlus, SokobanPlusDataError


else:
    try:
        from sokoenginepyext.game import (
            BoardCell,
            BoardGraph,
            BoardManager,
            BoardState,
            BoxGoalSwitchError,
            CellAlreadyOccupiedError,
            Config,
            Direction,
            Edge,
            GraphType,
            HashedBoardManager,
            IllegalMoveError,
            Mover,
            NonPlayableBoardError,
            PusherStep,
            SokobanPlus,
            SokobanPlusDataError,
            SolvingMode,
            Tessellation,
        )

    except ImportError:
        from .base_tessellation import Tessellation
        from .board_cell import BoardCell
        from .board_graph import BoardGraph, Edge
        from .board_manager import (
            BoardManager,
            BoxGoalSwitchError,
            CellAlreadyOccupiedError,
        )
        from .board_state import BoardState
        from .config import Config, Direction, GraphType
        from .hashed_board_manager import HashedBoardManager
        from .mover import IllegalMoveError, Mover, NonPlayableBoardError, SolvingMode
        from .pusher_step import PusherStep
        from .sokoban_plus import SokobanPlus, SokobanPlusDataError

from .coordinate_helpers import (
    index_1d,
    index_column,
    index_row,
    index_x,
    index_y,
    is_on_board_1d,
    is_on_board_2d,
)
from .mover_commands import JumpCommand, MoveCommand, SelectPusherCommand
