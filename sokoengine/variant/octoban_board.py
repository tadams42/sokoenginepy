from .tessellation import TessellationType
from .variant_board import VariantBoard


class OctobanBoard(VariantBoard):
    """
    Implements VariantBoard for Octoban variant.
    """

    def __init__(self, board_width=0, board_height=0, board_str = ""):
        super().__init__(
            board_width = board_width, board_height = board_height,
            tessellation_type = TessellationType.OCTOBAN,
            board_str = board_str
        )
