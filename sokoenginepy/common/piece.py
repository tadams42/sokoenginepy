from .exceptions import SokoengineError

DEFAULT_PIECE_ID = 1


class InvalidPieceIdError(SokoengineError):
    """
    Exception
    """
    pass


def is_valid_piece_id(pid):
    return isinstance(pid, int) and pid >= DEFAULT_PIECE_ID
