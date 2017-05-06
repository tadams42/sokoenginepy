from copy import deepcopy
from itertools import groupby

from .. import board as module_board
from .. import snapshot, utilities
from .solving_mode import SolvingMode


class NonPlayableBoardError(utilities.SokoengineError):
    def __init__(self):
        super().__init__("Board is not playable!")


class IllegalMoveError(utilities.SokoengineError):
    pass


class MoveWorkerOptions:
    def __init__(self):
        self.decrease_pull_count = None
        self.increase_pull_count = None
        self.force_pulls = None


class Mover:
    """Implements game rules (on-board movement).

    Supports forward and reverse solving mode.

    **Forward solving mode**

    - pusher is allowed to push single box at the time
    - pusher can't pull boxes
    - pusher can't jump over boxes or walls

    **Reverse solving mode:**

    - pusher is allowed to pull single box at the time

        - if position allows pull that pull is optional (pusher is allowed to
          move without pull even if pull is possible). Default behavior is to
          always pull boxes but that can be changed any time through
          :meth:`Mover.pulls_boxes`

    - pusher can't push boxes
    - pusher is allowed to jump over boxes and walls

        - jumps are allowed only before first pull is done

    - board starts in solved state: positions of boxes and goals are switched

    **History management**

    Mover only stores last performed move in history and it doesn't offer
    redo. Failed moves, undo and non-moves (ie. selecting already selected
    pusher or jumping on same position pusher is already standing on) clear
    undo history.

    Args:
        board (VariantBoard): Instance of :class:`.VariantBoard` subclasses
        solving_mode (SolvingMode): start the game in this solving mode

    Warning:
        :class:`.Mover` operates directly on referenced game board. Because of
        that, this board should not be edited outside of :class:`.Mover`
        interface once :class:`.Mover` instance had been attached to it: editing
        the board will corrupt :class:`.Mover` internal state. For the same
        reason, it is not allowed to attach two movers to same game board.
    """

    def __init__(self, board, solving_mode=SolvingMode.FORWARD):
        self._state = module_board.HashedBoardState(board)
        self._solving_mode = solving_mode
        self._pulls_boxes = True
        self._selected_pusher = module_board.DEFAULT_PIECE_ID
        self._pull_count = 0
        self.__last_move = []

        if not self._state.is_playable:
            raise NonPlayableBoardError

        if self.solving_mode == SolvingMode.REVERSE:
            self.state.switch_boxes_and_goals()

    @property
    def board(self):
        """Board on which :class:`Mover` is operating on"""
        return self._state.board

    @property
    def solving_mode(self):
        """:class:`Mover` operation mode (:class:`.SolvingMode`)."""
        return self._solving_mode

    @property
    def state(self):
        """Current board state (:class:`.HashedBoardState`)."""
        return self._state

    @property
    def selected_pusher(self):
        """ID of pusher that will perform next move.

        For single-pusher boards, pusher is always automatically selected so
        this doesn't need to be called.

        Default is :data:`.DEFAULT_PIECE_ID`
        """
        return self._selected_pusher

    @selected_pusher.setter
    def selected_pusher(self, pusher_id):
        if pusher_id == self.selected_pusher:
            return

        old_pusher_position = self._state.pusher_position(self.selected_pusher)
        new_pusher_position = self._state.pusher_position(pusher_id)
        selection_path = self._state.board.position_path_to_direction_path(
            self._state.board.
            find_jump_path(old_pusher_position, new_pusher_position)
        )['path']

        self.__last_move = []
        for direction in selection_path:
            atomic_move = snapshot.AtomicMove(direction, False)
            atomic_move.is_pusher_selection = True
            self.__last_move.append(atomic_move)

        self._selected_pusher = pusher_id

    @property
    def pulls_boxes(self):
        """
        Select behavior in :attr:`.SolvingMode.REVERSE` mode when pusher is
        moving away from box.

        See Also:
            :meth:`.Mover.move`
        """
        return self._pulls_boxes

    @pulls_boxes.setter
    def pulls_boxes(self, rv):
        self._pulls_boxes = rv

    @property
    def last_move(self):
        """Sequence of :class:`.AtomicMove` that describes most recent movemt.

        Sequence contains one :class:`.AtomicMove` or (in case of jumps and
        pusher selections) more than one :class:`.AtomicMove`

        This is useful for generating movement animation in GUI after calling
        undo/redo
        """
        return self.__last_move

    def move(self, direction):
        """Moves currently selected pusher in ``direction``.

        In :attr:`.SolvingMode.FORWARD` mode, pushes the box in front of pusher
        (if there is one).

        In :attr:`.SolvingMode.REVERSE` mode pulls box together with pusher (if
        there is one and if ``self.pulls_boxes is True``).

        Args:
            direction (Direction): direction of movement

        Raises:
            IllegalMoveError: for illegal moves
        """
        options = MoveWorkerOptions()
        if self._solving_mode == SolvingMode.FORWARD:
            options.decrease_pull_count = False
            self._push_or_move(direction, options)
        else:
            options.force_pulls = self._pulls_boxes
            options.increase_pull_count = True
            self._pull_or_move(direction, options)

    def jump(self, new_position):
        """Currently selected pusher jumps to ``new_position``.

        Fails if

            - :class:`Mover` is in :attr:`.SolvingMode.FORWARD` mode
            - pusher can't be dropped on ``new_position``
            - first pull had been made

        Raises:
            IllegalMoveError: for illegal jumps
        """
        if self._pull_count != 0:
            raise IllegalMoveError('Jumps not allowed after first pull')

        if self.solving_mode != SolvingMode.REVERSE:
            raise IllegalMoveError('Jumps allowed only in reverse solving mode')

        old_position = self._state.pusher_position(self.selected_pusher)
        if old_position == new_position:
            return

        try:
            self._state.move_pusher_from(old_position, new_position)
        except module_board.CellAlreadyOccupiedError as exc:
            raise IllegalMoveError(str(exc))

        path = self._state.board.position_path_to_direction_path(
            self._state.board.find_jump_path(old_position, new_position)
        )['path']

        def jump_am(direction):
            atomic_move = snapshot.AtomicMove(direction, False)
            atomic_move.is_jump = True
            atomic_move.pusher_id = self.selected_pusher
            return atomic_move

        self.__last_move = [jump_am(direction) for direction in path]

    def __undo_impl(self):
        if len(self.__last_move) == 1:
            options = MoveWorkerOptions()
            if self.solving_mode == SolvingMode.FORWARD:
                options.force_pulls = True
                options.increase_pull_count = False
                self._pull_or_move(
                    self.__last_move[0].direction.opposite, options
                )
            else:
                options.decrease_pull_count = True
                self._push_or_move(
                    self.__last_move[0].direction.opposite, options
                )
        elif len(self.__last_move) > 1:
            path = [
                am.direction.opposite
                for am in reversed(self.__last_move)
            ]
            old_position = self._state.pusher_position(self.selected_pusher)
            new_position = self._state.board.path_destination(
                old_position, path
            )
            if self.__last_move[0].is_jump:
                self.jump(new_position)
            else:
                self.selected_pusher = self._state.pusher_id_on(new_position)

    def undo(self):
        """ Undoes most recent movement.

        See Also:
            :attr:`.Mover.last_move`
        """
        self.__undo_impl()

    def _undo(self, moves):
        """Treats ``moves`` as performed moves and tries to undo them.

        Returns:
            list: undo sequence of moves.
        """
        retv = []

        def key_functor(elem):
            if elem.is_jump:
                return 0
            if elem.is_pusher_selection:
                return 1
            return 2

        for undo_move in [list(g) for k, g in groupby(moves, key_functor)]:
            self.__last_move = undo_move
            self.__undo_impl()
            for undone_atomic_move in self.last_move:
                retv.append(deepcopy(undone_atomic_move))

        return retv

    def _push_or_move(self, direction, options):
        """Perform movement of currently selected pusher in ``direction``.

        In case there is a box in front of pusher, pushes it.
        """
        initial_pusher_position = self._state.pusher_position(
            self.selected_pusher
        )
        in_front_of_pusher = self._state.board.neighbor(
            initial_pusher_position, direction
        )

        if not in_front_of_pusher:
            raise IllegalMoveError(
                "Can't move pusher off board! (ID: " +
                "{0}, direction: {1})".
                format(self.selected_pusher, str(direction))
            )

        is_push = False
        in_front_of_box = None
        if self._state.has_box_on(in_front_of_pusher):
            is_push = True
            in_front_of_box = self._state.board.neighbor(
                in_front_of_pusher, direction
            )
            if not in_front_of_box:
                raise IllegalMoveError(
                    "Can't push box off board! (ID: " +
                    "{0}, direction: {1})".format(
                        self._state.box_id_on(in_front_of_pusher),
                        str(direction)
                    )
                )

            try:
                self._state.move_box_from(in_front_of_pusher, in_front_of_box)
            except module_board.CellAlreadyOccupiedError as exc:
                raise IllegalMoveError(str(exc))

        try:
            self._state.move_pusher_from(
                initial_pusher_position, in_front_of_pusher
            )
        except module_board.CellAlreadyOccupiedError as exc:
            raise IllegalMoveError(str(exc))

        atomic_move = snapshot.AtomicMove(direction, is_push)
        atomic_move.pusher_id = self.selected_pusher
        if is_push:
            atomic_move.moved_box_id = self._state.box_id_on(in_front_of_box)
            if options.decrease_pull_count and self._pull_count > 0:
                self._pull_count -= 1
        self.__last_move = [atomic_move]

    def _pull_or_move(self, direction, options):
        """Perform movement of currently selected pusher in ``direction``.

        In case there is a box in behind of pusher, might pull it.
        """
        initial_pusher_position = self._state.pusher_position(
            self.selected_pusher
        )
        in_front_of_pusher = self._state.board.neighbor(
            initial_pusher_position, direction
        )

        if not in_front_of_pusher:
            raise IllegalMoveError(
                "Can't move pusher off board! (ID: " +
                "{0}, direction: {1})".
                format(self.selected_pusher, str(direction))
            )

        try:
            self._state.move_pusher_from(
                initial_pusher_position, in_front_of_pusher
            )
        except module_board.CellAlreadyOccupiedError as exc:
            raise IllegalMoveError(str(exc))

        is_pull = False
        if options.force_pulls:
            behind_pusher = self._state.board.neighbor(
                initial_pusher_position, direction.opposite
            )
            if behind_pusher and self._state.board[behind_pusher].has_box:
                is_pull = True
                try:
                    self._state.move_box_from(
                        behind_pusher, initial_pusher_position
                    )
                except module_board.CellAlreadyOccupiedError as exc:
                    raise IllegalMoveError(str(exc))
                if options.increase_pull_count:
                    self._pull_count += 1

        atomic_move = snapshot.AtomicMove(direction, is_pull)
        atomic_move.pusher_id = self.selected_pusher
        if is_pull:
            atomic_move.moved_box_id = self._state.box_id_on(
                initial_pusher_position
            )
        self.__last_move = [atomic_move]
