from enum import Enum

from .. import tessellation


class AtomicMove:
    """Represents single step of pusher movement.

        - move - pusher moved without pushing box
        - push/pull - pusher moved and pushed a box in front of it (
          :attr:`.SolvingMode.FORWARD`) or pusher moved and pulled a box behind
          it (:attr:`.SolvingMode.REVERSE`)
        - jump - single step in pusher jump sequence (jumps are allowed only in
          :attr:`.SolvingMode.REVERSE`)
        - pusher selection - single step in sequence describing focus change of
          active pusher in Multiban games
    """

    class Characters(str, Enum):
        """
        Characters used in textual representation of :class:`.AtomicMove`.

        Not all variants use all characters. Also, for different variants, same
        character may have different meaning (represent different
        :class:`.Direction`).
        """
        LOWER_L = 'l'
        LOWER_U = 'u'
        LOWER_R = 'r'
        LOWER_D = 'd'
        UPPER_L = 'L'
        UPPER_U = 'U'
        UPPER_R = 'R'
        UPPER_D = 'D'
        LOWER_NW = 'w'
        UPPER_NW = 'W'
        LOWER_SE = 'e'
        UPPER_SE = 'E'
        LOWER_NE = 'n'
        UPPER_NE = 'N'
        LOWER_SW = 's'
        UPPER_SW = 'S'

    def __init__(self, direction=tessellation.Direction.LEFT, box_moved=False):
        from .. import board
        self._box_moved = False
        self._pusher_selected = False
        self._pusher_jumped = False
        self._pusher_id = board.DEFAULT_PIECE_ID
        self._moved_box_id = None

        self.direction = direction
        #pylint: disable=simplifiable-if-statement
        if box_moved:
            self.is_push_or_pull = True
        else:
            self.is_move = True

    @classmethod
    def is_atomic_move_chr(cls, character):
        if isinstance(character, cls.Characters):
            character = character
        return (
            character == cls.Characters.LOWER_L or
            character == cls.Characters.LOWER_U or
            character == cls.Characters.LOWER_R or
            character == cls.Characters.LOWER_D or
            character == cls.Characters.LOWER_NW or
            character == cls.Characters.LOWER_SE or
            character == cls.Characters.LOWER_NE or
            character == cls.Characters.LOWER_SW or
            character == cls.Characters.UPPER_L or
            character == cls.Characters.UPPER_U or
            character == cls.Characters.UPPER_R or
            character == cls.Characters.UPPER_D or
            character == cls.Characters.UPPER_NW or
            character == cls.Characters.UPPER_SE or
            character == cls.Characters.UPPER_NE or
            character == cls.Characters.UPPER_SW
        )

    def __repr__(self):
        return "AtomicMove({0}, box_moved={1})".format(
            str(self.direction), self.is_push_or_pull
        )

    def __str__(self):
        return (
            "AtomicMove({0}, box_moved={1}, is_jump={2}, "
            "is_pusher_selection={3} pusher_id={4} box_id={5})"
        ).format(
            str(self.direction), self.is_push_or_pull, self.is_jump,
            self.is_pusher_selection, self.pusher_id, self.moved_box_id,
        )

    def __eq__(self, rv):
        return (
            self.direction == rv.direction and
            self.is_push_or_pull == rv.is_push_or_pull and
            self.is_pusher_selection == rv.is_pusher_selection and
            self.is_jump == rv.is_jump
        )

    def __ne__(self, rv):
        return not self == rv

    @property
    def moved_box_id(self):
        """
        ID of box that was moved or None, depending on type of
        :class:`.AtomicMove`
        """
        return self._moved_box_id if self.is_push_or_pull else None

    @moved_box_id.setter
    def moved_box_id(self, value):
        """
        Updates ID of moved box and if this ID is valid, also changes this to
        push/pull. If removing ID, changes this to not-push/not-pull
        """
        from .. import board
        if board.is_valid_piece_id(value):
            self._moved_box_id = value
            self.is_push_or_pull = True
        else:
            self._moved_box_id = None
            self.is_push_or_pull = False

    @property
    def pusher_id(self):
        """ID of pusher that performed movement."""
        return self._pusher_id

    @pusher_id.setter
    def pusher_id(self, value):
        from .. import board
        if board.is_valid_piece_id(value):
            self._pusher_id = value
        else:
            self._pusher_id = board.DEFAULT_PIECE_ID

    @property
    def is_move(self):
        """
        True if pusher didn't move box, jump or changed focus to other pusher.
        """
        return (
            not self._box_moved and not self._pusher_selected and
            not self._pusher_jumped
        )

    @is_move.setter
    def is_move(self, value):
        if value:
            self._box_moved = False
            self._pusher_jumped = False
            self._pusher_selected = False
            self._moved_box_id = None
        else:
            self._box_moved = True
            self._pusher_jumped = False
            self._pusher_selected = False

    @property
    def is_push_or_pull(self):
        """True if pusher also moved a box."""
        return (
            self._box_moved and not self._pusher_selected and
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
            self._pusher_selected and not self._pusher_jumped and
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
        True if this move is part of pusher jump sequence in
        :attr:`.SolvingMode.REVERSE` games.
        """
        return (
            self._pusher_jumped and not self._box_moved and
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
