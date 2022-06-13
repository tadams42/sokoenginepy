from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .collection import Collection
    from .hexoban import HexobanPuzzle, HexobanSnapshot
    from .octoban import OctobanPuzzle, OctobanSnapshot
    from .puzzle import Puzzle
    from .rle import Rle
    from .snapshot import Snapshot
    from .sokoban import SokobanPuzzle, SokobanSnapshot
    from .trioban import TriobanPuzzle, TriobanSnapshot
    from .utilities import is_blank

else:
    try:
        from sokoenginepyext.io import (
            Collection,
            HexobanPuzzle,
            OctobanPuzzle,
            Puzzle,
            Rle,
            Snapshot,
            SokobanPuzzle,
            TriobanPuzzle,
            is_blank,
        )

    except ImportError:
        from .collection import Collection
        from .hexoban import HexobanPuzzle, HexobanSnapshot
        from .octoban import OctobanPuzzle, OctobanSnapshot
        from .puzzle import Puzzle
        from .rle import Rle
        from .snapshot import Snapshot
        from .sokoban import SokobanPuzzle, SokobanSnapshot
        from .trioban import TriobanPuzzle, TriobanSnapshot
        from .utilities import is_blank
