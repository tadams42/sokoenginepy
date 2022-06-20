from typing import Optional


def index_1d(x: int, y: int, board_width: int) -> int:
    """Converts 2D coordinate to board position index."""
    return y * board_width + x


def index_x(index: int, board_width: int) -> int:
    """x component of board position index."""
    return 0 if board_width == 0 else index % board_width


def index_y(index: int, board_width: int) -> int:
    """y component of board position index."""
    return 0 if board_width == 0 else int(index / board_width)


def index_row(index: int, board_width: int) -> int:
    """x component of board position index."""
    return index_y(index, board_width)


def index_column(index: int, board_width: int) -> int:
    """y component of board position index."""
    return index_x(index, board_width)


def is_on_board_2d(x: int, y: int, board_width: int, board_height: int) -> bool:
    return x >= 0 and y >= 0 and x < board_width and y < board_height


def is_on_board_1d(index: Optional[int], board_width: int, board_height: int) -> bool:
    return (
        index is not None
        and index >= 0
        and is_on_board_2d(
            index_x(index, board_width),
            index_y(index, board_width),
            board_width,
            board_height,
        )
    )
