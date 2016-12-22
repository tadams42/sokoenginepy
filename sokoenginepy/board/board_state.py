from copy import deepcopy
from functools import partial
from itertools import permutations
from textwrap import dedent, indent

from cached_property import cached_property
from midict import MIDict, ValueExistsError

from .. import utilities
from .piece import DEFAULT_PIECE_ID
from .sokoban_plus import SokobanPlus


class CellAlreadyOccupiedError(utilities.SokoengineError):
    pass


class BoardState:
    """Memoizes, tracks and updates positions of all pieces.

    - Provides efficient means to inspect positions of pushers, boxes and goals.
      To understand how this works, we need to have a way of identifying
      individual pushers, boxes and goals. :class:`.BoardState` does that by
      assigning numerical ID to each individual piece. This ID can then be used
      to refer to that piece in various contexts.

      IDs are assigned by simply counting from top left corner of board,
      starting with :data:`.DEFAULT_PIECE_ID`

      .. image:: /images/assigning_ids.png
          :alt: Assigning board elements' IDs

    - Provides efficient means of pieces movemet. Ie. we can move pushers and
      boxes and :class:`BoardState` will update internal state and board cells.

      This movement preserves piece IDs in contex of board state changes. To
      ilustrate, let's assume we create :class:`.BoardState` from board with two
      pushers one abowe the other. After then we edit the board, placing pusher
      ID 2 in row abowe pusher ID 1. Finally, we create another instance of
      :class:`.BoardState`. If we now inspect pusher IDs in first and second
      :class:`.BoardState` instance, they will be different. Have we used
      movement methods instead of board editing, these IDs would be preserved:

      +----------------------------------------------+----------------------------------------------+----------------------------------------------+
      | 1) Initial board                             | 2) Edited board                              | 3) Box moved                                 |
      +----------------------------------------------+----------------------------------------------+----------------------------------------------+
      | .. image:: /images/movement_vs_transfer1.png | .. image:: /images/movement_vs_transfer2.png | .. image:: /images/movement_vs_transfer3.png |
      +----------------------------------------------+----------------------------------------------+----------------------------------------------+

    Note:
        Movement methods here are just for state and board cell updates, they
        don't implement full game logic. For game logic see :class:`.Mover`

    Warning:
        Once we create instance of :class:`BoardState` from some
        :class:`VariantBoard` instance, that board should not be edited.
        :class:`BoardState` will updated cells on board when pieces are moved,
        and editing board cells directly (ie. adding/removing pushers or boxes,
        changing board size, changing walls layout, etc...) will not sync these
        edits back to our :class:`BoardState` instance.

    Args:
        variant_board (VariantBoard): board for which we want to manage state
    """

    # Following two are needed because accessing .keys('name') in MIDict
    # doesn't seem to always work
    _INDEX_ID = 0
    _INDEX_POS = 1

    def __init__(self, variant_board):
        self._variant_board = variant_board
        self._boxes = MIDict([], ['id', 'position'])
        self._goals = MIDict([], ['id', 'position'])
        self._pushers = MIDict([], ['id', 'position'])

        pusher_id = box_id = goal_id = DEFAULT_PIECE_ID

        for position in range(0, variant_board.size):
            cell = variant_board[position]

            if cell.has_pusher:
                self._pushers[self._INDEX_ID:pusher_id] = position
                pusher_id += 1

            if cell.has_box:
                self._boxes[self._INDEX_ID:box_id] = position
                box_id += 1

            if cell.has_goal:
                self._goals[self._INDEX_ID:goal_id] = position
                goal_id += 1

        self._sokoban_plus = SokobanPlus(
            pieces_count=len(self._boxes), boxorder='', goalorder=''
        )

    def __str__(self):
        return "<{klass} pushers={pushers},".format(
            klass=self.__class__.__name__,
            pushers=self.pushers_positions,
        ) + indent(dedent(
            """
            boxes={boxes},
            goals={goals},
            boxorder='{boxorder}',
            goalorder='{goalorder}',
            variant='{variant}',
            variant_board=
            """.format(
                boxes=self.boxes_positions,
                goals=self.goals_positions,
                boxorder=str(self.boxorder),
                goalorder=str(self.goalorder),
                variant=str(self._variant_board.variant)
            )), (len(self.__class__.__name__) + 2) * ' '
        ) + str(self._variant_board) + '>'

    def __repr__(self):
        return "{klass}({board_klass}(board_str='\\n'.join([\n".format(
            klass=self.__class__.__name__,
            board_klass=self._variant_board.__class__.__name__
        ) + indent(',\n'.join([
            '"{0}"'.format(l) for l in str(self._variant_board).split('\n')
        ]), '    ') + "\n])))"

    @cached_property
    def board_size(self):
        return self._variant_board.size

    @cached_property
    def board(self):
        return self._variant_board

    # --------------------------------------------------------------------------
    # Pushers
    # --------------------------------------------------------------------------

    @cached_property
    def pushers_count(self):
        return len(self._pushers)

    @cached_property
    def pushers_ids(self):
        """IDs of all pushers on board.

        Returns:
            list: integer IDs of all pushers on board
        """
        return list(self._pushers.keys(self._INDEX_ID))

    @property
    def pushers_positions(self):
        """Positions of all pushers on board.

        Returns:
            dict: mapping pushers' IDs to the corresponding board positions::

                {1: 42, 2: 24}
        """
        return dict(
            (pid, self._pushers[self._INDEX_ID:pid])
            for pid in self._pushers.keys(self._INDEX_ID)
        )

    def pusher_position(self, pid):
        """
        Args:
            pid (int): pusher ID

        Returns:
            int: pusher position

        Raises:
            :exc:`KeyError`: No pusher with ID ``pid``
        """
        try:
            return self._pushers[self._INDEX_ID:pid]
        except KeyError:
            raise KeyError("No pusher with ID: {0}".format(pid))

    def pusher_id_on(self, position):
        """ID of pusher on position.

        Args:
            position (int): position to check

        Returns:
            int: pusher ID

        Raises:
            :exc:`KeyError`: No pusher on ``position``
        """
        try:
            return self._pushers[self._INDEX_POS:position]
        except KeyError:
            raise KeyError("No pusher on position: {0}".format(position))

    def has_pusher(self, pid):
        """
        Args:
            pid (int): pusher ID
        """
        # TODO Buggy MIDict forces us to convert to list here
        return pid in list(self._pushers.keys(self._INDEX_ID))

    def has_pusher_on(self, position):
        """
        Args:
            position (int): position to check
        """
        return position in self._pushers.keys(self._INDEX_POS)

    def move_pusher_from(self, old_position, to_new_position):
        """Updates board state and board cells with changed pusher position.

        Args:
            old_position (int): starting position
            to_new_position (int): ending position

        Raises:
            :exc:`KeyError`: there is no pusher on ``old_position``
            :exc:`.CellAlreadyOccupiedError`: there is an obstacle (
                wall/box/antoher pusher) on ``to_new_position``
        """
        if old_position == to_new_position:
            return

        dest_cell = self._variant_board[to_new_position]
        if not dest_cell.can_put_pusher_or_box:
            raise CellAlreadyOccupiedError(
                "Pusher can't be placed in position " +
                "{0} occupied by '{1}'".format(to_new_position, dest_cell)
            )

        try:
            self._pushers[
                self._INDEX_ID:self.pusher_id_on(old_position)
            ] = to_new_position
        except ValueExistsError:
            raise CellAlreadyOccupiedError(
                "Pusher can't be placed onto pusher in position: {0}".format(
                    to_new_position
                )
            )

        self._variant_board[old_position].remove_pusher()
        dest_cell.put_pusher()

    def move_pusher(self, pusher_id, to_new_position):
        """Updates board state and board cells with changed pusher position.

        Args:
            pusher_id (int): pusher ID
            to_new_position (int): ending position

        Raises:
            :exc:`KeyError`: there is no pusher with ID ``pid``
            :exc:`.CellAlreadyOccupiedError`: there is a pusher already on
                ``to_new_position``

        Note:
            Allows placing a pusher onto position occupied by box. This is for
            cases when we switch box/goals positions in reverse solving mode.
            In this situation it is legal for pusher to end up standing on top
            of the box. Game rules say that for these situations, first move(s)
            must be jumps.

        Warning:
            It doesn't verify if ``to_new_position`` is valid on-board position.
        """
        self.move_pusher_from(self.pusher_position(pusher_id), to_new_position)

    # --------------------------------------------------------------------------
    # Boxes
    # --------------------------------------------------------------------------

    @cached_property
    def boxes_count(self):
        return len(self._boxes)

    @cached_property
    def boxes_ids(self):
        """IDs of all boxes on board.

        Returns:
            list: integer IDs of all boxes on board
        """
        return list(self._boxes.keys(self._INDEX_ID))

    @property
    def boxes_positions(self):
        """Positions of all boxes on board.

        Returns:
            dict: mapping boxes' IDs to the corresponding board positions::

                {1: 42, 2: 24}
        """
        return dict(
            (pid, self._boxes[self._INDEX_ID:pid])
            for pid in self._boxes.keys(self._INDEX_ID)
        )

    def box_position(self, pid):
        """
        Args:
            pid (int): box ID

        Returns:
            int: box position

        Raises:
            KeyError: No box with ID ``pid``
        """
        try:
            return self._boxes[self._INDEX_ID:pid]
        except KeyError:
            raise KeyError("No box with ID: {0}".format(pid))

    def box_id_on(self, position):
        """ID of box on position.

        Args:
            position (int): position to check

        Returns:
            int: box ID

        Raises:
            KeyError: No box on ``position``
        """
        try:
            return self._boxes[self._INDEX_POS:position]
        except KeyError:
            raise KeyError("No box on position: {0}".format(position))

    def has_box(self, pid):
        """
        Args:
            pid (int): box ID
        """
        # TODO Buggy MIDict forces us to convert to list here
        return pid in list(self._boxes.keys(self._INDEX_ID))

    def has_box_on(self, position):
        """
        Args:
            position (int): position to check
        """
        return position in self._boxes.keys(self._INDEX_POS)

    def move_box_from(self, old_position, to_new_position):
        """Updates board state with changed box position.

        Args:
            old_position (int): starting position
            to_new_position (int): ending position

        Raises:
            :exc:`KeyError`: there is no box on ``old_position``
            :exc:`.CellAlreadyOccupiedError`: there is a box already on
                ``to_new_position``

        Note:
            Allows placing of a box onto position occupied by pusher. This is
            for cases when we switch box/goals positions in reverse solving
            mode. In this situation it is legal for pusher to end up standing
            on top of the box. Game rules say that for these situations, first
            move(s) must be jumps

        Warning:
            It doesn't verify if ``old_position`` or ``to_new_position`` are
            valid on-board positions.
        """
        if old_position == to_new_position:
            return

        dest_cell = self._variant_board[to_new_position]
        if not dest_cell.can_put_pusher_or_box:
            raise CellAlreadyOccupiedError(
                "Box can't be placed on position " +
                "{0} occupied by '{1}'".format(to_new_position, dest_cell)
            )

        try:
            self._boxes[
                self._INDEX_ID:self.box_id_on(old_position)
            ] = to_new_position
        except ValueExistsError:
            raise CellAlreadyOccupiedError(
                "Box can't be placed onto box in position: {0}".format(
                    to_new_position
                )
            )

        self._variant_board[old_position].remove_box()
        dest_cell.put_box()

    def move_box(self, box_id, to_new_position):
        """Updates board state with changed box position.

        Args:
            box_id (int): box ID
            to_new_position (int): ending position

        Raises:
            :exc:`KeyError`: there is no box with ID ``box_id``
            :exc:`.CellAlreadyOccupiedError`: there is a box already on
                ``to_new_position``

        Note:
            Allows placing of a box onto position occupied by pusher. This is
            for cases when we switch box/goals positions in reverse solving
            mode. In this situation it is legal for pusher to end up standing
            on top of the box. Game rules say that for these situations, first
            move(s) must be jumps

        Warning:
            It doesn't verify if ``to_new_position`` is valid on-board position.
        """
        self.move_box_from(self.box_position(box_id), to_new_position)

    # --------------------------------------------------------------------------
    # Goals
    # --------------------------------------------------------------------------

    @cached_property
    def goals_count(self):
        return len(self._goals)

    @cached_property
    def goals_ids(self):
        """IDs of all goals on board.

        Returns:
            list: integer IDs of all goals on board
        """
        return list(self._goals.keys(self._INDEX_ID))

    @property
    def goals_positions(self):
        """Positions of all goals on board.

        Returns:
            dict: mapping goals' IDs to the corresponding board positions::

                {1: 42, 2: 24}
        """
        return dict(
            (pid, self._goals[self._INDEX_ID:pid])
            for pid in self._goals.keys(self._INDEX_ID)
        )

    def goal_position(self, pid):
        """
        Args:
            pid (int): goal ID

        Returns:
            int: goal position

        Raises:
            :exc:`KeyError`: No goal with ID ``pid``
        """
        try:
            return self._goals[self._INDEX_ID:pid]
        except KeyError:
            raise KeyError("No goal with ID: {0}".format(pid))

    def goal_id_on(self, position):
        """ID of goal on position.

        Args:
            position (int): position to check

        Returns:
            int: goal ID

        Raises:
            :exc:`KeyError`: No goal on ``position``
        """
        try:
            return self._goals[self._INDEX_POS:position]
        except KeyError:
            raise KeyError("No goal on position: {0}".format(position))

    def has_goal(self, pid):
        """
        Args:
            pid (int): goal ID
        """
        # TODO Buggy MIDict forces us to convert to list here
        return pid in list(self._goals.keys(self._INDEX_ID))

    def has_goal_on(self, position):
        """
        Args:
            position (int): position to check
        """
        return position in self._goals.keys(self._INDEX_POS)

    # --------------------------------------------------------------------------
    # Sokoban+
    # --------------------------------------------------------------------------

    def box_plus_id(self, pid):
        """
        See Also:
            :meth:`.SokobanPlus.box_plus_id`
        """
        return self._sokoban_plus.box_plus_id(pid)

    def goal_plus_id(self, pid):
        """
        See Also:
            :meth:`.SokobanPlus.goal_plus_id`
        """
        return self._sokoban_plus.goal_plus_id(pid)

    @property
    def boxorder(self):
        """
        See Also:
            :attr:`.SokobanPlus.boxorder`
        """
        return self._sokoban_plus.boxorder

    @boxorder.setter
    def boxorder(self, rv):
        self._sokoban_plus.boxorder = rv

    @property
    def goalorder(self):
        """
        See Also:
            :attr:`.SokobanPlus.goalorder`
        """
        return self._sokoban_plus.goalorder

    @goalorder.setter
    def goalorder(self, rv):
        self._sokoban_plus.goalorder = rv

    @property
    def is_sokoban_plus_enabled(self):
        return self._sokoban_plus.is_enabled

    @is_sokoban_plus_enabled.setter
    def is_sokoban_plus_enabled(self, rv):
        self._sokoban_plus.is_enabled = rv

    @property
    def is_sokoban_plus_valid(self):
        return self._sokoban_plus.is_valid

    # --------------------------------------------------------------------------
    # Other
    # --------------------------------------------------------------------------

    def solutions(self):
        """
        Generator for all configurations of boxes that result in solved board.

        Yields:
            dict: {box_id1: box_position1, box_id2: box_position2, ...}

        Note:
            Resultset depends on :attr:`.BoardState.is_sokoban_plus_enabled`.
        """
        if self.boxes_count != self.goals_count:
            return []

        def is_valid_solution(boxes_positions):
            retv = True
            for index, box_position in enumerate(boxes_positions):
                box_id = index + DEFAULT_PIECE_ID
                box_plus_id = self.box_plus_id(box_id)
                goal_id = self.goal_id_on(box_position)
                goal_plus_id = self.goal_plus_id(goal_id)

                retv = retv and (box_plus_id == goal_plus_id)
                if not retv:
                    break
            return retv

        for boxes_positions in permutations(self.goals_positions.values()):
            if is_valid_solution(boxes_positions):
                yield dict(
                    (index + DEFAULT_PIECE_ID, box_position)
                    for index, box_position in enumerate(boxes_positions)
                )

    def _box_goal_pairs(self):
        """Finds a list of paired (box_id, goal_id,) tuples.

        If Sokoban+ is enabled, boxes and goals are paired by Sokoban+ IDs,
        otherwise they are paired by regular IDs

        Yields:
            tuple: (box_id, goal_id)
        """
        if self.boxes_count != self.goals_count:
            return []

        def is_box_goal_pair(box, goal_id):
            if self.is_sokoban_plus_enabled:
                return (
                    self.box_plus_id(box[1]) == self.goal_plus_id(goal_id)
                )
            return box[1] == goal_id

        boxes_todo = deepcopy(self.boxes_ids)
        goals_ids = deepcopy(self.goals_ids)
        for goal_id in goals_ids:
            predicate = partial(is_box_goal_pair, goal_id=goal_id)
            index, box_id = next(filter(predicate, enumerate(boxes_todo)), None)
            yield (box_id, goal_id,)
            del(boxes_todo[index])

    def switch_boxes_and_goals(self):
        """Switches positions of boxes and goals pairs."""
        if self.boxes_count != self.goals_count:
            raise utilities.SokoengineError(
                "Unable to switch boxes and goals - counts are not the same"
            )

        for box_id, goal_id in self._box_goal_pairs():
            old_box_position = self.box_position(box_id)
            old_goal_position = self.goal_position(goal_id)

            if old_box_position != old_goal_position:
                self._goals[self._INDEX_ID:goal_id] = old_box_position
                self._variant_board[old_goal_position].remove_goal()

                old_pusher_position = None
                if self.has_pusher_on(old_goal_position):
                    # If there is a pusher on goal, we have to remove it before
                    # we put a box there
                    old_pusher_position = old_goal_position
                    self._variant_board[old_goal_position].remove_pusher()

                self.move_box_from(old_box_position, old_goal_position)
                self._variant_board[old_box_position].put_goal()

                if old_pusher_position:
                    # There was pusher on former goal cell - we now put it on
                    # new goal cell avoiding situation where pusher would end up
                    # standing on top of the box - net result is that box and
                    # goal switched places and pusher moved to new goal
                    # position.
                    # Note that move_pusher_from doesn't mind if there is no
                    # pusher on src board cell, but would mind if there was no
                    # pusher in self._pushers. Also, we couldn't just edit
                    # self._pushers - we need to actually perform movement
                    # because subclasses might count on it.
                    self.move_pusher_from(old_pusher_position, old_box_position)

    @property
    def is_playable(self):
        return (
            self.pushers_count > 0 and
            self.boxes_count == self.goals_count and
            self.boxes_count > 0 and
            self.goals_count > 0
        )
