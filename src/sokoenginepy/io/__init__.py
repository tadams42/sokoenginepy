"""
Module that handles Sokoban I/O and text processing.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .collection import Collection
    from .hexoban import HexobanPuzzle, HexobanSnapshot
    from .octoban import OctobanPuzzle, OctobanSnapshot
    from .puzzle import CellOrientation, Puzzle
    from .rle import Rle
    from .snapshot import Snapshot
    from .sokoban import SokobanPuzzle, SokobanSnapshot
    from .trioban import TriobanPuzzle, TriobanSnapshot

else:
    try:
        from sokoenginepyext.io import (
            CellOrientation,
            Collection,
            HexobanPuzzle,
            HexobanSnapshot,
            OctobanPuzzle,
            OctobanSnapshot,
            Puzzle,
            Rle,
            Snapshot,
            SokobanPuzzle,
            SokobanSnapshot,
            TriobanPuzzle,
            TriobanSnapshot,
        )

    except ImportError:
        from .collection import Collection
        from .hexoban import HexobanPuzzle, HexobanSnapshot
        from .octoban import OctobanPuzzle, OctobanSnapshot
        from .puzzle import CellOrientation, Puzzle
        from .rle import Rle
        from .snapshot import Snapshot
        from .sokoban import SokobanPuzzle, SokobanSnapshot
        from .trioban import TriobanPuzzle, TriobanSnapshot

from .utilities import is_blank
