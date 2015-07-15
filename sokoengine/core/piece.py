from .helpers import PrettyPrintable, EqualityComparable
from .exceptions import InvalidPieceIdError, InvalidPiecePlusIdError

class Piece(PrettyPrintable, EqualityComparable):
    DEFAULT_ID      = 1
    DEFAULT_PLUS_ID = 0

    def __init__(self, position = 0, id = DEFAULT_ID, plus_id = DEFAULT_PLUS_ID):
        self._id       = None
        self._plus_id  = None

        self.position = position
        self.id       = id
        self.plus_id  = plus_id

    def __representation_attributes__(self):
        return {
            'position': self.position,
            'id': self.id,
            'plus_id': self.plus_id,
        }

    @classmethod
    def is_valid_id(cls, id):
        return (
            id is not None and id >= cls.DEFAULT_ID
        )

    @classmethod
    def is_valid_plus_id(cls, plus_id):
        return (
            plus_id is not None and plus_id >= cls.DEFAULT_PLUS_ID
        )

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if not type(self).is_valid_id(value):
            raise InvalidPieceIdError()
        self._id = value

    @property
    def plus_id(self):
        return self._plus_id

    @plus_id.setter
    def plus_id(self, value):
        if not type(self).is_valid_plus_id(value):
            raise InvalidPiecePlusIdError()
        self._plus_id = value


class Box(Piece):
    pass


class Goal(Piece):
    pass


class Pusher(Piece):
    pass
