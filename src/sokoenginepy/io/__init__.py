from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .collection import Collection
    from .hexoban_puzzle import HexobanPuzzle
    from .octoban_puzzle import OctobanPuzzle
    from .puzzle import Puzzle
    from .rle import Rle
    from .snapshot import Snapshot
    from .sokoban_puzzle import SokobanPuzzle
    from .trioban_puzzle import TriobanPuzzle
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
        from .hexoban_puzzle import HexobanPuzzle
        from .octoban_puzzle import OctobanPuzzle
        from .puzzle import Puzzle
        from .rle import Rle
        from .snapshot import Snapshot
        from .sokoban_puzzle import SokobanPuzzle
        from .trioban_puzzle import TriobanPuzzle
        from .utilities import is_blank
