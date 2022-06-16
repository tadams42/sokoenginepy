from ..io import Puzzle


class BoardCell:
    """
    Stores properties of one cell in board layout.

    Note:
        There is no game logic encoded in this class. It is perfectly fine to put
        pusher on wall cell (in which case wall will be replaced by pusher). This is
        by design: :class:`.BoardCell` is value class, not game logic class.
    """

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
        character: str = Puzzle.FLOOR,
        is_in_playable_area: bool = False,
        is_deadlock: bool = False,
    ):
        self._has_box: bool = False
        self._has_pusher: bool = False
        self._has_goal: bool = False
        self._is_wall: bool = False
        self.is_in_playable_area: bool = is_in_playable_area
        self.is_deadlock: bool = is_deadlock

        if not Puzzle.is_empty_floor(character):
            if Puzzle.is_wall(character):
                self.is_wall = True
            elif Puzzle.is_pusher(character):
                self.has_pusher = True
                if Puzzle.is_goal(character):
                    self.has_goal = True
            elif Puzzle.is_box(character):
                self.has_box = True
                if Puzzle.is_goal(character):
                    self.has_goal = True
            elif Puzzle.is_goal(character):
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
            and self.is_wall == Puzzle.is_wall(rv)
            and self.has_pusher == Puzzle.is_pusher(rv)
            and self.has_box == Puzzle.is_box(rv)
            and self.has_goal == Puzzle.is_goal(rv)
        )

    def __ne__(self, rv):
        return not self == rv

    def __str__(self):
        return self.to_str(use_visible_floor=False)

    def __repr__(self):
        return "BoardCell('{0}')".format(str(self))

    def to_str(self, use_visible_floor: bool = False) -> str:
        retv = Puzzle.FLOOR

        if not self.has_piece:
            if self.is_wall:
                retv = Puzzle.WALL
            else:
                retv = Puzzle.VISIBLE_FLOOR if use_visible_floor else Puzzle.FLOOR
        elif not self.has_box and not self.has_goal and self.has_pusher:
            retv = Puzzle.PUSHER
        elif not self.has_box and self.has_goal and not self.has_pusher:
            retv = Puzzle.GOAL
        elif not self.has_box and self.has_goal and self.has_pusher:
            retv = Puzzle.PUSHER_ON_GOAL
        elif self.has_box and not self.has_goal and not self.has_pusher:
            retv = Puzzle.BOX
        else:
            retv = Puzzle.BOX_ON_GOAL

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
