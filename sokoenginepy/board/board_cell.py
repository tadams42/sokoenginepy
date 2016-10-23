from .input_output import (BoardConversionError, BoardCharacters,
                           is_box, is_empty_floor, is_goal, is_pusher, is_wall)


class BoardCell:
    """Stores properties of one cell in board layout.

    Note:
        There is no game logic encoded in this class. It is perfectly fine to
        put pusher on wall cell (in which case wall will be replaced by pusher).
        This is by design: :class:`BoardCell` is value class, not game logic
        class.
    """

    def __init__(self, character=BoardCharacters.FLOOR):
        self._has_box = False
        self._has_pusher = False
        self._has_goal = False
        self._is_wall = False
        self.is_in_playable_area = False
        self.is_deadlock = False

        # Most of the board space consists of empty floors, thus a chance this
        # first test succeeds is larger than for other cases. This means that
        # other branches will not be executed most of the time, which means
        # whole method runs faster.
        if not is_empty_floor(character):
            if is_wall(character):
                self.is_wall = True
            elif is_pusher(character):
                self.has_pusher = True
                if is_goal(character):
                    self.has_goal = True
            elif is_box(character):
                self.has_box = True
                if is_goal(character):
                    self.has_goal = True
            elif is_goal(character):
                self.has_goal = True
            else:
                raise BoardConversionError(
                    BoardConversionError.NON_BOARD_CHARS_FOUND
                )

    def __eq__(self, rv):
        return (
            self.is_wall == rv.is_wall and
            self.has_pusher == rv.has_pusher and
            self.has_box == rv.has_box and
            self.has_goal == rv.has_goal
        )

    def __str__(self):
        return self._str_helper.value

    def __repr__(self):
        return "BoardCell({0})".format(self._str_helper)

    @property
    def _str_helper(self):
        from ..input_output import OUTPUT_SETTINGS
        retv = BoardCharacters.FLOOR

        if not self.has_box and not self.has_goal and not self.has_pusher:
            if self.is_wall:
                retv = BoardCharacters.WALL
            else:
                retv = (
                    BoardCharacters.VISIBLE_FLOOR
                    if OUTPUT_SETTINGS.use_visible_floors
                    else BoardCharacters.FLOOR
                )
        elif not self.has_box and not self.has_goal and self.has_pusher:
            retv = BoardCharacters.PUSHER
        elif not self.has_box and self.has_goal and not self.has_pusher:
            retv = BoardCharacters.GOAL
        elif not self.has_box and self.has_goal and self.has_pusher:
            retv = BoardCharacters.PUSHER_ON_GOAL
        elif self.has_box and not self.has_goal and not self.has_pusher:
            retv = BoardCharacters.BOX
        else:
            retv = BoardCharacters.BOX_ON_GOAL

        return retv

    def clear(self):
        """Clears cell, converting it to empty floor."""
        self._is_wall = self._has_box = self._has_goal = self._has_pusher = False
        return self

    def switch_box_and_goal(self):
        """Changes box into goal and vice versa.

        In case there is pusher on goal, does nothing.
        """
        if self.has_box and not self.has_goal:
            self._has_box = False
            self._has_goal = True
        elif not self.has_box and self.has_goal and not self.has_pusher:
            self._has_box = True
            self._has_goal = False
        return self

    @property
    def has_piece(self):
        """True if there is pusher, box or goal on this cell."""
        return self.has_pusher or self.has_box or self.has_goal

    @property
    def is_empty_floor(self):
        """True if there is no pieces and no wall on this cell."""
        return (
            not self.has_pusher and not self.has_box and not self.has_goal and
            not self.is_wall
        )

    @property
    def is_border_element(self):
        """True if this is either a wall or box on goal."""
        return self.is_wall or (self.has_box and self.has_goal)

    @property
    def can_put_pusher_or_box(self):
        """True if this cell allows putting box or pusher on self.

        Note:
            This method isn't used by others in class, thus nothing prevents
            putting box on wall (which replaces that wall with box). This method
            can be used by higher game logic classes to implement actual game
            logic.
        """
        return not self.has_box and not self.has_pusher and not self.is_wall

    @property
    def has_box(self):
        return self._has_box

    @has_box.setter
    def has_box(self, value):
        if value:
            self._has_box = True
            self._is_wall = False
            self._has_pusher = False
        else:
            self._has_box = False

    def put_box(self):
        self.has_box = True
        return self

    def remove_box(self):
        self.has_box = False
        return self

    @property
    def has_goal(self):
        return self._has_goal

    @has_goal.setter
    def has_goal(self, value):
        if value:
            self._has_goal = True
            self._is_wall = False
        else:
            self._has_goal = False

    def put_goal(self):
        self.has_goal = True
        return self

    def remove_goal(self):
        self.has_goal = False
        return self

    @property
    def has_pusher(self):
        return self._has_pusher

    @has_pusher.setter
    def has_pusher(self, value):
        if value:
            self._has_pusher = True
            self._has_box = False
            self._is_wall = False
        else:
            self._has_pusher = False

    def put_pusher(self):
        self.has_pusher = True
        return self

    def remove_pusher(self):
        self.has_pusher = False
        return self

    @property
    def is_wall(self):
        return self._is_wall

    @is_wall.setter
    def is_wall(self, value):
        if value:
            self._is_wall = True
            self._has_box = False
            self._has_goal = False
            self._has_pusher = False
        else:
            self._is_wall = False
