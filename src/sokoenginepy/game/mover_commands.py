from abc import ABC, abstractmethod

from .. import utilities


class MoverCommand(ABC):
    def __init__(self, mover):
        self._mover = mover
        self._moves = []
        self._rendered_moves = []

    @abstractmethod
    def redo(self):
        """Redoes movement command."""
        pass

    @abstractmethod
    def undo(self):
        """Undoes movement command."""
        pass

    @property
    def mover(self):
        return self._mover

    @property
    def render(self):
        """
        Sequence of :class:`.AtomicMove` from last command execution (redo or
        undo).

        This sequence shows the moves like they would be rendered in GUI.
        Bacause of that, it shows different moves between undo and redo calls.

        See Also:
            :attr:`.Mover.last_move`
        """
        return self._rendered_moves

    @property
    def moves(self):
        """
        Sequence of :class:`.AtomicMove` as a result of redo execution.

        This sequence shows the moves like they would be stored in
        :class:`.Snapshot` and remains same between undo and redo executions.
        """
        return self._moves


class MetaclassMediator(type(MoverCommand), utilities.InheritableDocstrings):
    pass


class SelectPusherCommand(MoverCommand, metaclass=MetaclassMediator):
    def __init__(self, mover, pusher_id):
        super().__init__(mover)
        self._new_pusher_id = pusher_id
        self._old_pusher_id = self._mover.selected_pusher

    @copy_ancestor_docstring
    def redo(self):
        self._mover.select_pusher(self._new_pusher_id)
        self._moves = self._mover.last_move
        self._rendered_moves = self._mover.last_move

    @copy_ancestor_docstring
    def undo(self):
        self._mover.select_pusher(self._old_pusher_id)
        self._rendered_moves = self._mover.last_move

    @property
    def old_pusher_id(self):
        return self._old_pusher_id

    @property
    def new_pusher_id(self):
        return self._new_pusher_id


class JumpCommand(MoverCommand, metaclass=MetaclassMediator):
    def __init__(self, mover, final_position):
        super().__init__(mover)
        self._initial_position = mover.state.pusher_position(
            mover.selected_pusher
        )
        self._final_position = final_position

    @copy_ancestor_docstring
    def redo(self):
        self._mover.jump(self._final_position)
        self._moves = self._mover.last_move
        self._rendered_moves = self._mover.last_move

    @copy_ancestor_docstring
    def undo(self):
        self._mover.jump(self._initial_position)
        self._rendered_moves = self._mover.last_move

    @property
    def initial_position(self):
        return self._initial_position

    @property
    def final_position(self):
        return self._final_position


class MoveCommand(MoverCommand, metaclass=MetaclassMediator):
    def __init__(self, mover, direction):
        super().__init__(mover)
        self._direction = direction

    @property
    def direction(self):
        return self._direction

    @copy_ancestor_docstring
    def redo(self):
        self._mover.move(self._direction)
        self._moves = self._mover.last_move
        self._rendered_moves = self._mover.last_move

    @copy_ancestor_docstring
    def undo(self):
        self._mover.last_move = self._moves
        self._mover.undo_last_move()
        self._rendered_moves = self._mover.last_move
