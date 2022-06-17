from typing import Optional

from .config import Config, Direction


class PusherStep:
    """
    Represents single step of pusher movement.

    - ``move`` - pusher moved without pushing box
    - ``push/pull`` - pusher moved and pushed a box in front of it (
      :attr:`.SolvingMode.FORWARD`) or pusher moved and pulled a box behind it
      (:attr:`.SolvingMode.REVERSE`)
    - ``jump`` - single step in pusher jump sequence (jumps are allowed only in
      :attr:`.SolvingMode.REVERSE`)
    - ``pusher selection`` - single step in sequence describing focus change of active
      pusher in Multiban games
    """

    __slots__ = [
        "_pusher_selected",
        "_pusher_jumped",
        "_pusher_id",
        "_moved_box_id",
        "direction",
        "is_current_pos",
    ]

    def __init__(
        self,
        direction: Direction = Direction.LEFT,
        moved_box_id: int = Config.NO_ID,
        is_jump: bool = False,
        is_pusher_selection: bool = False,
        pusher_id: int = Config.DEFAULT_ID,
        is_current_pos: bool = False,
    ):
        box_moved = moved_box_id != Config.NO_ID or moved_box_id >= Config.DEFAULT_ID

        if box_moved and is_pusher_selection and is_jump:
            raise ValueError(
                "PusherStep can't be everything, a push, a jump and a pusher "
                "selection, all at once!"
            )
        if box_moved and is_jump:
            raise ValueError("PusherStep can't be both, a push and a jump!")
        if box_moved and is_pusher_selection:
            raise ValueError("PusherStep can't be both, a push and a pusher selection!")
        if is_jump and is_pusher_selection:
            raise ValueError("PusherStep can't be both, a jump and a pusher selection!")

        self._moved_box_id: int
        self._pusher_id: int

        self.direction: Direction = direction
        self.moved_box_id = moved_box_id
        self.pusher_id = pusher_id
        self._pusher_jumped = is_jump
        self._pusher_selected = is_pusher_selection
        self.is_current_pos = is_current_pos

    def __repr__(self):
        pusher_id = None
        if self.pusher_id != Config.DEFAULT_ID:
            pusher_id = (
                f"pusher_id=Config.DEFAULT_ID + {self.pusher_id - Config.DEFAULT_ID}"
            )

        box_id = None
        if self.moved_box_id != Config.NO_ID:
            if self.moved_box_id == Config.DEFAULT_ID:
                box_id = "moved_box_id=Config.DEFAULT_ID"
            else:
                box_id = f"moved_box_id=Config.DEFAULT_ID + {self.moved_box_id - Config.DEFAULT_ID}"

        jump = None
        if self.is_jump:
            jump = "is_jump=True"

        pusher_select = None
        if self.is_pusher_selection:
            pusher_select = "is_pusher_selection=True"

        current_pos = None
        if self.is_current_pos:
            current_pos = "is_current_pos=True"

        args = ", ".join(
            _
            for _ in [
                str(self.direction),
                box_id,
                jump,
                pusher_select,
                pusher_id,
                current_pos,
            ]
            if _
        )

        return f"PusherStep({args})"

    def __str__(self):
        return repr(self)

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
    def moved_box_id(self) -> int:
        """
        ID of box that was moved or `Config.NO_ID` if no box was moved.
        """
        return self._moved_box_id

    @moved_box_id.setter
    def moved_box_id(self, value: int):
        """
        Updates ID of moved box and if `value` is valid, also changes this to push/pull.
        To remove box ID and change this to move (instead of push/pull), set `value`
        equal to `Config.NO_ID`.
        """
        if value == Config.NO_ID or value < Config.DEFAULT_ID:
            self._moved_box_id = Config.NO_ID
        else:
            self._moved_box_id = value
            self._pusher_selected = False
            self._pusher_jumped = False

    @property
    def pusher_id(self) -> int:
        """ID of pusher that performed movement."""
        return self._pusher_id

    @pusher_id.setter
    def pusher_id(self, value: int):
        """
        Note:
            Pusher ID can't be illegal value. If ``value`` is illegal, ``pusher_id``
            will become `Config.DEFAULT_ID`
        """
        if value == Config.NO_ID or value < Config.DEFAULT_ID:
            self._pusher_id = Config.DEFAULT_ID
        else:
            self._pusher_id = value

    @property
    def is_move(self) -> bool:
        """
        True if pusher didn't move box, didn't jump and didn't chang focus to other
        pusher.
        """
        return (
            self.moved_box_id == Config.NO_ID
            and not self._pusher_selected
            and not self._pusher_jumped
        )

    @property
    def is_push_or_pull(self) -> bool:
        """True if pusher moved a box."""
        return (
            self.moved_box_id != Config.NO_ID
            and not self._pusher_selected
            and not self._pusher_jumped
        )

    @property
    def is_pusher_selection(self) -> bool:
        """
        True if this move is part of change active pusher sequence in Multiban games.
        """
        return self._pusher_selected

    @is_pusher_selection.setter
    def is_pusher_selection(self, value: bool):
        if value:
            self._pusher_selected = True
            self._pusher_jumped = False
            self._moved_box_id = Config.NO_ID
        else:
            self._pusher_selected = False

    @property
    def is_jump(self) -> bool:
        """
        True if this move is part of pusher jump sequence in
        :attr:`.SolvingMode.REVERSE` games.
        """
        return self._pusher_jumped

    @is_jump.setter
    def is_jump(self, value: bool):
        if value:
            self._pusher_jumped = True
            self._pusher_selected = False
            self._moved_box_id = Config.NO_ID
        else:
            self._pusher_jumped = False
