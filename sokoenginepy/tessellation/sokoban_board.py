from ..common import Variant
from .variant_board import VariantBoard, VariantBoardResizer


class SokobanBoard(VariantBoard):
    """Implements :class:`.VariantBoard` for Sokoban variant."""

    def __init__(self, board_width=0, board_height=0, board_str=""):
        super().__init__(
            board_width=board_width,
            board_height=board_height,
            variant=Variant.SOKOBAN,
            board_str=board_str
        )

    @property
    def _resizer_class(self):
        return SokobanBoardResizer

    def _parse_string(self, board_str):
        return super()._parse_string(board_str)


class SokobanBoardResizer(VariantBoardResizer):

    def __init__(self, sokoban_board):
        super().__init__(sokoban_board)
