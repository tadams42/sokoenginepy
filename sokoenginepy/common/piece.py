from .exceptions import SokoengineError

DEFAULT_PIECE_ID = 1


class InvalidPieceIdError(SokoengineError):
    """
    Exception
    """
    pass


def is_valid_piece_id(id):
    return isinstance(id, int) and id >= DEFAULT_PIECE_ID
