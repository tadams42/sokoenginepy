from typing import ClassVar, Optional, Set, Union


class BoardConversionError(RuntimeError):
    """Exception risen when converting board to or from board strings."""

    pass


class BoardCell:
    """
    Stores properties of one cell in board layout.

    Note:
        There is no game logic encoded in this class. It is perfectly fine to put
        pusher on wall cell (in which case wall will be replaced by pusher). This is
        by design: :class:`.BoardCell` is value class, not game logic class.
    """

    WALL: ClassVar[str] = "#"
    PUSHER: ClassVar[str] = "@"
    PUSHER_ON_GOAL: ClassVar[str] = "+"
    BOX: ClassVar[str] = "$"
    BOX_ON_GOAL: ClassVar[str] = "*"
    GOAL: ClassVar[str] = "."
    FLOOR: ClassVar[str] = " "
    VISIBLE_FLOOR: ClassVar[str] = "-"
    ALT_PUSHER1: ClassVar[str] = "p"
    ALT_PUSHER2: ClassVar[str] = "m"
    ALT_PUSHER_ON_GOAL1: ClassVar[str] = "P"
    ALT_PUSHER_ON_GOAL2: ClassVar[str] = "M"
    ALT_BOX1: ClassVar[str] = "b"
    ALT_BOX_ON_GOAL1: ClassVar[str] = "B"
    ALT_GOAL1: ClassVar[str] = "o"
    ALT_VISIBLE_FLOOR1: ClassVar[str] = "_"

    #: Characters used in textual representation of boards and BoardCell
    CHARACTERS: ClassVar[Set[str]] = {
        WALL,
        PUSHER,
        PUSHER_ON_GOAL,
        BOX,
        BOX_ON_GOAL,
        GOAL,
        FLOOR,
        VISIBLE_FLOOR,
        ALT_PUSHER1,
        ALT_PUSHER2,
        ALT_PUSHER_ON_GOAL1,
        ALT_PUSHER_ON_GOAL2,
        ALT_BOX1,
        ALT_BOX_ON_GOAL1,
        ALT_GOAL1,
        ALT_VISIBLE_FLOOR1,
    }

    @classmethod
    def is_pusher_chr(cls, character: str) -> bool:
        return (
            character == cls.PUSHER
            or character == cls.ALT_PUSHER1
            or character == cls.ALT_PUSHER2
            or character == cls.PUSHER_ON_GOAL
            or character == cls.ALT_PUSHER_ON_GOAL1
            or character == cls.ALT_PUSHER_ON_GOAL2
        )

    @classmethod
    def is_box_chr(cls, character: str) -> bool:
        return (
            character == cls.BOX
            or character == cls.ALT_BOX1
            or character == cls.BOX_ON_GOAL
            or character == cls.ALT_BOX_ON_GOAL1
        )

    @classmethod
    def is_goal_chr(cls, character: str) -> bool:
        return (
            character == cls.GOAL
            or character == cls.ALT_GOAL1
            or character == cls.BOX_ON_GOAL
            or character == cls.ALT_BOX_ON_GOAL1
            or character == cls.PUSHER_ON_GOAL
            or character == cls.ALT_PUSHER_ON_GOAL1
            or character == cls.ALT_PUSHER_ON_GOAL2
        )

    @classmethod
    def is_empty_floor_chr(cls, character: str) -> bool:
        return (
            character == cls.FLOOR
            or character == cls.VISIBLE_FLOOR
            or character == cls.ALT_VISIBLE_FLOOR1
        )

    @classmethod
    def is_wall_chr(cls, character: str) -> bool:
        return character == cls.WALL

    __slots__ = [
        "_has_box",
        "_has_pusher",
        "_has_goal",
        "_is_wall",
        "is_in_playable_area",
        "is_deadlock",
    ]

    def __init__(
        self,
        character: str = FLOOR,
        is_in_playable_area: bool = False,
        is_deadlock: bool = False,
    ):
        self._has_box: bool = False
        self._has_pusher: bool = False
        self._has_goal: bool = False
        self._is_wall: bool = False
        self.is_in_playable_area: bool = is_in_playable_area
        self.is_deadlock: bool = is_deadlock

        if not self.is_empty_floor_chr(character):
            if self.is_wall_chr(character):
                self.is_wall = True
            elif self.is_pusher_chr(character):
                self.has_pusher = True
                if self.is_goal_chr(character):
                    self.has_goal = True
            elif self.is_box_chr(character):
                self.has_box = True
                if self.is_goal_chr(character):
                    self.has_goal = True
            elif self.is_goal_chr(character):
                self.has_goal = True
            else:
                raise ValueError("Illegal characters found in board string")

    def __eq__(self, rv):
        return (
            isinstance(rv, self.__class__)
            and self.is_wall == rv.is_wall
            and self.has_pusher == rv.has_pusher
            and self.has_box == rv.has_box
            and self.has_goal == rv.has_goal
        ) or (
            isinstance(rv, str)
            and self.is_wall == self.is_wall_chr(rv)
            and self.has_pusher == self.is_pusher_chr(rv)
            and self.has_box == self.is_box_chr(rv)
            and self.has_goal == self.is_goal_chr(rv)
        )

    def __ne__(self, rv):
        return not self == rv

    def __str__(self):
        return self.to_str(use_visible_floor=False)

    def __repr__(self):
        return "BoardCell('{0}')".format(str(self))

    def to_str(self, use_visible_floor: bool = False) -> str:
        retv = self.FLOOR

        if not self.has_piece:
            if self.is_wall:
                retv = self.WALL
            else:
                retv = self.VISIBLE_FLOOR if use_visible_floor else self.FLOOR
        elif not self.has_box and not self.has_goal and self.has_pusher:
            retv = self.PUSHER
        elif not self.has_box and self.has_goal and not self.has_pusher:
            retv = self.GOAL
        elif not self.has_box and self.has_goal and self.has_pusher:
            retv = self.PUSHER_ON_GOAL
        elif self.has_box and not self.has_goal and not self.has_pusher:
            retv = self.BOX
        else:
            retv = self.BOX_ON_GOAL

        return retv

    def clear(self):
        """Clears cell, converting it to empty floor."""
        self._is_wall = self._has_box = self._has_goal = self._has_pusher = False

    @property
    def has_piece(self) -> bool:
        """True if there is pusher, box or goal on this cell."""
        return self.has_pusher or self.has_box or self.has_goal

    @property
    def is_empty_floor(self) -> bool:
        """True if there is no pieces and no wall on this cell."""
        return not (self.has_pusher or self.has_box or self.has_goal or self.is_wall)

    @property
    def is_border_element(self) -> bool:
        """True if this is either a wall or box on goal."""
        return self.is_wall or (self.has_box and self.has_goal)

    @property
    def can_put_pusher_or_box(self) -> bool:
        """
        True if this cell allows putting box or pusher on self.

        Note:
            This method is not used by BoardCell modifiers (ie. `put_box`,
            `put_pusher`, etc...). As far as BoardCell is concerned, nothing prevents
            clients from putting box on wall (which replaces that wall with box).
            This method is intended to be used by higher game logic classes that
            would implement pusher movement in which case putting ie. pusher onto
            same cell where box is makes no sense.
        """
        return not (self.has_box or self.has_pusher or self.is_wall)

    @property
    def has_box(self) -> bool:
        return self._has_box

    @has_box.setter
    def has_box(self, value: bool):
        if value:
            self._has_box = True
            self._is_wall = False
            self._has_pusher = False
        else:
            self._has_box = False

    def put_box(self):
        self.has_box = True

    def remove_box(self):
        self.has_box = False

    @property
    def has_goal(self) -> bool:
        return self._has_goal

    @has_goal.setter
    def has_goal(self, value: bool):
        if value:
            self._has_goal = True
            self._is_wall = False
        else:
            self._has_goal = False

    def put_goal(self):
        self.has_goal = True

    def remove_goal(self):
        self.has_goal = False

    @property
    def has_pusher(self):
        return self._has_pusher

    @has_pusher.setter
    def has_pusher(self, value: bool):
        if value:
            self._has_pusher = True
            self._has_box = False
            self._is_wall = False
        else:
            self._has_pusher = False

    def put_pusher(self):
        self.has_pusher = True

    def remove_pusher(self):
        self.has_pusher = False

    @property
    def is_wall(self) -> bool:
        return self._is_wall

    @is_wall.setter
    def is_wall(self, value: bool):
        if value:
            self._is_wall = True
            self._has_box = False
            self._has_goal = False
            self._has_pusher = False
        else:
            self._is_wall = False
