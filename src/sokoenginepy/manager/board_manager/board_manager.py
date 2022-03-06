from functools import cached_property, partial
from itertools import permutations

from ... import utilities
from ..board_state import BoardState
from ..piece import DEFAULT_PIECE_ID
from ..sokoban_plus import SokobanPlus


class CellAlreadyOccupiedError(RuntimeError):
    pass


class BoxGoalSwitchError(RuntimeError):
    pass


class BoardManager:
    """Memoizes, tracks and updates positions of all pieces.

    - Provides efficient means to inspect positions of pushers, boxes and goals. To
      understand how this works, we need to have a way of identifying individual
      pushers, boxes and goals. :class:`.BoardManager` does that by assigning
      numerical ID to each individual piece. This ID can then be used to refer to
      that piece in various contexts.

      IDs are assigned by simply counting from top left corner of board, starting
      with :data:`.DEFAULT_PIECE_ID`

      .. image:: /images/assigning_ids.png
          :alt: Assigning board elements' IDs

    - Provides efficient means of pieces movemet. Ie. we can move pushers and boxes
      and :class:`.BoardManager` will update internal state and board cells.

      This movement preserves piece IDs in contex of board state changes. To
      ilustrate, let's assume we create :class:`.BoardManager` from board with two
      pushers one above the other. After then we edit the board, placing pusher ID 2
      in row above pusher ID 1. Finally, we create another instance of
      :class:`.BoardManager`. If we now inspect pusher IDs in first and second
      :class:`.BoardManager` instance, they will be different. Have we used movement
      methods instead of board editing, these IDs would be preserved:

      .. |img1| image:: /images/movement_vs_transfer1.png
      .. |img2| image:: /images/movement_vs_transfer2.png
      .. |img3| image:: /images/movement_vs_transfer3.png

      +------------------+------------------+------------------+
      | 1) Initial board | 2) Edited board  | 3) Box ID:1 moved|
      +------------------+------------------+------------------+
      |      |img1|      |      |img2|      |      |img3|      |
      +------------------+------------------+------------------+

    Note:
        Movement methods here are just for state and board cell updates, they don't
        implement full game logic. For game logic see :class:`.Mover`

    Warning:
        Once we create instance of :class:`.BoardManager` from some
        :class:`.VariantBoard` instance, that board should not be edited.
        :class:`.BoardManager` will update cells on board when pieces are moved, and
        editing board cells directly (ie. adding/removing pushers or boxes, changing
        board size, changing walls layout, etc...) will not sync these edits back to
        our :class:`.BoardManager` instance.

    Args:
        variant_board (VariantBoard): board for which we want to manage state
    """

    def __init__(self, variant_board, boxorder=None, goalorder=None):
        self._board = variant_board
        self._boxes = utilities.Flipdict()
        self._goals = utilities.Flipdict()
        self._pushers = utilities.Flipdict()
        self._walls = []

        pusher_id = box_id = goal_id = DEFAULT_PIECE_ID

        for position in range(0, variant_board.size):
            cell = variant_board[position]

            if cell.has_pusher:
                self._pushers[pusher_id] = position
                pusher_id += 1

            if cell.has_box:
                self._boxes[box_id] = position
                box_id += 1

            if cell.has_goal:
                self._goals[goal_id] = position
                goal_id += 1

            if cell.is_wall:
                self._walls.append(position)

        self._sokoban_plus = SokobanPlus(
            pieces_count=len(self._boxes), boxorder=boxorder, goalorder=goalorder
        )

    def __str__(self):
        prefix = (len(self.__class__.__name__) + 2) * " "
        return "\n".join(
            [
                "<{} pushers: {},".format(
                    self.__class__.__name__, self.pushers_positions
                ),
                prefix + "boxes: {},".format(self.boxes_positions),
                prefix + "goals: {},".format(self.goals_positions),
                prefix
                + "walls: {},".format(
                    self.walls_positions
                    if len(self.walls_positions) <= 10
                    else "[{}, ...]".format(
                        ", ".join(str(w) for w in self.walls_positions[:10])
                    )
                ),
                prefix + "boxorder: '{}',".format(self.boxorder or ""),
                prefix + "goalorder: '{}',".format(self.goalorder or ""),
                prefix + "board:\n" + str(self.board) + ">",
            ]
        )

    def __repr__(self):
        return "{}(variant_board={}, boxorder='{}', goalorder='{}')".format(
            self.__class__.__name__,
            repr(self.board),
            self.boxorder or "",
            self.goalorder or "",
        )

    @property
    def board(self):
        return self._board

    @property
    def walls_positions(self):
        return self._walls

    # --------------------------------------------------------------------------
    # Pushers
    # --------------------------------------------------------------------------

    @cached_property
    def pushers_count(self):
        return len(self._pushers)

    @cached_property
    def pushers_ids(self):
        """
        IDs of all pushers on board.

        Returns:
            list: integer IDs of all pushers on board
        """
        return list(self._pushers.keys())

    @property
    def pushers_positions(self):
        """
        Positions of all pushers on board.

        Returns:
            dict: mapping pushers' IDs to the corresponding board positions::

                {1: 42, 2: 24}
        """
        return dict(self._pushers)

    def pusher_position(self, pusher_id):
        """
        Args:
            pusher_id (int): pusher ID

        Returns:
            int: pusher position

        Raises:
            :exc:`KeyError`: No pusher with ID ``pusher_id``
        """
        try:
            return self._pushers[pusher_id]
        except KeyError:
            raise KeyError("No pusher with ID: {0}".format(pusher_id))

    def pusher_id_on(self, position):
        """
        ID of pusher on position.

        Args:
            position (int): position to check

        Returns:
            int: pusher ID

        Raises:
            :exc:`KeyError`: No pusher on ``position``
        """
        try:
            return self._pushers.flip[position]
        except KeyError:
            raise KeyError("No pusher on position: {0}".format(position))

    def has_pusher(self, pusher_id):
        """
        Args:
            pusher_id (int): pusher ID
        """
        return pusher_id in self._pushers

    def has_pusher_on(self, position):
        """
        Args:
            position (int): position to check
        """
        return position in self._pushers.flip

    def _pusher_moved(self, old_position, to_new_position):
        """Subclass hook used to notify it that we modified pusher position."""
        pass

    def move_pusher_from(self, old_position, to_new_position):
        """
        Updates board state and board cells with changed pusher position.

        Args:
            old_position (int): starting position
            to_new_position (int): ending position

        Raises:
            :exc:`KeyError`: there is no pusher on ``old_position``
            :exc:`.CellAlreadyOccupiedError`: there is an obstacle (
                wall/box/another pusher) on ``to_new_position``
        """
        if old_position == to_new_position:
            return

        dest_cell = self._board[to_new_position]
        if not dest_cell.can_put_pusher_or_box:
            raise CellAlreadyOccupiedError(
                "Pusher ID: {0} ".format(self.pusher_id_on(old_position))
                + "can't be placed in position {0} occupied by '{1}'".format(
                    to_new_position, dest_cell
                )
            )

        self._pushers[self._pushers.flip[old_position]] = to_new_position
        self._board[old_position].remove_pusher()
        dest_cell.put_pusher()

        self._pusher_moved(old_position, to_new_position)

    def move_pusher(self, pusher_id, to_new_position):
        """
        Updates board state and board cells with changed pusher position.

        Args:
            pusher_id (int): pusher ID
            to_new_position (int): ending position

        Raises:
            :exc:`KeyError`: there is no pusher with ID ``pusher_id``
            :exc:`.CellAlreadyOccupiedError`: there is a pusher already on
                ``to_new_position``

        Note:
            Allows placing a pusher onto position occupied by box. This is for cases
            when we switch box/goals positions in reverse solving mode. In this
            situation it is legal for pusher to end up standing on top of the box.
            Game rules say that for these situations, first move(s) must be jumps.

        Warning:
            It doesn't verify if ``to_new_position`` is valid on-board position.
        """
        self.move_pusher_from(self._pushers[pusher_id], to_new_position)

    # --------------------------------------------------------------------------
    # Boxes
    # --------------------------------------------------------------------------

    @cached_property
    def boxes_count(self):
        return len(self._boxes)

    @cached_property
    def boxes_ids(self):
        """
        IDs of all boxes on board.

        Returns:
            list: integer IDs of all boxes on board
        """
        return list(self._boxes.keys())

    @property
    def boxes_positions(self):
        """
        Positions of all boxes on board.

        Returns:
            dict: mapping boxes' IDs to the corresponding board positions::

                {1: 42, 2: 24}
        """
        return dict(self._boxes)

    def box_position(self, box_id):
        """
        Args:
            box_id (int): box ID

        Returns:
            int: box position

        Raises:
            :exc:`KeyError`: No box with ID ``box_id``
        """
        try:
            return self._boxes[box_id]
        except KeyError:
            raise KeyError("No box with ID: {0}".format(box_id))

    def box_id_on(self, position):
        """
        ID of box on position.

        Args:
            position (int): position to check

        Returns:
            int: box ID

        Raises:
            :exc:`KeyError`: No box on ``position``
        """
        try:
            return self._boxes.flip[position]
        except KeyError:
            raise KeyError("No box on position: {0}".format(position))

    def has_box(self, box_id):
        """
        Args:
            box_id (int): box ID
        """
        return box_id in self._boxes

    def has_box_on(self, position):
        """
        Args:
            position (int): position to check
        """
        return position in self._boxes.flip

    def _box_moved(self, old_position, to_new_position):
        """Subclass hook used to notify it that we modified box position."""
        pass

    def move_box_from(self, old_position, to_new_position):
        """
        Updates board state and board cells with changed box position.

        Args:
            old_position (int): starting position
            to_new_position (int): ending position

        Raises:
            :exc:`KeyError`: there is no box on ``old_position``
            :exc:`.CellAlreadyOccupiedError`: there is an obstacle ( wall/box/pusher)
                on ``to_new_position``
        """
        if old_position == to_new_position:
            return

        dest_cell = self._board[to_new_position]
        if not dest_cell.can_put_pusher_or_box:
            raise CellAlreadyOccupiedError(
                "Box ID: {0} ".format(self.box_id_on(old_position))
                + "can't be placed in position {0} occupied by '{1}'".format(
                    to_new_position, dest_cell
                )
            )

        self._boxes[self._boxes.flip[old_position]] = to_new_position
        self._board[old_position].remove_box()
        dest_cell.put_box()

        self._box_moved(old_position, to_new_position)

    def move_box(self, box_id, to_new_position):
        """
        Updates board state and board cells with changed box position.

        Args:
            old_position (int): starting position
            to_new_position (int): ending position

        Raises:
            :exc:`KeyError`: there is no box on ``old_position``
            :exc:`.CellAlreadyOccupiedError`: there is an obstacle ( wall/box/another
                pusher) on ``to_new_position``
        """
        self.move_box_from(self._boxes[box_id], to_new_position)

    # --------------------------------------------------------------------------
    # Goals
    # --------------------------------------------------------------------------

    @cached_property
    def goals_count(self):
        return len(self._goals)

    @cached_property
    def goals_ids(self):
        """
        IDs of all goals on board.

        Returns:
            list: integer IDs of all goals on board
        """
        return list(self._goals.keys())

    @property
    def goals_positions(self):
        """
        Positions of all goals on board.

        Returns:
            dict: mapping goals' IDs to the corresponding board positions::

                {1: 42, 2: 24}
        """
        return dict(self._goals)

    def goal_position(self, goal_id):
        """
        Args:
            goal_id (int): goal ID

        Returns:
            int: goal position

        Raises:
            :exc:`KeyError`: No goal with ID ``goal_id``
        """
        try:
            return self._goals[goal_id]
        except KeyError:
            raise KeyError("No goal with ID: {0}".format(goal_id))

    def goal_id_on(self, position):
        """
        ID of goal on position.

        Args:
            position (int): position to check

        Returns:
            int: goal ID

        Raises:
            :exc:`KeyError`: No goal on ``position``
        """
        try:
            return self._goals.flip[position]
        except KeyError:
            raise KeyError("No goal on position: {0}".format(position))

    def has_goal(self, goal_id):
        """
        Args:
            goal_id (int): goal ID
        """
        return goal_id in self._goals

    def has_goal_on(self, position):
        """
        Args:
            position (int): position to check
        """
        return position in self._goals.flip

    # --------------------------------------------------------------------------
    # Sokoban+
    # --------------------------------------------------------------------------

    def box_plus_id(self, box_id):
        """
        See Also:
            :meth:`.SokobanPlus.box_plus_id`
        """
        return self._sokoban_plus.box_plus_id(box_id)

    def goal_plus_id(self, goal_id):
        """
        See Also:
            :meth:`.SokobanPlus.goal_plus_id`
        """
        return self._sokoban_plus.goal_plus_id(goal_id)

    @property
    def boxorder(self):
        """
        See Also:
            `.SokobanPlus.boxorder`
        """
        return self._sokoban_plus.boxorder

    @boxorder.setter
    def boxorder(self, rv):
        self._sokoban_plus.boxorder = rv

    @property
    def goalorder(self):
        """
        See Also:
            `.SokobanPlus.goalorder`
        """
        return self._sokoban_plus.goalorder

    @goalorder.setter
    def goalorder(self, rv):
        self._sokoban_plus.goalorder = rv

    @property
    def is_sokoban_plus_enabled(self):
        return self._sokoban_plus.is_enabled

    def enable_sokoban_plus(self):
        """
        Enables using Sokoban+ rules for this board.

        Enabling these, changes victory condition for given board.

        See Also:
            :class:`.SokobanPlus`
        """
        self._sokoban_plus.is_enabled = True

    def disable_sokoban_plus(self):
        """
        Disables using Sokoban+ rules for this board.

        See Also:
            :class:`.SokobanPlus`
        """
        self._sokoban_plus.is_enabled = False

    @property
    def is_sokoban_plus_valid(self):
        """
        Validates current set of Sokoban+ rules.

        See Also:
            :class:`.SokobanPlus`
        """
        return self._sokoban_plus.is_valid

    # --------------------------------------------------------------------------
    # Other
    # --------------------------------------------------------------------------

    @property
    def is_solved(self):
        if self.boxes_count != self.goals_count:
            return False

        retv = True
        for box_id, box_position in self._boxes.items():
            retv = (
                retv
                and self.has_goal_on(box_position)
                and (
                    self.box_plus_id(box_id)
                    == self.goal_plus_id(self.goal_id_on(box_position))
                )
            )

            if not retv:
                break

        return retv

    def solutions(self):
        """
        Generator for all configurations of boxes that result in solved board.

        Note:
            Resultset depends on `.BoardManager.is_sokoban_plus_enabled`.

        Yields:
            `.BoardState`
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

        for boxes_positions in permutations(self._goals.values()):
            if is_valid_solution(boxes_positions):
                yield BoardState(
                    boxes_positions=list(boxes_positions), pushers_positions=[]
                )

    def _box_goal_pairs(self):
        """
        Finds a list of paired (box_id, goal_id,) tuples.

        If Sokoban+ is enabled, boxes and goals are paired by Sokoban+ IDs, otherwise
        they are paired by regular IDs

        Yields:
            tuple: (box_id, goal_id)
        """
        if self.boxes_count != self.goals_count:
            return []

        def is_box_goal_pair(box, goal_id):
            if self.is_sokoban_plus_enabled:
                return self.box_plus_id(box[1]) == self.goal_plus_id(goal_id)
            return box[1] == goal_id

        boxes_todo = list(self.boxes_ids)
        goals_ids = list(self.goals_ids)
        for goal_id in goals_ids:
            predicate = partial(is_box_goal_pair, goal_id=goal_id)
            index, box_id = next(filter(predicate, enumerate(boxes_todo)), None)
            yield box_id, goal_id
            del boxes_todo[index]

    def switch_boxes_and_goals(self):
        """Switches positions of boxes and goals pairs."""
        if self.boxes_count != self.goals_count:
            raise BoxGoalSwitchError(
                "Unable to switch boxes and goals - counts are not the same"
            )

        for box_id, goal_id in self._box_goal_pairs():
            old_box_position = self._boxes[box_id]
            old_goal_position = self._goals[goal_id]

            if old_box_position != old_goal_position:
                # If there is a pusher on goal, we have to remove it before
                # we put a box there
                moved_pusher_id = None
                if self.has_pusher_on(old_goal_position):
                    moved_pusher_id = self.pusher_id_on(old_goal_position)
                    self._pushers[moved_pusher_id] = -1
                    self._board[old_goal_position].remove_pusher()

                self._goals[goal_id] = old_box_position
                self._board[old_goal_position].remove_goal()
                self._board[old_box_position].put_goal()

                self._boxes[box_id] = old_goal_position
                self._board[old_box_position].remove_box()
                self._board[old_goal_position].put_box()
                self._box_moved(old_box_position, old_goal_position)

                if moved_pusher_id is not None:
                    # There was pusher on former goal cell and was deleted
                    # We now put it back on board, onto new goal position
                    # Net result is that box and goal switched places and
                    # pusher moved to new goal position.
                    self._pushers[moved_pusher_id] = old_box_position
                    self._board[old_box_position].put_pusher()
                    self._pusher_moved(old_goal_position, old_box_position)

    @property
    def is_playable(self):
        return (
            self.pushers_count > 0
            and self.boxes_count == self.goals_count
            and self.boxes_count > 0
            and self.goals_count > 0
        )

    @property
    def state(self):
        pushers_positions = self.pushers_positions
        boxes_positions = self.boxes_positions
        return BoardState(
            pushers_positions=[
                pushers_positions[pusher_id]
                for pusher_id in sorted(pushers_positions.keys())
            ],
            boxes_positions=[
                boxes_positions[box_id] for box_id in sorted(boxes_positions.keys())
            ],
        )
