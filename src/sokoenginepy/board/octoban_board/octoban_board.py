from ..variant_board import VariantBoard, VariantBoardResizer


class OctobanBoard(VariantBoard):
    def __init__(self, board_width=0, board_height=0, board_str=None):
        super().__init__(
            tessellation_or_description="octoban",
            board_width=board_width,
            board_height=board_height,
            board_str=board_str,
        )

    @property
    def _resizer_class(self):
        return OctobanBoardResizer

    def _parse_string(self, board_str):
        return super()._parse_string(board_str)


class OctobanBoardResizer(VariantBoardResizer):
    def __init__(self, octoban_board):
        super().__init__(octoban_board)
