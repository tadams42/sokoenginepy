from .exceptions import SokoengineError

#: All pieces on board (pushers, boxes) and goals are assigned ID to be used for
#: referring them . Default ID for a piece or goal is this value.
#:
#: Piece ids are assigned by numbering each type of piece or goal starting with
#: ``DEFAULT_PIECE_ID``
#:
#: .. image:: /images/assigning_ids.png
#:     :alt: Assigning IDs to pieces and goals
#:
#: Once assigned, id of a piece doesn't change by either moving piece or
#: applying board view transformations.
DEFAULT_PIECE_ID = 1


class InvalidPieceIdError(SokoengineError):
    pass


def is_valid_piece_id(pid):
    return isinstance(pid, int) and pid >= DEFAULT_PIECE_ID
