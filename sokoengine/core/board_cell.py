from .helpers import PrettyPrintable, EqualityComparable, SokoengineError
from ..io.text_utils import BoardEncodingCharacters, is_wall, is_pusher, \
    is_goal, is_empty_floor, is_box


class BoardCell(PrettyPrintable, EqualityComparable):
    """
    Stores properties of one cell in board layout.
    Note that there is no game logic encoded in this class. It is perfectly fine
    to put pusher on wall cell (in which case wall will be replaced by pusher).
    This is by design: BoardCell is value class, not game logic class.
    """

    _has_box      = False
    _has_pusher   = False
    _has_goal     = False
    _is_wall     = False
    is_in_playable_area = False
    is_deadlock = False

    def __init__(self, chr = BoardEncodingCharacters.FLOOR.value):
        if is_wall(chr):
            self.is_wall = True
        elif is_pusher(chr):
            self.has_pusher = True
            if is_goal(chr):
                self.has_goal = True
        elif is_box(chr):
            self.has_box = True
            if is_goal(chr):
                self.has_goal = True
        elif is_goal(chr):
            self.has_goal = True
        elif is_empty_floor(chr):
            self.clear()
        else:
            raise SokoengineError("Invalid character in BoardCell initializer!")

    def __representation_attributes__(self):
        return {
            'has_pusher': self.has_pusher,
            'has_box': self.has_box,
            'has_goal': self.has_goal,
            'is_wall': self.is_wall,
            'is_in_playable_area': self.is_in_playable_area,
            'is_deadlock': self.is_deadlock,
        }

    def __equality_attributes__(self):
        return (self.is_wall, self.has_pusher, self.has_box, self.has_goal,)

    def to_s(self, use_visible_floor = False):
        """
        Converts self to printable character (BoardEncondingCharacters value)
        """
        retv = BoardEncodingCharacters.FLOOR.value

        if not self.has_box and not self.has_goal and not self.has_pusher:
            if self.is_wall:
                retv = BoardEncodingCharacters.WALL.value
            else:
                retv = (
                    BoardEncodingCharacters.VISIBLE_FLOOR.value
                    if use_visible_floor
                    else BoardEncodingCharacters.FLOOR.value
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
        self._is_wall = self._has_box = self._has_goal = self._has_pusher = False
        return self

    def switch_box_and_goal(self):
        if self.has_box and not self.has_goal:
            self._has_box = False
            self._has_goal = True
        elif not self.has_box and self.has_goal and not self.has_pusher:
            self._has_box = True
            self._has_goal = False
        return self

    @property
    def has_piece(self):
        return self.has_pusher or self.has_box or self.has_goal

    @property
    def is_empty_floor(self):
        return (
            not self.has_pusher and
            not self.has_box and
            not self.has_goal and
            not self.is_wall
        )

    @property
    def is_border_element(self):
        """
        True if this is either a wall or box on goal.
        """
        return self.is_wall or (self.has_box and self.has_goal)

    @property
    def can_put_pusher_or_box(self):
        return (
            not self.has_box and
            not self.has_pusher and
            not self.is_wall
        )

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
