from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .atomic_move import AtomicMove
    from .board_cell import BoardCell
    from .board_graph import BoardGraph
    from .board_manager import (
        BoardManager,
        BoxGoalSwitchError,
        CellAlreadyOccupiedError,
    )
    from .board_state import BoardState
    from .cell_orientation import CellOrientation
    from .direction import Direction
    from .graph_type import GraphType
    from .hashed_board_manager import HashedBoardManager
    from .hexoban_tessellation import HexobanTessellation
    from .mover import IllegalMoveError, Mover, NonPlayableBoardError
    from .octoban_tessellation import OctobanTessellation
    from .sokoban_plus import SokobanPlus, SokobanPlusDataError
    from .sokoban_tessellation import SokobanTessellation
    from .solving_mode import SolvingMode
    from .trioban_tessellation import TriobanTessellation


else:
    try:
        from sokoenginepyext.game import (
            AtomicMove,
            BoardCell,
            BoardGraph,
            BoardManager,
            BoardState,
            BoxGoalSwitchError,
            CellAlreadyOccupiedError,
            CellOrientation,
            Direction,
            GraphType,
            HashedBoardManager,
            HexobanTessellation,
            IllegalMoveError,
            Mover,
            NonPlayableBoardError,
            OctobanTessellation,
            SokobanPlus,
            SokobanPlusDataError,
            SokobanTessellation,
            SolvingMode,
            TriobanTessellation,
        )

    except ImportError:
        from .atomic_move import AtomicMove
        from .board_cell import BoardCell
        from .board_graph import BoardGraph
        from .board_manager import (
            BoardManager,
            BoxGoalSwitchError,
            CellAlreadyOccupiedError,
        )
        from .board_state import BoardState
        from .cell_orientation import CellOrientation
        from .direction import Direction
        from .graph_type import GraphType
        from .hashed_board_manager import HashedBoardManager
        from .hexoban_tessellation import HexobanTessellation
        from .mover import IllegalMoveError, Mover, NonPlayableBoardError
        from .octoban_tessellation import OctobanTessellation
        from .sokoban_plus import SokobanPlus, SokobanPlusDataError
        from .sokoban_tessellation import SokobanTessellation
        from .solving_mode import SolvingMode
        from .trioban_tessellation import TriobanTessellation

from .mover_commands import JumpCommand, MoveCommand, SelectPusherCommand
from .piece import DEFAULT_PIECE_ID
from .tessellation import AnyTessellation, Tessellation, TessellationOrDescription
from .utilities import COLUMN, ROW, X, Y, index_1d, is_on_board_1d, is_on_board_2d
