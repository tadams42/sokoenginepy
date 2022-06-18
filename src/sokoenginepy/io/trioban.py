from __future__ import annotations

from typing import Optional

from .puzzle import Puzzle
from .snapshot import Snapshot


class TriobanSnapshot(Snapshot):
    """
    `Snapshot` implementation for `.Tessellation.TRIOBAN` and `.TriobanTessellation`.
    """

    def __init__(self, moves_data: str = ""):
        from ..game import Tessellation

        super().__init__(tessellation=Tessellation.TRIOBAN, moves_data=moves_data)


class TriobanPuzzle(Puzzle):
    """
    `Puzzle` implementation for `.Tessellation.TRIOBAN` and `.TriobanTessellation`.

    Arguments:
        width: number of columns
        height: number of rows
        board: If not blank, it will be parsed and board will be created from it,
            ignoring ``width`` and ``height``.
    """

    def __init__(self, width: int = 0, height: int = 0, board: Optional[str] = None):
        from ..game import Tessellation

        super().__init__(
            tessellation=Tessellation.TRIOBAN, width=width, height=height, board=board
        )
