from __future__ import annotations

from typing import Optional

from .puzzle import Puzzle
from .snapshot import Snapshot


class SokobanSnapshot(Snapshot):
    def __init__(self, moves_data: str = ""):
        from ..game import Tessellation

        super().__init__(tessellation=Tessellation.SOKOBAN, moves_data=moves_data)


class SokobanPuzzle(Puzzle):
    def __init__(self, width: int = 0, height: int = 0, board: Optional[str] = None):
        """
        Arguments:
            width: number of columns
            height: number of rows
            board: If not blank, it will be parsed and board will be created from it,
                ignoring ``width`` and ``height``.
        """
        from ..game import Tessellation

        super().__init__(
            tessellation=Tessellation.SOKOBAN, width=width, height=height, board=board
        )
