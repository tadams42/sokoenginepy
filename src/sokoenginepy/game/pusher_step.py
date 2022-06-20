from .config import Config, Direction


class PusherStep:
    """
    Represents single step of pusher movement.

    Single step can be:

    - ``move``: pusher moved without pushing box
    - ``push/pull``: pusher pushed or pulled a box
    - ``jump``: pusher jumped
    - ``pusher selection``: pusher was selected among other pushers on board

    Arguments:
        direction: direction in which movement was performed.
        moved_box_id: ID of a box that was pushed or `Config.NO_ID`. Box usually
            gets it's ID from `BoardManager`.
        is_jump: flag marking this step as part of pusher jump in reverse solving
            mode. See `Mover` for more details about reverse movement.
        is_pusher_selection: marks this step as part of pusher selecting sequence on
            boards with multiple pushers (Multiban game variant)
        pusher_id: ID of pusher that performed movement. Pusher usually
            gets it's ID from `BoardManager`.
        is_current_pos: flags this step as current position in game snapshot

    Raises:
        ValueError: single step can only be one thing at a time: ``move``, ``push/pull``
            or ``jump``.

    See Also:
        - :class:`Mover`
        - :class:`BoardManager`
        - :class:`SokobanPlus`
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

        #: :class:`Direction` of movement
        self.direction: Direction = direction
        self.moved_box_id = moved_box_id
        self.pusher_id = pusher_id
        self._pusher_jumped = is_jump
        self._pusher_selected = is_pusher_selection
        #: flags this step as current position in game snapshot
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
                box_id = (
                    "moved_box_id=Config.DEFAULT_ID + "
                    f"{self.moved_box_id - Config.DEFAULT_ID}"
                )

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

        When setting box ID on ie. ``jump``, that ``jump`` will become ``push``.
        To change ``push`` into ``move``, set box ID to `Config.NO_ID`.

        Setting it to invalid value will silently set it to `.Config.NO_ID`.
        """
        return self._moved_box_id

    @moved_box_id.setter
    def moved_box_id(self, value: int):
        if value == Config.NO_ID or value < Config.DEFAULT_ID:
            self._moved_box_id = Config.NO_ID
        else:
            self._moved_box_id = value
            self._pusher_selected = False
            self._pusher_jumped = False

    @property
    def pusher_id(self) -> int:
        """
        ID of pusher that performed movement.

        Pusher ID must always be valid. When setting it to invalid value, PusherStep
        will silently set pusher ID to `Config.DEFAULT_ID`.
        """
        return self._pusher_id

    @pusher_id.setter
    def pusher_id(self, value: int):
        if value == Config.NO_ID or value < Config.DEFAULT_ID:
            self._pusher_id = Config.DEFAULT_ID
        else:
            self._pusher_id = value

    @property
    def is_move(self) -> bool:
        """
        True if pusher didn't move box, didn't jump and didn't select another pusher.
        """
        return (
            self.moved_box_id == Config.NO_ID
            and not self._pusher_selected
            and not self._pusher_jumped
        )

    @property
    def is_push_or_pull(self) -> bool:
        """
        True if pusher moved a box.
        """
        return (
            self.moved_box_id != Config.NO_ID
            and not self._pusher_selected
            and not self._pusher_jumped
        )

    @property
    def is_pusher_selection(self) -> bool:
        """
        True if this step is part of pusher selection sequence in ``Multiban`` games.
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
        True if this move is part of jump sequence in :attr:`.SolvingMode.REVERSE`
        games.
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
