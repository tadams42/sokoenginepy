def index_1d(x, y, board_width):
    """Converts 2D coordinate to board position index."""
    return y * board_width + x


def X(index, board_width):
    return 0 if board_width == 0 else index % board_width


def Y(index, board_width):
    return 0 if board_width == 0 else int(index / board_width)


def ROW(index, board_width):
    return Y(index, board_width)


def COLUMN(index, board_width):
    return X(index, board_width)


def on_board_2d(x, y, board_width, board_height):
    return x >= 0 and y >= 0 and x < board_width and y < board_height


def on_board_1d(index, board_width, board_height):
    return index is not None and index >= 0 and on_board_2d(
        X(index, board_width), Y(index, board_width), board_width, board_height
    )
