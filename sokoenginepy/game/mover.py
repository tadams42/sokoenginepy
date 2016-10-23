from copy import deepcopy
from itertools import groupby

from ..board import HashedBoardState
from ..common import DEFAULT_PIECE_ID, GameSolvingMode, SokoengineError
from ..snapshot import AtomicMove


class NonPlayableBoardError(SokoengineError):
    def __init__(self):
        super().__init__("Board is not playable!")


class IllegalMoveError(SokoengineError):
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
        always pulls boxes but can be changed through Mover flag

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
        solving_mode (GameSolvingMode): start the game in this solving mode

    Warning:
        :class:`.Mover` operates directly on referenced game board. Because of
        that, this board should not be edited outside of :class:`.Mover`
        interface once :class:`.Mover` instance had been attached to it: editing
        the board will corrupt :class:`.Mover` internal state. For the same
        reason, it is not allowed to attach two movers to same game board.
    """

    def __init__(self, board, solving_mode=GameSolvingMode.FORWARD):
        self._board = board
        self._initial_board = deepcopy(board)
        self._state = HashedBoardState(self._board)
        self._solving_mode = solving_mode
        self._pulls_boxes = True
        self._selected_pusher = DEFAULT_PIECE_ID
        self._pull_count = 0
        self._last_performed_moves = []

        if not self._state.is_playable:
            raise NonPlayableBoardError

        if self.solving_mode == GameSolvingMode.REVERSE:
            self._switch_boxes_and_goals()

    @property
    def board(self):
        """Instance of :class:`.VariantBoard` subclasses."""
        return self._board

    @property
    def initial_board(self):
        """Saved ``board`` layout before any movement."""
        return self._initial_board

    @property
    def solving_mode(self):
        """In which solving mode is board being solved?"""
        return self._solving_mode

    @property
    def state(self):
        """Board state tracking through instance of :class:`.HashedBoardState`"""
        return self._state

    @property
    def selected_pusher(self):
        """ID of pusher that will perform next move.

        For single-pusher boards the only pusher is always selected so this
        doesn't need to be called.

        Default is :data:`.DEFAULT_PIECE_ID`
        """
        return self._selected_pusher

    @selected_pusher.setter
    def selected_pusher(self, pusher_id):
        if not self._state.has_pusher(pusher_id):
            raise KeyError('No such pusher: {0}', format(pusher_id))

        self._last_performed_moves = []

        if pusher_id != self.selected_pusher:
            old_pusher_position = self._state.pusher_position(self.selected_pusher)
            new_pusher_position = self._state.pusher_position(pusher_id)
            selection_path = self._board.position_path_to_direction_path(
                self._board.find_jump_path(
                    old_pusher_position, new_pusher_position
                )
            )['path']
            for direction in selection_path:
                atomic_move = AtomicMove(direction, False)
                atomic_move.is_pusher_selection = True
                self._last_performed_moves.append(atomic_move)

            self._selected_pusher = pusher_id

    @property
    def pulls_boxes(self):
        """In reverse solving mode it is optional to pull boxes.

        This flag selects pull behavior.
        """
        return self._pulls_boxes

    @pulls_boxes.setter
    def pulls_boxes(self, rv):
        self._pulls_boxes = rv

    @property
    def last_performed_moves(self):
        """Sequence of :class:`.AtomicMove` that describes most recent movemt

        Sequence contains one :class:`.AtomicMove` or (in case of jumps and
        pusher selections) a more than one :class:`.AtomicMove`-s

        This is useful for generating movement animation in GUI after calling
        undo/redo
        """
        return self._last_performed_moves

    def move(self, direction):
        """Moves currently selected pusher in ``direction``.

        In forward solving mode, pushes the box if it is there.

        In reverse solving mode pulls box together with pusher depending on
        self.pulls_boxes.

        Args:
            direction (Direction): direction of movement

        Raises:
            IllegalMoveError: for illegal moves
        """
        move_success = None
        options = MoveWorkerOptions()
        if self._solving_mode == GameSolvingMode.FORWARD:
            options.decrease_pull_count = False
            move_success = self._push_or_move(direction, options)
        else:
            options.force_pulls = self._pulls_boxes
            options.increase_pull_count = True
            move_success = self._pull_or_move(direction, options)

        if not move_success:
            raise IllegalMoveError("Can't move in {0}".format(direction))

        return True

    def jump(self, new_position):
        """Currently selected pusher jumps to ``new_position``.

        Fails if
            - :class:`Mover` is in forward solving mode
            - pusher can't be dropped on ``new_position``
            - first pull had been made

        Raises:
            IllegalMoveError: for illegal jumps
        """
        if self._pull_count != 0:
            raise IllegalMoveError('Jumps not allowed after first pull')

        if self.solving_mode != GameSolvingMode.REVERSE:
            raise IllegalMoveError('Jumps allowed only in reverse solving mode')

        self._last_performed_moves = []

        old_position = self._state.pusher_position(self.selected_pusher)
        if old_position == new_position:
            return True

        if self._board[new_position].can_put_pusher_or_box:
            self._board[old_position].remove_pusher()
            self._board[new_position].put_pusher()
            self._state.move_pusher_from(old_position, new_position)
            for direction in self._board.position_path_to_direction_path(
                self._board.find_jump_path(
                    old_position, new_position
                )
            )['path']:
                am = AtomicMove(direction, False)
                am.is_jump = True
                am.pusher_id = self.selected_pusher
                self._last_performed_moves.append(am)
            return True

        raise IllegalMoveError("Can't jump onto wall, box or pusher!")

    def undo(self):
        """Undoes most recent movement."""

        if len(self._last_performed_moves) == 1:
            options = MoveWorkerOptions()
            if self.solving_mode == GameSolvingMode.FORWARD:
                options.force_pulls = True
                options.increase_pull_count = False
                return self._pull_or_move(
                    self._last_performed_moves[0].direction.opposite, options
                )
            else:
                options.decrease_pull_count = True
                return self._push_or_move(
                    self._last_performed_moves[0].direction.opposite, options
                )
        elif len(self._last_performed_moves) > 1:
            path = [
                am.direction.opposite
                for am in reversed(self._last_performed_moves)
            ]
            old_position = self._state.pusher_position(self.selected_pusher)
            new_position = self._board.path_destination(old_position, path)
            if self._last_performed_moves[0].is_jump:
                return self.jump(new_position)
            else:
                self.selected_pusher = self._state.pusher_id_on(new_position)
                return True

    def _undo(self, moves):
        """Treats ``moves`` as performed moves and tries to undo them.

        Returns undo sequence of moves.

        Stops after  all moves from ``moves`` are undone of illegal move is
        encountered.
        """
        retv = []

        def kf(elem):
            if elem.is_jump:
                return 0
            if elem.is_pusher_selection:
                return 1
            return 2

        for undo_move in [list(g) for k, g in groupby(moves, kf)]:
            self._last_performed_moves = undo_move
            move_success = self.undo()

            if move_success:
                for undone_atomic_move in self.last_performed_moves:
                    retv.append(deepcopy(undone_atomic_move))

        return retv

    def _switch_boxes_and_goals(self):
        switch = self._state.switch_boxes_and_goals()

        if switch:
            for pos in switch['pusher_to_remove']:
                self.board[pos].remove_pusher()

            for pos in switch['switches']:
                self.board[pos].switch_box_and_goal()

            for pos in switch['pushers_to_place']:
                self.board[pos].put_pusher()

    def _push_or_move(self, direction, options):
        """Perform movement of currently selected pusher in ``direction``.

        In case there is a box in front of pusher, pushes it.

        Returns:
            bool: True if both, pusher and box, moved successfully.

        Note:
            Method guarantees strong exception safety.
        """
        self._last_performed_moves = []

        is_push = None
        box_moved_ok = None
        pusher_moved_ok = None
        in_front_of_box = None

        initial_pusher_position = self._state.pusher_position(self.selected_pusher)
        in_front_of_pusher = self._board.neighbor(initial_pusher_position, direction)

        if in_front_of_pusher:
            if self._state.has_box_on(in_front_of_pusher):
                is_push = True
                in_front_of_box = self._board.neighbor(in_front_of_pusher, direction)
                if in_front_of_box:
                    if self._board[in_front_of_box].can_put_pusher_or_box:
                        self._state.move_box_from(in_front_of_pusher, in_front_of_box)
                        self._board[in_front_of_pusher].remove_box()
                        self._board[in_front_of_box].put_box()
                        box_moved_ok = True
                    else:
                        box_moved_ok = False
                else:
                    box_moved_ok = False
            else:
                is_push = False

            if not is_push or (is_push and box_moved_ok):
                if self._board[in_front_of_pusher].can_put_pusher_or_box:
                    self._state.move_pusher_from(initial_pusher_position, in_front_of_pusher)
                    self._board[initial_pusher_position].remove_pusher()
                    self._board[in_front_of_pusher].put_pusher()
                    pusher_moved_ok = True
                else:
                    pusher_moved_ok = False
            else:
                pusher_moved_ok = False
        else:
            pusher_moved_ok = False

        if pusher_moved_ok and (not is_push or (is_push and box_moved_ok)):
            atomic_move = AtomicMove(direction, is_push)
            atomic_move.pusher_id = self.selected_pusher
            if is_push:
                atomic_move.moved_box_id = self._state.box_id_on(in_front_of_box)
                if options.decrease_pull_count and self._pull_count > 0:
                    self._pull_count -= 1
            self._last_performed_moves = [atomic_move]
            return True
        else:
            return False

    def _pull_or_move(self, direction, options):
        """Perform movement of currently selected pusher in ``direction``.

        In case there is a box in behind of pusher, might pull it.

        Returns:
            bool: True if both, pusher and box, moved successfully.

        Note:
            Method guarantees strong exception safety.
        """
        self._last_performed_moves = []

        pusher_moved_ok = None
        initial_pusher_position = self._state.pusher_position(self.selected_pusher)
        in_front_of_pusher = self._board.neighbor(initial_pusher_position, direction)

        if in_front_of_pusher:
            if self._board[in_front_of_pusher].can_put_pusher_or_box:
                self._state.move_pusher_from(initial_pusher_position, in_front_of_pusher)
                self._board[initial_pusher_position].remove_pusher()
                self._board[in_front_of_pusher].put_pusher()
                pusher_moved_ok = True
            else:
                pusher_moved_ok = False
        else:
            pusher_moved_ok = False

        if not pusher_moved_ok:
            return False

        is_pull = False
        box_moved_ok = None

        if options.force_pulls:
            behind_pusher = self._board.neighbor(initial_pusher_position, direction.opposite)
            if behind_pusher and self._board[behind_pusher].has_box:
                is_pull = True
                self._state.move_box_from(behind_pusher, initial_pusher_position)
                self._board[behind_pusher].remove_box()
                self._board[initial_pusher_position].put_box()
                if options.increase_pull_count:
                    self._pull_count += 1
                box_moved_ok = True

        if pusher_moved_ok and (not is_pull or (is_pull and box_moved_ok)):
            atomic_move = AtomicMove(direction, is_pull)
            atomic_move.pusher_id = self.selected_pusher
            if is_pull:
                atomic_move.moved_box_id = self._state.box_id_on(initial_pusher_position)
            self._last_performed_moves = [atomic_move]
            return True
        else:
            return False
