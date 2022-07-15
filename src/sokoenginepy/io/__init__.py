"""
Module that handles Sokoban I/O and text processing.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .collection import Collection
    from .puzzle import CellOrientation, Puzzle
    from .rle import Rle
    from .snapshot import Snapshot

else:
    try:
        from sokoenginepyext.io import (
            CellOrientation,
            Collection,
            Puzzle,
            Rle,
            Snapshot,
        )

    except ImportError:
        from .collection import Collection
        from .puzzle import CellOrientation, Puzzle
        from .rle import Rle
        from .snapshot import Snapshot

from .utilities import is_blank
