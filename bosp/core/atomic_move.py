from .helpers import PrettyPrintable, EqualityComparable
from .tessellation import Direction
from .piece import Box, Pusher, InvalidPieceIdError

class AtomicMove(PrettyPrintable, EqualityComparable):

    direction = Direction.LEFT
    _box_moved = False
    _pusher_selected = False
    _pusher_jumped = False
    _pusher_id = Pusher.DEFAULT_ID
    _moved_box_id = None
    group_id = 0

    def __init__(self, direction = Direction.LEFT, box_moved = False):
        self.direction = direction
        if box_moved:
            self.is_push_or_pull = True
        else:
            self.is_move = True

    def __representation_attributes__(self):
        return {
            'direction': self.direction,
            'is_push_or_pull': self.is_push_or_pull,
            'is_pusher_selection': self.is_pusher_selection,
            'is_jump': self.is_jump,
            'pusher_id': self.pusher_id,
            'moved_box_id': self.moved_box_id,
            'group_id': self.group_id,
        }

    def __equality_attributes__(self):
        return (
            self.direction, self.is_push_or_pull,
            self.is_pusher_selection, self.is_jump,
        )

    @property
    def moved_box_id(self):
        return self._moved_box_id if self.is_push_or_pull else None

    @moved_box_id.setter
    def moved_box_id(self, value):
        if value is None:
            self._moved_box_id = value
            self.is_push_or_pull = False
        else:
            if not Box.is_valid_id(value):
                raise InvalidPieceIdError
            self._moved_box_id = value
            self.is_push_or_pull = True

    @property
    def pusher_id(self):
        return self._pusher_id

    @pusher_id.setter
    def pusher_id(self, value):
        if not Pusher.is_valid_id(value):
            raise InvalidPieceIdError
        self._pusher_id = value

    @property
    def is_move(self):
        return (
            not self._box_moved and
            not self._pusher_selected and
            not self._pusher_jumped
        )

    @is_move.setter
    def is_move(self, value):
        if value:
            self._box_moved = False
            self._pusher_jumped = False
            self._pusher_selected = False
        else:
            self._moved_box_id = None

    @property
    def is_push_or_pull(self):
        return (
            self._box_moved and
            not self._pusher_selected and
            not self._pusher_jumped
        )

    @is_push_or_pull.setter
    def is_push_or_pull(self, value):
        if value:
            self._box_moved = True
            self._pusher_jumped = False
            self._pusher_selected = False
        else:
            self._box_moved = False
            self._moved_box_id = None

    @property
    def is_pusher_selection(self):
        return (
            self._pusher_selected and
            not self._pusher_jumped and
            not self._box_moved
        )

    @is_pusher_selection.setter
    def is_pusher_selection(self, value):
        if value:
            self._pusher_selected = True
            self._box_moved = False
            self._pusher_jumped = False
            self._moved_box_id = None
        else:
            self._pusher_selected = False

    @property
    def is_jump(self):
        return (
            self._pusher_jumped and
            not self._box_moved and
            not self._pusher_selected
        )

    @is_jump.setter
    def is_jump(self, value):
        if value:
            self._pusher_jumped = True
            self._pusher_selected = False
            self._box_moved = False
            self._moved_box_id = None
        else:
            self._pusher_jumped = False
