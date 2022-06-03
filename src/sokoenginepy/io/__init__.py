from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .collection import Collection
    from .puzzle import Puzzle
    from .puzzle_types import PuzzleTypes
    from .rle import Rle
    from .snapshot import Snapshot
    from .utilities import is_blank

else:
    try:
        from sokoenginepyext.io import (
            Collection,
            Puzzle,
            PuzzleTypes,
            Rle,
            Snapshot,
            is_blank,
        )

    except ImportError:
        from .collection import Collection
        from .puzzle import Puzzle
        from .puzzle_types import PuzzleTypes
        from .rle import Rle
        from .snapshot import Snapshot
        from .utilities import is_blank
