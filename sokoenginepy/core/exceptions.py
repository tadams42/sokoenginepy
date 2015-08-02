class SokoengineError(RuntimeError):
    """
    Base class for all sokoenginepy exceptions.
    """
    pass


class BoardConversionError(SokoengineError):
    """
    Exception risen when converting board to or from board strings.
    """
    RLE_DECODING_ERROR    = "Rle decoding board string failed"
    NON_BOARD_CHARS_FOUND = "Illegal characters found in board string"
    INVALID_LAYOUT        = "Board string has invalid layout for tessellation with multiple characters per single board cell"


class SnapshotConversionError(SokoengineError):
    """
    Exception risen when converting game snapshot to or from snapshot strings.
    """
    RLE_DECODING_ERROR = "Rle decoding board string failed"
    NON_SNAPSHOT_CHARACTERS_FOUND = "Illegal characters found in snapshot string"
    TOKENIZATION_ERROR = "Tokenizing snapshot string elements failed. Maybe there are unmatched parentheses"
    NON_VARIANT_CHARACTERS_FOUND = "Snapshot string contains directions not supported by requested tessellation"
    PUSHER_CHANGE_CONTAINS_PUSHES = "Pusher change sequence in snapshot string contains atomic pushes. This is not allowed"
    JUMP_CONTAINS_PUSHES = "Jump sequence in snapshot string contains atomic pushes. This is not allowed"


class IllegalDirectionError(SokoengineError):
    """
    Exception
    """
    pass


class UnknownTessellationError(SokoengineError):
    """
    Exception
    """
    pass


class InvalidPieceIdError(SokoengineError):
    """
    Exception
    """
    pass


class InvalidPiecePlusIdError(SokoengineError):
    """
    Exception
    """
    pass


class SokobanPlusDataError(SokoengineError):
    """
    Exception
    """
    pass
