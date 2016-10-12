from ..common import Variant
from ..input_output import OutputSettings
from .variant_board import VariantBoard, VariantBoardResizer


class OctobanBoard(VariantBoard):
    """Implements :class:`.VariantBoard` for Octoban variant."""

    def __init__(self, board_width=0, board_height=0, board_str=""):
        super().__init__(
            board_width=board_width,
            board_height=board_height,
            variant=Variant.OCTOBAN,
            board_str=board_str
        )

    @property
    def _resizer_class(self):
        return OctobanBoardResizer

    def _parse_string(self, board_str):
        return super()._parse_string(board_str)

    def to_s(self, output_settings=OutputSettings()):
        return super().to_s(output_settings)


class OctobanBoardResizer(VariantBoardResizer):

    def __init__(self, octoban_board):
        super().__init__(octoban_board)
