from typing import ClassVar, Optional, Set

from ...manager import DEFAULT_PIECE_ID
from ...tessellation import Direction


class AtomicMove:
    """Represents single step of pusher movement.

        - move - pusher moved without pushing box
        - push/pull - pusher moved and pushed a box in front of it (
          :attr:`.SolvingMode.FORWARD`) or pusher moved and pulled a box behind it
          (:attr:`.SolvingMode.REVERSE`)
        - jump - single step in pusher jump sequence (jumps are allowed only in
          :attr:`.SolvingMode.REVERSE`)
        - pusher selection - single step in sequence describing focus change of
          active pusher in Multiban games
    """

    __slots__ = [
        "_box_moved",
        "_pusher_selected",
        "_pusher_jumped",
        "_pusher_id",
        "_moved_box_id",
        "direction",
    ]

    l: ClassVar[str] = "l"
    u: ClassVar[str] = "u"
    r: ClassVar[str] = "r"
    d: ClassVar[str] = "d"
    L: ClassVar[str] = "L"
    U: ClassVar[str] = "U"
    R: ClassVar[str] = "R"
    D: ClassVar[str] = "D"
    w: ClassVar[str] = "w"
    W: ClassVar[str] = "W"
    e: ClassVar[str] = "e"
    E: ClassVar[str] = "E"
    n: ClassVar[str] = "n"
    N: ClassVar[str] = "N"
    s: ClassVar[str] = "s"
    S: ClassVar[str] = "S"

    #: Characters used in textual representation of :class:`.Snapshot`.
    #:
    #: Not all variants use all characters. Also, for different variants, same character
    #: may have different meaning (represent different :class:`.Direction`).
    CHARACTERS: ClassVar[Set[str]] = {l, u, r, d, L, U, R, D, W, W, e, E, n, N, s, S}

    def __init__(
        self,
        direction: Direction = Direction.LEFT,
        box_moved: bool = False,
        is_jump: bool = False,
        is_pusher_selection: bool = False,
        pusher_id: int = DEFAULT_PIECE_ID,
        moved_box_id: Optional[int] = None,
    ):
        if (box_moved or moved_box_id) and is_pusher_selection and is_jump:
            raise ValueError(
                "AtomicMove can't be all, a push, a jump and a pusher selection!"
            )

        if is_jump and is_pusher_selection:
            raise ValueError("AtomicMove can't be both, a jump and a pusher selection!")

        if (box_moved or moved_box_id) and is_jump:
            raise ValueError("AtomicMove can't be both, a push and a jump!")

        if (box_moved or moved_box_id) and is_pusher_selection:
            raise ValueError("AtomicMove can't be both, a push and a pusher selection!")

        self._box_moved: bool = False
        self._pusher_selected: bool = False
        self._pusher_jumped: bool = False
        self.pusher_id: int = pusher_id
        self._moved_box_id: Optional[int] = None
        self.direction: Direction = direction

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
    def is_atomic_move_chr(cls, character: str) -> bool:
        return character in cls.CHARACTERS

    def __repr__(self):
        return "AtomicMove({0}, box_moved={1})".format(
            str(self.direction), self.is_push_or_pull
        )

    def __str__(self):
        return (
            "AtomicMove({0}, box_moved={1}, is_jump={2}, "
            "is_pusher_selection={3} pusher_id={4} box_id={5})"
        ).format(
            str(self.direction),
            self.is_push_or_pull,
            self.is_jump,
            self.is_pusher_selection,
            self.pusher_id,
            self.moved_box_id,
        )

    def __eq__(self, rv):
        return (
            self.direction == rv.direction
            and self.is_push_or_pull == rv.is_push_or_pull
            and self.is_pusher_selection == rv.is_pusher_selection
            and self.is_jump == rv.is_jump
        )

    def __ne__(self, rv):
        return not self == rv

    @property
    def moved_box_id(self) -> Optional[int]:
        """
        ID of box that was moved or None, depending on type of :class:`.AtomicMove`
        """
        return self._moved_box_id if self.is_push_or_pull else None

    @moved_box_id.setter
    def moved_box_id(self, value: Optional[int]):
        """
        Updates ID of moved box and if this ID is valid, also changes this to
        push/pull. If removing ID, changes this to not-push/not-pull
        """
        if isinstance(value, int) and value >= DEFAULT_PIECE_ID:
            self._moved_box_id = value
            self.is_push_or_pull = True
        else:
            self._moved_box_id = None
            self.is_push_or_pull = False

    @property
    def pusher_id(self) -> int:
        """ID of pusher that performed movement."""
        return self._pusher_id

    @pusher_id.setter
    def pusher_id(self, value: int):
        """
        Note:
            Pusher ID can't be None, thus we always set it to DEFAULT_PIECE_ID
        """
        if isinstance(value, int) and value >= DEFAULT_PIECE_ID:
            self._pusher_id = value
        else:
            self._pusher_id = DEFAULT_PIECE_ID

    @property
    def is_move(self) -> bool:
        """
        True if pusher didn't move box, jump or changed focus to other pusher.
        """
        return (
            not self._box_moved
            and not self._pusher_selected
            and not self._pusher_jumped
        )

    @is_move.setter
    def is_move(self, value: bool):
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
    def is_push_or_pull(self) -> bool:
        """True if pusher also moved a box."""
        return self._box_moved and not self._pusher_selected and not self._pusher_jumped

    @is_push_or_pull.setter
    def is_push_or_pull(self, value: bool):
        if value:
            self._box_moved = True
            self._pusher_jumped = False
            self._pusher_selected = False
        else:
            self._box_moved = False
            self._moved_box_id = None

    @property
    def is_pusher_selection(self) -> bool:
        """
        True if this move is part of change active pusher sequence in Multiban games.
        """
        return self._pusher_selected and not self._pusher_jumped and not self._box_moved

    @is_pusher_selection.setter
    def is_pusher_selection(self, value: bool):
        if value:
            self._pusher_selected = True
            self._box_moved = False
            self._pusher_jumped = False
            self._moved_box_id = None
        else:
            self._pusher_selected = False

    @property
    def is_jump(self) -> bool:
        """
        True if this move is part of pusher jump sequence in
        :attr:`.SolvingMode.REVERSE` games.
        """
        return self._pusher_jumped and not self._box_moved and not self._pusher_selected

    @is_jump.setter
    def is_jump(self, value: bool):
        if value:
            self._pusher_jumped = True
            self._pusher_selected = False
            self._box_moved = False
            self._moved_box_id = None
        else:
            self._pusher_jumped = False
