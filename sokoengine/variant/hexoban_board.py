from ..core import TessellationType
from ..io import OutputSettings

from .variant_board import VariantBoard, VariantBoardResizer


class HexobanBoard(VariantBoard):
    """
    Implements VariantBoard for Hexoban variant.
    """

    def __init__(self, board_width=0, board_height=0, board_str = ""):
        super().__init__(
            board_width = board_width, board_height = board_height,
            tessellation_type = TessellationType.HEXOBAN,
            board_str = board_str
        )

    def _parse_string(self, board_str):
        return super()._parse_string(board_str)

    def to_s(self, output_settings = OutputSettings()):
        return super().to_s(output_settings)


class HexobanBoardResizer(VariantBoardResizer):
    def __init__(self, hexoban_board):
        super().__init__(hexoban_board)
