"""
Module that handles Sokoban gameplay.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base_tessellation import BaseTessellation, Tessellation
    from .board_cell import BoardCell
    from .board_graph import BoardGraph
    from .board_manager import (
        BoardManager,
        BoxGoalSwitchError,
        CellAlreadyOccupiedError,
    )
    from .board_state import BoardState
    from .config import Config, Direction, GraphType
    from .hashed_board_manager import HashedBoardManager
    from .hexoban_tessellation import HexobanTessellation
    from .mover import IllegalMoveError, Mover, NonPlayableBoardError, SolvingMode
    from .octoban_tessellation import OctobanTessellation
    from .pusher_step import PusherStep
    from .sokoban_plus import SokobanPlus, SokobanPlusDataError
    from .sokoban_tessellation import SokobanTessellation
    from .trioban_tessellation import TriobanTessellation


else:
    try:
        from sokoenginepyext.game import (
            BaseTessellation,
            BoardCell,
            BoardGraph,
            BoardManager,
            BoardState,
            BoxGoalSwitchError,
            CellAlreadyOccupiedError,
            Config,
            Direction,
            GraphType,
            HashedBoardManager,
            HexobanTessellation,
            IllegalMoveError,
            Mover,
            NonPlayableBoardError,
            OctobanTessellation,
            PusherStep,
            SokobanPlus,
            SokobanPlusDataError,
            SokobanTessellation,
            SolvingMode,
            Tessellation,
            TriobanTessellation,
        )

    except ImportError:
        from .base_tessellation import BaseTessellation, Tessellation
        from .board_cell import BoardCell
        from .board_graph import BoardGraph
        from .board_manager import (
            BoardManager,
            BoxGoalSwitchError,
            CellAlreadyOccupiedError,
        )
        from .board_state import BoardState
        from .config import Config, Direction, GraphType
        from .hashed_board_manager import HashedBoardManager
        from .hexoban_tessellation import HexobanTessellation
        from .mover import IllegalMoveError, Mover, NonPlayableBoardError, SolvingMode
        from .octoban_tessellation import OctobanTessellation
        from .pusher_step import PusherStep
        from .sokoban_plus import SokobanPlus, SokobanPlusDataError
        from .sokoban_tessellation import SokobanTessellation
        from .trioban_tessellation import TriobanTessellation

from .base_tessellation import (
    COLUMN,
    ROW,
    X,
    Y,
    index_1d,
    is_on_board_1d,
    is_on_board_2d,
)
from .mover_commands import JumpCommand, MoveCommand, SelectPusherCommand
