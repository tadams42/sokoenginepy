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
    from .hexoban_board import HexobanBoard
    from .hexoban_tessellation import HexobanTessellation
    from .mover import IllegalMoveError, Mover, NonPlayableBoardError
    from .octoban_board import OctobanBoard
    from .octoban_tessellation import OctobanTessellation
    from .sokoban_board import SokobanBoard
    from .sokoban_plus import SokobanPlus, SokobanPlusDataError
    from .sokoban_tessellation import SokobanTessellation
    from .solving_mode import SolvingMode
    from .trioban_board import TriobanBoard
    from .trioban_tessellation import TriobanTessellation
    from .variant_board import VariantBoard


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
            HexobanBoard,
            HexobanTessellation,
            IllegalMoveError,
            Mover,
            NonPlayableBoardError,
            OctobanBoard,
            OctobanTessellation,
            SokobanBoard,
            SokobanPlus,
            SokobanPlusDataError,
            SokobanTessellation,
            SolvingMode,
            TriobanBoard,
            TriobanTessellation,
            VariantBoard,
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
        from .hexoban_board import HexobanBoard
        from .hexoban_tessellation import HexobanTessellation
        from .mover import IllegalMoveError, Mover, NonPlayableBoardError
        from .octoban_board import OctobanBoard
        from .octoban_tessellation import OctobanTessellation
        from .sokoban_board import SokobanBoard
        from .sokoban_plus import SokobanPlusDataError, SokobanPlus
        from .sokoban_tessellation import SokobanTessellation
        from .solving_mode import SolvingMode
        from .trioban_board import TriobanBoard
        from .trioban_tessellation import TriobanTessellation
        from .variant_board import VariantBoard

from .mover_commands import JumpCommand, MoveCommand, SelectPusherCommand
from .piece import DEFAULT_PIECE_ID
from .snapshot import Snapshot
from .tessellation import AnyTessellation, Tessellation, TessellationOrDescription
from .utilities import COLUMN, ROW, X, Y, index_1d, is_on_board_1d, is_on_board_2d
