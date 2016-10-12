from ..common import EqualityComparable, PrettyPrintable
from .input_output import (BoardConversionError, BoardEncodingCharacters,
                           is_box, is_empty_floor, is_goal, is_pusher, is_wall)


class BoardCell(PrettyPrintable, EqualityComparable):
    """Stores properties of one cell in board layout.

    Note:
        There is no game logic encoded in this class. It is perfectly fine to
        put pusher on wall cell (in which case wall will be replaced by pusher).
        This is by design: :class:`BoardCell` is value class, not game logic
        class.
    """

    def __init__(self, character=BoardEncodingCharacters.FLOOR):
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

    @property
    def _representation_attributes(self):
        return {
            'has_pusher': self.has_pusher,
            'has_box': self.has_box,
            'has_goal': self.has_goal,
            'is_wall': self.is_wall,
            'is_in_playable_area': self.is_in_playable_area,
            'is_deadlock': self.is_deadlock,
        }

    @property
    def _equality_attributes(self):
        return (self.is_wall,
                self.has_pusher,
                self.has_box,
                self.has_goal,)

    def to_s(self, use_visible_floor=False):
        """Converts self to string (for printing boards in textual format)."""
        retv = BoardEncodingCharacters.FLOOR.value

        if not self.has_box and not self.has_goal and not self.has_pusher:
            if self.is_wall:
                retv = BoardEncodingCharacters.WALL.value
            else:
                retv = (
                    BoardEncodingCharacters.VISIBLE_FLOOR.value if
                    use_visible_floor else BoardEncodingCharacters.FLOOR.value
                )
        elif not self.has_box and not self.has_goal and self.has_pusher:
            retv = BoardEncodingCharacters.PUSHER.value
        elif not self.has_box and self.has_goal and not self.has_pusher:
            retv = BoardEncodingCharacters.GOAL.value
        elif not self.has_box and self.has_goal and self.has_pusher:
            retv = BoardEncodingCharacters.PUSHER_ON_GOAL.value
        elif self.has_box and not self.has_goal and not self.has_pusher:
            retv = BoardEncodingCharacters.BOX.value
        else:
            retv = BoardEncodingCharacters.BOX_ON_GOAL.value

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
