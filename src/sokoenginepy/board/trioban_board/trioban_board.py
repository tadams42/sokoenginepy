from __future__ import annotations

from typing import List, Optional, Type

from ..variant_board import VariantBoard, VariantBoardResizer


class TriobanBoard(VariantBoard):
    def __init__(
        self,
        board_width: int = 0,
        board_height: int = 0,
        board_str: Optional[str] = None,
    ):
        super().__init__(
            tessellation_or_description="trioban",
            board_width=board_width,
            board_height=board_height,
            board_str=board_str,
        )

    @property
    def _resizer_class(self) -> Type[TriobanBoardResizer]:
        return TriobanBoardResizer

    def _parse_string(self, board_str: str) -> List[str]:
        return super()._parse_string(board_str)


class TriobanBoardResizer(VariantBoardResizer):
    def __init__(self, trioban_board: TriobanBoard):
        super().__init__(trioban_board)
