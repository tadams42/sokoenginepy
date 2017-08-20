from enum import Enum

from ... import board, tessellation


class InvalidAtomicMoveError(ValueError):
    pass


class AtomicMoveCharacters(str, Enum):
    """
    Characters used in textual representation of :class:`.Snapshot`.

    Not all variants use all characters. Also, for different variants, same
    character may have different meaning (represent different
    :class:`.Direction`).
    """
    l = 'l'
    u = 'u'
    r = 'r'
    d = 'd'
    L = 'L'
    U = 'U'
    R = 'R'
    D = 'D'
    w = 'w'
    W = 'W'
    e = 'e'
    E = 'E'
    n = 'n'
    N = 'N'
    s = 's'
    S = 'S'

    @classmethod
    def values(cls):
        return (o for o in cls)


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

    def __init__(
        self, direction=tessellation.Direction.LEFT, box_moved=False,
        is_jump=False, is_pusher_selection=False,
        pusher_id=board.DEFAULT_PIECE_ID, moved_box_id=None,
    ):
        if (box_moved or moved_box_id) and is_pusher_selection and is_jump:
            raise InvalidAtomicMoveError(
                "AtomicMove can't be all, a push, a jump and a pusher "
                "selection!"
            )

        if is_jump and is_pusher_selection:
            raise InvalidAtomicMoveError(
                "AtomicMove can't be both, a jump and a pusher selection!"
            )

        if (box_moved or moved_box_id) and is_jump:
            raise InvalidAtomicMoveError(
                "AtomicMove can't be both, a push and a jump!"
            )

        if (box_moved or moved_box_id) and is_pusher_selection:
            raise InvalidAtomicMoveError(
                "AtomicMove can't be both, a push and a pusher selection!"
            )

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

        if moved_box_id:
            self.moved_box_id = moved_box_id

        if is_jump:
            self.is_jump = is_jump

        if is_pusher_selection:
            self.is_pusher_selection = is_pusher_selection

    @classmethod
    def is_atomic_move_chr(cls, character):
        return character in cls.Characters.values()

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
