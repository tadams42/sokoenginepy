from enum import IntEnum
from itertools import groupby

from ...manager import DEFAULT_PIECE_ID, CellAlreadyOccupiedError, HashedBoardManager
from ...snapshot import AtomicMove


class SolvingMode(IntEnum):
    FORWARD = 0
    REVERSE = 1

    def __repr__(self):
        return "SolvingMode." + self.name


class NonPlayableBoardError(RuntimeError):
    def __init__(self):
        super().__init__("Board is not playable!")


class IllegalMoveError(RuntimeError):
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

        - if position allows pull that pull is optional (pusher is allowed to move
          without pull even if pull is possible).
        - default behavior is to always pull boxes but that can be changed any time
          through `.pulls_boxes`

    - pusher can't push boxes

    - pusher is allowed to jump over boxes and walls

        - jumps are allowed only before first pull is done

    - board starts in solved state: positions of boxes and goals are switched

    **History management**

    Mover only stores last performed move in history and it doesn't offer redo.
    Failed moves, undo and non-moves (ie. selecting already selected pusher or
    jumping on same position pusher is already standing on) clear undo history.

    Args:
        board (VariantBoard): Instance of :class:`.VariantBoard` subclasses
        solving_mode (SolvingMode): start the game in this solving mode

    Warning:
        :class:`.Mover` operates directly on referenced game board. Because of that,
        this board should not be edited outside of :class:`.Mover` once
        :class:`.Mover` instance had been attached to it: editing the board will
        corrupt :class:`.Mover` internal state. For the same reason, it is not
        allowed to attach two movers to same game board.
    """

    def __init__(self, board, solving_mode=SolvingMode.FORWARD):
        self._manager = HashedBoardManager(board)
        self._solving_mode = solving_mode
        self._pulls_boxes = True
        self._selected_pusher = DEFAULT_PIECE_ID
        self._pull_count = 0
        self._last_move = []

        if not self._manager.is_playable:
            raise NonPlayableBoardError

        if self._solving_mode == SolvingMode.REVERSE:
            self._manager.switch_boxes_and_goals()

    @property
    def board(self):
        """Board on which :class:`.Mover` is operating on"""
        return self._manager.board

    @property
    def solving_mode(self):
        """:class:`.Mover` operation mode (:class:`.SolvingMode`)."""
        return self._solving_mode

    @property
    def board_manager(self):
        """Current board manager (:class:`.HashedBoardManager`)."""
        return self._manager

    @property
    def selected_pusher(self):
        """ID of pusher that will perform next move.

        See Also:
            :meth:`.select_pusher`
        """
        return self._selected_pusher

    @property
    def pulls_boxes(self):
        """
        Select behavior in `.SolvingMode.REVERSE` mode when pusher is moving away
        from box.

        See Also:
            :meth:`.move`
        """
        return self._pulls_boxes

    @pulls_boxes.setter
    def pulls_boxes(self, rv):
        self._pulls_boxes = rv

    @property
    def last_move(self):
        """Sequence of :class:`.AtomicMove` that contains most recent movement.

        Whenever :class:`.Mover` performs any movemet or pusher selection, it puts
        resulting :class:`.AtomicMove` into this sequence in order atomic moves
        happened.

        This is useful for movement animation in GUI. After Mover performs movement,
        GUI has enough information to know what was performed and to choose which
        animations to render for that.

        It is also possible to set this to some external sequence of moves. In that
        case, calling :meth:`.undo_last_move` will cause Mover to try to undo that
        external sequence of atomic moves.

        Example:

            >>> from sokoenginepy import Mover, SokobanBoard, AtomicMove, Direction
            >>> board = SokobanBoard(board_str='\\n'.join([
            ...     '    #####',
            ...     '    #  @#',
            ...     '    #$  #',
            ...     '  ###  $##',
            ...     '  #  $ $ #',
            ...     '### # ## #   ######',
            ...     '#   # ## #####  ..#',
            ...     '# $  $          ..#',
            ...     '##### ### #@##  ..#',
            ...     '    #     #########',
            ...     '    #######'
            ... ]))
            >>> mover = Mover(board)
            >>> mover.last_move = [AtomicMove(Direction.UP), AtomicMove(Direction.RIGHT)]
            >>> mover.undo_last_move()
            >>> mover.board
            SokobanBoard(board_str='\\n'.join([
                '    #####          ',
                '    #   #          ',
                '    #$@ #          ',
                '  ###  $##         ',
                '  #  $ $ #         ',
                '### # ## #   ######',
                '#   # ## #####  ..#',
                '# $  $          ..#',
                '##### ### #@##  ..#',
                '    #     #########',
                '    #######        '
            ]))
            >>> mover.last_move
            [AtomicMove(Direction.LEFT, box_moved=False), AtomicMove(Direction.DOWN, box_moved=False)]

        Warning:
            Subsequent movement overwrites this meaning that Mover can only undo last
            move performed (it doesn't keep whole history of movement, only the last
            move).
        """
        return self._last_move

    @last_move.setter
    def last_move(self, rv):
        self._last_move = rv

    def select_pusher(self, pusher_id):
        """
        Selects pusher that will perform next move.

        Mover always selects :data:`.DEFAULT_PIECE_ID` before any movements is
        performed. This means that for single-pusher boards, that single pusher is
        always automatically selected and this method doesn't need to be called.

        Args:
            pusher_id (int): ID of pusher

        See Also:
            `.BoardManager.pushers_ids`
        """

        if pusher_id == self._selected_pusher:
            return

        old_pusher_position = self._manager.pusher_position(self._selected_pusher)
        new_pusher_position = self._manager.pusher_position(pusher_id)
        selection_path = self._manager.board.positions_path_to_directions_path(
            self._manager.board.find_jump_path(old_pusher_position, new_pusher_position)
        )

        self._last_move = []
        for direction in selection_path:
            atomic_move = AtomicMove(direction, False)
            atomic_move.is_pusher_selection = True
            self._last_move.append(atomic_move)

        self._selected_pusher = pusher_id

    def move(self, direction):
        """Moves currently selected pusher in ``direction``.

        In `.SolvingMode.FORWARD` mode, pushes the box in front of pusher (if there
        is one).

        In `.SolvingMode.REVERSE` mode pulls box together with pusher (if there is
        one and if ``self.pulls_boxes is True``).

        Args:
            direction (Direction): direction of movement

        Raises:
            .IllegalMoveError: for illegal moves
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

            - :class:`.Mover` is in `.SolvingMode.FORWARD` mode
            - pusher can't be dropped on ``new_position``
            - first pull had been made

        Raises:
            .IllegalMoveError: for illegal jumps
        """
        if self._pull_count != 0:
            raise IllegalMoveError("Jumps not allowed after first pull")

        if self._solving_mode != SolvingMode.REVERSE:
            raise IllegalMoveError("Jumps allowed only in reverse solving mode")

        old_position = self._manager.pusher_position(self._selected_pusher)
        if old_position == new_position:
            return

        try:
            self._manager.move_pusher_from(old_position, new_position)
        except CellAlreadyOccupiedError as exc:
            raise IllegalMoveError(str(exc))

        path = self._manager.board.positions_path_to_directions_path(
            self._manager.board.find_jump_path(old_position, new_position)
        )

        def jump_am(direction):
            atomic_move = AtomicMove(direction, False)
            atomic_move.is_jump = True
            atomic_move.pusher_id = self._selected_pusher
            return atomic_move

        self._last_move = [jump_am(direction) for direction in path]

    def undo_last_move(self):
        """
        Takes sequence of moves stored in self.last_move and undoes it.

        See Also:
            `.Mover.last_move`
        """
        new_last_moves = []
        old_last_moves = self._last_move

        jump_key = 0
        pusher_change_key = 1
        move_key = 2

        def key_functor(elem):
            if elem.is_jump:
                return jump_key
            if elem.is_pusher_selection:
                return pusher_change_key
            return move_key

        for moves_type, moves_group in groupby(reversed(old_last_moves), key_functor):
            if moves_type == move_key:
                for atomic_move in moves_group:
                    self._undo_atomic_move(atomic_move)
                    new_last_moves += self._last_move
            elif moves_type == jump_key:
                self._undo_jump(moves_group)
                new_last_moves += self._last_move
            else:
                self._undo_pusher_selection(moves_group)
                new_last_moves += self._last_move

        self._last_move = new_last_moves

    def _undo_atomic_move(self, atomic_move):
        options = MoveWorkerOptions()
        if self._solving_mode == SolvingMode.FORWARD:
            has_box_behind_pusher = self.board_manager.has_box_on(
                self._manager.board.neighbor(
                    self.board_manager.pusher_position(self.selected_pusher),
                    atomic_move.direction,
                )
            )

            if not atomic_move.is_move and not has_box_behind_pusher:
                raise IllegalMoveError("Requested push undo, but no box behind pusher!")
            options.force_pulls = not atomic_move.is_move
            options.increase_pull_count = False
            self._pull_or_move(atomic_move.direction.opposite, options)
        else:
            options.decrease_pull_count = True
            self._push_or_move(atomic_move.direction.opposite, options)

    def _undo_jump(self, jump_moves):
        path = [atomic_move.direction.opposite for atomic_move in jump_moves]
        old_position = self._manager.pusher_position(self._selected_pusher)
        new_position = self._manager.board.path_destination(old_position, path)
        self.jump(new_position)

    def _undo_pusher_selection(self, selection_moves):
        path = [atomic_move.direction.opposite for atomic_move in selection_moves]
        old_position = self._manager.pusher_position(self._selected_pusher)
        new_position = self._manager.board.path_destination(old_position, path)
        self.select_pusher(self._manager.pusher_id_on(new_position))

    def _push_or_move(self, direction, options):
        """
        Perform movement of currently selected pusher in ``direction``.

        In case there is a box in front of pusher, pushes it.
        """
        initial_pusher_position = self._manager.pusher_position(self._selected_pusher)
        in_front_of_pusher = self._manager.board.neighbor(
            initial_pusher_position, direction
        )

        if not in_front_of_pusher:
            raise IllegalMoveError(
                "Can't move pusher off board! (ID: "
                + "{0}, direction: {1})".format(self._selected_pusher, str(direction))
            )

        is_push = False
        in_front_of_box = None
        if self._manager.has_box_on(in_front_of_pusher):
            is_push = True
            in_front_of_box = self._manager.board.neighbor(
                in_front_of_pusher, direction
            )
            if not in_front_of_box:
                raise IllegalMoveError(
                    "Can't push box off board! (ID: "
                    + "{0}, direction: {1})".format(
                        self._manager.box_id_on(in_front_of_pusher), str(direction)
                    )
                )

            try:
                self._manager.move_box_from(in_front_of_pusher, in_front_of_box)
            except CellAlreadyOccupiedError as exc:
                raise IllegalMoveError(str(exc))

        try:
            self._manager.move_pusher_from(initial_pusher_position, in_front_of_pusher)
        except CellAlreadyOccupiedError as exc:
            raise IllegalMoveError(str(exc))

        atomic_move = AtomicMove(direction, is_push)
        atomic_move.pusher_id = self._selected_pusher
        if is_push:
            atomic_move.moved_box_id = self._manager.box_id_on(in_front_of_box)
            if options.decrease_pull_count and self._pull_count > 0:
                self._pull_count -= 1
        self._last_move = [atomic_move]

    def _pull_or_move(self, direction, options):
        """
        Perform movement of currently selected pusher in ``direction``.

        In case there is a box in behind of pusher, might pull it.
        """
        initial_pusher_position = self._manager.pusher_position(self._selected_pusher)
        in_front_of_pusher = self._manager.board.neighbor(
            initial_pusher_position, direction
        )

        if not in_front_of_pusher:
            raise IllegalMoveError(
                "Can't move pusher off board! (ID: "
                + "{0}, direction: {1})".format(self._selected_pusher, str(direction))
            )

        try:
            self._manager.move_pusher_from(initial_pusher_position, in_front_of_pusher)
        except CellAlreadyOccupiedError as exc:
            raise IllegalMoveError(str(exc))

        is_pull = False
        if options.force_pulls:
            behind_pusher = self._manager.board.neighbor(
                initial_pusher_position, direction.opposite
            )
            if behind_pusher and self._manager.board[behind_pusher].has_box:
                is_pull = True
                try:
                    self._manager.move_box_from(behind_pusher, initial_pusher_position)
                except CellAlreadyOccupiedError as exc:
                    raise IllegalMoveError(str(exc))
                if options.increase_pull_count:
                    self._pull_count += 1

        atomic_move = AtomicMove(direction, is_pull)
        atomic_move.pusher_id = self._selected_pusher
        if is_pull:
            atomic_move.moved_box_id = self._manager.box_id_on(initial_pusher_position)
        self._last_move = [atomic_move]
