from ..variant_board import VariantBoard, VariantBoardResizer


class SokobanBoard(VariantBoard):
    def __init__(self, board_width=0, board_height=0, board_str=None):
        super().__init__(
            tessellation_or_description="sokoban",
            board_width=board_width,
            board_height=board_height,
            board_str=board_str,
        )

    @property
    def _resizer_class(self):
        return SokobanBoardResizer

    def _parse_string(self, board_str):
        return super()._parse_string(board_str)


class SokobanBoardResizer(VariantBoardResizer):
    def __init__(self, sokoban_board):
        super().__init__(sokoban_board)
