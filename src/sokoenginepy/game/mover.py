from __future__ import annotations

import enum
from dataclasses import dataclass
from itertools import groupby
from typing import Iterable, List, Optional

from .board_graph import BoardGraph
from .board_manager import CellAlreadyOccupiedError
from .config import Direction, Config
from .hashed_board_manager import HashedBoardManager
from .pusher_step import PusherStep


class SolvingMode(enum.Enum):
    FORWARD = 0
    REVERSE = 1

    def __repr__(self):
        return "SolvingMode." + self.name


class NonPlayableBoardError(RuntimeError):
    def __init__(self):
        super().__init__("Board is not playable!")


class IllegalMoveError(RuntimeError):
    pass


@dataclass
class MoveWorkerOptions:
    decrease_pull_count: Optional[int] = None
    increase_pull_count: Optional[int] = None
    force_pulls: Optional[bool] = None


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

    Warning:
        :class:`.Mover` operates directly on referenced game board. Because of that,
        this board should not be edited outside of :class:`.Mover` once
        :class:`.Mover` instance had been attached to it: editing the board will
        corrupt :class:`.Mover` internal state. For the same reason, it is not
        allowed to attach two movers to same game board.
    """

    def __init__(
        self, board: BoardGraph, solving_mode: SolvingMode = SolvingMode.FORWARD
    ):
        """
        Args:
            board: Instance of :class:`.BoardGraph` subclasses
            solving_mode: start the game in this solving mode
        """
        self._manager = HashedBoardManager(board)
        self._solving_mode = solving_mode
        self._pulls_boxes = True
        self._selected_pusher: int = Config.DEFAULT_PIECE_ID
        self._pull_count: int = 0
        self._last_move: List[PusherStep] = []

        if not self._manager.is_playable:
            raise NonPlayableBoardError

        if self._solving_mode == SolvingMode.REVERSE:
            self._manager.switch_boxes_and_goals()

    @property
    def board(self) -> BoardGraph:
        """Board on which :class:`.Mover` is operating on"""
        return self._manager.board

    @property
    def solving_mode(self) -> SolvingMode:
        """:class:`.Mover` operation mode (:class:`.SolvingMode`)."""
        return self._solving_mode

    @property
    def board_manager(self) -> HashedBoardManager:
        """Current board manager (:class:`.HashedBoardManager`)."""
        return self._manager

    @property
    def selected_pusher(self) -> int:
        """ID of pusher that will perform next move.

        See Also:
            :meth:`.select_pusher`
        """
        return self._selected_pusher

    @property
    def pulls_boxes(self) -> bool:
        """
        Select behavior in `.SolvingMode.REVERSE` mode when pusher is moving away
        from box.

        See Also:
            :meth:`.move`
        """
        return self._pulls_boxes

    @pulls_boxes.setter
    def pulls_boxes(self, rv: bool):
        self._pulls_boxes = rv

    @property
    def last_move(self) -> List[PusherStep]:
        """Sequence of :class:`.PusherStep` that contains most recent movement.

        Whenever :class:`.Mover` performs any movement or pusher selection, it puts
        resulting :class:`.PusherStep` into this sequence in order pusher steps
        happened.

        This is useful for movement animation in GUI. After Mover performs movement,
        GUI has enough information to know what was performed and to choose which
        animations to render for that.

        It is also possible to set this to some external sequence of moves. In that
        case, calling :meth:`.undo_last_move` will cause Mover to try to undo that
        external sequence of pusher steps.

        Example:

            >>> from sokoenginepy.game import Mover, PusherStep, Direction, BoardGraph
            >>> from sokoenginepy.io import SokobanPuzzle
            >>> puzzle = SokobanPuzzle(board='\\n'.join([
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
            >>> board = BoardGraph(puzzle)
            >>> mover = Mover(board)
            >>> mover.last_move = [PusherStep(Direction.UP), PusherStep(Direction.RIGHT)]
            >>> mover.undo_last_move()
            >>> print(mover.board)
            ----#####----------
            ----#---#----------
            ----#$@-#----------
            --###--$##---------
            --#--$-$-#---------
            ###-#-##-#---######
            #---#-##-#####--..#
            #-$--$----------..#
            #####-###-#@##--..#
            ----#-----#########
            ----#######--------
            >>> mover.last_move
            [PusherStep(Direction.LEFT, box_moved=False), PusherStep(Direction.DOWN, box_moved=False)]

        Warning:
            Subsequent movement overwrites this meaning that Mover can only undo last
            move performed (it doesn't keep whole history of movement, only the last
            move).
        """
        return self._last_move

    @last_move.setter
    def last_move(self, rv: List[PusherStep]):
        self._last_move = rv

    def select_pusher(self, pusher_id: int):
        """
        Selects pusher that will perform next move.

        Mover always selects :data:`Config.DEFAULT_PIECE_ID` before any movements is
        performed. This means that for single-pusher boards, that single pusher is
        always automatically selected and this method doesn't need to be called.

        Args:
            pusher_id: ID of pusher

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
            pusher_step = PusherStep(direction, False)
            pusher_step.is_pusher_selection = True
            self._last_move.append(pusher_step)

        self._selected_pusher = pusher_id

    def move(self, direction: Direction):
        """Moves currently selected pusher in ``direction``.

        In `.SolvingMode.FORWARD` mode, pushes the box in front of pusher (if there
        is one).

        In `.SolvingMode.REVERSE` mode pulls box together with pusher (if there is
        one and if ``self.pulls_boxes is True``).

        Args:
            direction: direction of movement

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

    def jump(self, new_position: int):
        """Currently selected pusher jumps to ``new_position``.

        Fails if

            - :class:`.Mover` is in `.SolvingMode.FORWARD` mode
            - pusher can't be dropped on ``new_position``
            - first pull had been made

        Raises:
            IllegalMoveError: for illegal jumps
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
            pusher_step = PusherStep(direction, False)
            pusher_step.is_jump = True
            pusher_step.pusher_id = self._selected_pusher
            return pusher_step

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
                for pusher_step in moves_group:
                    self._undo_pusher_step(pusher_step)
                    new_last_moves += self._last_move
            elif moves_type == jump_key:
                self._undo_jump(moves_group)
                new_last_moves += self._last_move
            else:
                self._undo_pusher_selection(moves_group)
                new_last_moves += self._last_move

        self._last_move = new_last_moves

    def _undo_pusher_step(self, pusher_step: PusherStep):
        options = MoveWorkerOptions()
        if self._solving_mode == SolvingMode.FORWARD:
            has_box_behind_pusher = self.board_manager.has_box_on(
                self._manager.board.neighbor(
                    self.board_manager.pusher_position(self.selected_pusher),
                    pusher_step.direction,
                )
            )

            if not pusher_step.is_move and not has_box_behind_pusher:
                raise IllegalMoveError("Requested push undo, but no box behind pusher!")
            options.force_pulls = not pusher_step.is_move
            options.increase_pull_count = False
            self._pull_or_move(pusher_step.direction.opposite, options)
        else:
            options.decrease_pull_count = True
            self._push_or_move(pusher_step.direction.opposite, options)

    def _undo_jump(self, jump_moves: Iterable[PusherStep]):
        path = [pusher_step.direction.opposite for pusher_step in jump_moves]
        old_position = self._manager.pusher_position(self._selected_pusher)
        new_position = self._manager.board.path_destination(old_position, path)
        self.jump(new_position)

    def _undo_pusher_selection(self, selection_moves: Iterable[PusherStep]):
        path = [pusher_step.direction.opposite for pusher_step in selection_moves]
        old_position = self._manager.pusher_position(self._selected_pusher)
        new_position = self._manager.board.path_destination(old_position, path)
        self.select_pusher(self._manager.pusher_id_on(new_position))

    def _push_or_move(self, direction: Direction, options: MoveWorkerOptions):
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

        pusher_step = PusherStep(direction, is_push)
        pusher_step.pusher_id = self._selected_pusher
        if is_push:
            pusher_step.moved_box_id = self._manager.box_id_on(in_front_of_box)
            if options.decrease_pull_count and self._pull_count > 0:
                self._pull_count -= 1
        self._last_move = [pusher_step]

    def _pull_or_move(self, direction: Direction, options: MoveWorkerOptions):
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

        pusher_step = PusherStep(direction, is_pull)
        pusher_step.pusher_id = self._selected_pusher
        if is_pull:
            pusher_step.moved_box_id = self._manager.box_id_on(initial_pusher_position)
        self._last_move = [pusher_step]
