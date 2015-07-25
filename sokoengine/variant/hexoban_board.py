from ..core import TessellationType

from .variant_board import VariantBoard


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
