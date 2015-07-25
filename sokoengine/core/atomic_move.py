from .helpers import PrettyPrintable, EqualityComparable
from ..variant.tessellation import Direction
from .piece import Box, Pusher
from .exceptions import InvalidPieceIdError


class AtomicMove(PrettyPrintable, EqualityComparable):
    """
    Represents single step of pusher movement. It can be one of the following:
        - move - pusher moved without pushing box
        - push/pull - pusher moved and pushed a box in front of it (FORWARD
          solving mode) or pusher moved and pulled a box behind it (REVERSE
          solving mode)
        - jump - single step in pusher jump sequence (jumps are allowed only in
          REVERSE solving mode)
        - pusher selection - single step in sequence describing focus change of
          active pusher in Multiban games
    """

    def __init__(self, direction = Direction.LEFT, box_moved = False):
        self._box_moved = False
        self._pusher_selected = False
        self._pusher_jumped = False
        self._pusher_id = Pusher.DEFAULT_ID
        self._moved_box_id = None
        self.group_id = 0

        self.direction = direction
        if box_moved:
            self.is_push_or_pull = True
        else:
            self.is_move = True

    def _representation_attributes(self):
        return {
            'direction': self.direction,
            'is_push_or_pull': self.is_push_or_pull,
            'is_pusher_selection': self.is_pusher_selection,
            'is_jump': self.is_jump,
            'pusher_id': self.pusher_id,
            'moved_box_id': self.moved_box_id,
            'group_id': self.group_id,
        }

    def _equality_attributes(self):
        return (
            self.direction, self.is_push_or_pull,
            self.is_pusher_selection, self.is_jump,
        )

    @property
    def moved_box_id(self):
        """
        If pusher performed push/pull, this is ID of box that was moved.
        Otherwise returns None
        """
        return self._moved_box_id if self.is_push_or_pull else None

    @moved_box_id.setter
    def moved_box_id(self, value):
        """
        Setting box ID to not None make this atomic move a push/pull. It also
        validates value and requires it to be valid Piece id.
        Setting ID to None, makes this a non-push.
        """
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
        """
        Piece ID of pusher that performed movement.
        """
        return self._pusher_id

    @pusher_id.setter
    def pusher_id(self, value):
        if not Pusher.is_valid_id(value):
            raise InvalidPieceIdError
        self._pusher_id = value

    @property
    def is_move(self):
        """
        True if pusher didn't move box, jump or changed focus to other pusher.
        """
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
        """
        True if pusher also moved a box.
        """
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
        """
        True if this move is part of change active pusher sequence in Multiban
        games.
        """
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
        """
        True if this move is part of pusher jump sequence in REVERSE games.
        """
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
