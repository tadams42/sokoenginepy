from typing import TYPE_CHECKING

__version__ = "2.0.0.dev"

if TYPE_CHECKING:
    from .common import TileShape, Config, Direction, Tessellation
    from .game import (
        BoardCell,
        BoardGraph,
        BoardManager,
        BoardState,
        BoxGoalSwitchError,
        CellAlreadyOccupiedError,
        Edge,
        HashedBoardManager,
        IllegalMoveError,
        Mover,
        NonPlayableBoardError,
        PusherStep,
        SokobanPlus,
        SokobanPlusDataError,
        SolvingMode,
    )
    from .io import Collection, Puzzle, Rle, Snapshot

else:
    try:
        from sokoenginepyext import (
            BoardCell,
            BoardGraph,
            BoardManager,
            BoardState,
            BoxGoalSwitchError,
            CellAlreadyOccupiedError,
            TileShape,
            Collection,
            Config,
            Direction,
            Edge,
            HashedBoardManager,
            IllegalMoveError,
            Mover,
            NonPlayableBoardError,
            PusherStep,
            Puzzle,
            Rle,
            Snapshot,
            SokobanPlus,
            SokobanPlusDataError,
            SolvingMode,
            Tessellation,
        )

    except ImportError:
        from .common import (
            TileShape,
            Config,
            Direction,
            Tessellation,
        )
        from .game import (
            BoardCell,
            BoardGraph,
            BoardManager,
            BoardState,
            BoxGoalSwitchError,
            CellAlreadyOccupiedError,
            Edge,
            HashedBoardManager,
            IllegalMoveError,
            Mover,
            NonPlayableBoardError,
            PusherStep,
            SokobanPlus,
            SokobanPlusDataError,
            SolvingMode,
        )
        from .io import Collection, Puzzle, Rle, Snapshot

from .common import (
    index_1d,
    index_column,
    index_row,
    index_x,
    index_y,
    is_on_board_1d,
    is_on_board_2d,
)
from .game import JumpCommand, MoveCommand, SelectPusherCommand
