from __future__ import annotations

from typing import Optional

from .puzzle import Puzzle


class SokobanPuzzle(Puzzle):
    def __init__(self, width: int = 0, height: int = 0, board: Optional[str] = None):
        """
        Arguments:
            width: number of columns
            height: number of rows
            board: If not blank, it will be parsed and board will be created from it,
                ignoring ``width`` and ``height``.
        """
        super().__init__(
            tessellation_or_description="sokoban",
            width=width,
            height=height,
            board=board,
        )
