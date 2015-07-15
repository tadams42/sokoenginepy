class SokoengineError(RuntimeError):
    pass


class BoardConversionError(SokoengineError):
    RLE_DECODING_ERROR    = "Rle decoding board string failed"
    NON_BOARD_CHARS_FOUND = "Illegal characters found in board string"
    INVALID_LAYOUT        = "Board string has invalid layout for tessellation with multiple characters per single board cell"


class SnapshotConversionError(SokoengineError):
    RLE_DECODING_ERROR = "Rle decoding board string failed"
    NON_SNAPSHOT_CHARACTERS_FOUND = "Illegal characters found in snapshot string"
    TOKENIZATION_ERROR = "Tokenizing snapshot string elements failed. Maybe there are unmatched parentheses"
    NON_VARIANT_CHARACTERS_FOUND = "Snapshot string contains directions not supported by requested tessellation"
    PUSHER_CHANGE_CONTAINS_PUSHES = "Pusher change sequence in snapshot string contains atomic pushes. This is not allowed"
    JUMP_CONTAINS_PUSHES = "Jump sequence in snapshot string contains atomic pushes. This is not allowed"


class IllegalDirectionError(SokoengineError):
    pass


class UnknownTessellationError(SokoengineError):
    pass


class InvalidPieceIdError(SokoengineError):
    pass


class InvalidPiecePlusIdError(SokoengineError):
    pass
