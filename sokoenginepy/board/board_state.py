from copy import deepcopy
from functools import partial
from itertools import permutations

from cached_property import cached_property
from midict import MIDict, ValueExistsError

from ..common import DEFAULT_PIECE_ID
from .exceptions import CellAlreadyOccupiedError
from .sokoban_plus import SokobanPlus


class BoardState:
    """
    Memoizes all pieces on board and allows state modifications.

    Note that it never modifies actual board cells - it just adjusts memoized
    state for given board. Also, if given board is modified outside of
    BoardState (ie. cells with boxes are edited, board is resized, etc..) this
    is not automatically reflected on BoardState.

    For reasons abowe, clients are responsible for syncing board and its
    BoardState
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
                self._pushers['id':pusher_id] = position
                pusher_id += 1

            if cell.has_box:
                self._boxes['id':box_id] = position
                box_id += 1

            if cell.has_goal:
                self._goals['id':goal_id] = position
                goal_id += 1

        self._sokoban_plus = SokobanPlus(
            pieces_count=len(self._boxes), boxorder='', goalorder=''
        )

    @cached_property
    def board_size(self):
        return self._variant_board.size

    # --------------------------------------------------------------------------
    # Pushers
    # --------------------------------------------------------------------------

    @cached_property
    def pushers_count(self):
        return len(self._pushers)

    @cached_property
    def pushers_ids(self):
        return list(self._pushers.keys(self._INDEX_ID))

    @property
    def pushers_positions(self):
        return dict(
            (pid, self._pushers[self._INDEX_ID:pid])
            for pid in self._pushers.keys(self._INDEX_ID)
        )

    @cached_property
    def normalized_pushers_positions(self):
        retv = dict()
        excluded = list(self.boxes_positions.values())
        for pid, position in self._pushers.iteritems():
            retv[pid] = self._variant_board.normalized_pusher_position(
                position, excluded_positions=excluded
            )
            excluded = excluded + [retv[pid]]
        return retv

    def pusher_position(self, pid):
        try:
            return self._pushers['id':pid]
        except KeyError:
            raise KeyError("No pusher with ID: {0}".format(pid))

    def pusher_id_on(self, on_position):
        try:
            return self._pushers['position':on_position]
        except KeyError:
            raise KeyError("No pusher on position: {0}".format(on_position))

    def has_pusher(self, pid):
        # TODO Buggy MIDict forces us to convert to list here
        return pid in list(self._pushers.keys(self._INDEX_ID))

    def has_pusher_on(self, position):
        return position in self._pushers.keys(self._INDEX_POS)

    def _move_pusher(self, pusher_id, from_old_position, to_new_position):
        try:
            self._pushers['id':pusher_id] = to_new_position
        except ValueExistsError:
            raise CellAlreadyOccupiedError(
                "Pusher can't be placed onto pusher in position: {0}".format(
                    to_new_position
                )
            )

    def move_pusher(self, from_old_position, to_new_position):
        """
        Updates board state with changed pusher position.

        It doesn't verify if from_old_position and to_new_position are valid
        board positions.

        Raises KeyError in case there is no pusher on from_old_position.

        Raises CellAlreadyOccupiedError if there is a pusher already on
        to_new_position

        Note: Allows placing of a pusher onto position occupied by box. This is
        for cases when we switch box/goals positions in reverse solving mode.
        In this situation it is legal for pusher to end up standing on top of
        the box. Game rules say that for these situations, first move(s) must be
        jumps
        """
        if from_old_position == to_new_position:
            return
        pusher_id = self.pusher_id_on(from_old_position)
        self._move_pusher(pusher_id, from_old_position, to_new_position)

    def move_pusher_id(self, pusher_id, to_new_position):
        """
        Updates board state with changed pusher position.

        It doesn't verify if from_old_position and to_new_position are valid
        board positions.

        Raises KeyError in case there is no pusher with pusher_id

        Raises CellAlreadyOccupiedError if there is a pusher already on
        to_new_position

        Note: Allows placing of a pusher onto position occupied by box. This is
        for cases when we switch box/goals positions in reverse solving mode.
        In this situation it is legal for pusher to end up standing on top of
        the box. Game rules say that for these situations, first move(s) must be
        jumps
        """
        from_old_position = self.pusher_position(pusher_id)
        if from_old_position == to_new_position:
            return
        self._move_pusher(pusher_id, from_old_position, to_new_position)

    # --------------------------------------------------------------------------
    # Boxes
    # --------------------------------------------------------------------------

    @cached_property
    def boxes_count(self):
        return len(self._boxes)

    @cached_property
    def boxes_ids(self):
        return list(self._boxes.keys(self._INDEX_ID))

    @property
    def boxes_positions(self):
        return dict(
            (pid, self._boxes[self._INDEX_ID:pid])
            for pid in self._boxes.keys(self._INDEX_ID)
        )

    def box_position(self, pid):
        try:
            return self._boxes['id':pid]
        except KeyError:
            raise KeyError("No box with ID: {0}".format(pid))

    def box_id_on(self, on_position):
        try:
            return self._boxes['position':on_position]
        except KeyError:
            raise KeyError("No box on position: {0}".format(on_position))

    def has_box(self, pid):
        # TODO Buggy MIDict forces us to convert to list here
        return pid in list(self._boxes.keys(self._INDEX_ID))

    def has_box_on(self, position):
        return position in self._boxes.keys(self._INDEX_POS)

    def _move_box(self, box_id, box_plus_id, from_old_position, to_new_position):
        try:
            self._boxes['id':box_id] = to_new_position
        except ValueExistsError:
            raise CellAlreadyOccupiedError(
                "Box can't be placed onto box in position: {0}".format(
                    to_new_position
                )
            )

    def move_box(self, from_old_position, to_new_position):
        """
        Updates board state with changed box position.

        It doesn't verify if from_old_position and to_new_position are valid
        board positions.

        Raises KeyError in case there is no box on from_old_position.

        Raises CellAlreadyOccupiedError if there is a box already on
        to_new_position

        Note: Allows placing of a box onto position occupied by pusher. This is
        for cases when we switch box/goals positions in reverse solving mode.
        In this situation it is legal for pusher to end up standing on top of
        the box. Game rules say that for these situations, first move(s) must be
        jumps
        """
        if from_old_position == to_new_position:
            return
        box_id = self.box_id_on(from_old_position)
        box_plus_id = self.box_plus_id(box_id)
        self._move_box(box_id, box_plus_id, from_old_position, to_new_position)

    def move_box_id(self, box_id, to_new_position):
        """
        Updates board state with changed box position.

        It doesn't verify if from_old_position and to_new_position are valid
        board positions.

        Raises KeyError in case there is no box with box_id.

        Raises CellAlreadyOccupiedError if there is a box already on
        to_new_position

        Note: Allows placing of a box onto position occupied by pusher. This is
        for cases when we switch box/goals positions in reverse solving mode.
        In this situation it is legal for pusher to end up standing on top of
        the box. Game rules say that for these situations, first move(s) must be
        jumps
        """
        from_old_position = self.box_position(box_id)
        if from_old_position == to_new_position:
            return
        box_plus_id = self.box_plus_id(box_id)
        self._move_box(box_id, box_plus_id, from_old_position, to_new_position)

    # --------------------------------------------------------------------------
    # Goals
    # --------------------------------------------------------------------------

    @cached_property
    def goals_count(self):
        return len(self._goals)

    @cached_property
    def goals_ids(self):
        return list(self._goals.keys(self._INDEX_ID))

    @property
    def goals_positions(self):
        return dict(
            (pid, self._goals[self._INDEX_ID:pid])
            for pid in self._goals.keys(self._INDEX_ID)
        )

    def goal_position(self, pid):
        try:
            return self._goals['id':pid]
        except KeyError:
            raise KeyError("No goal with ID: {0}".format(pid))

    def goal_id_on(self, on_position):
        try:
            return self._goals['position':on_position]
        except KeyError:
            raise KeyError("No goal on position: {0}".format(on_position))

    def has_goal(self, pid):
        # TODO Buggy MIDict forces us to convert to list here
        return pid in list(self._goals.keys(self._INDEX_ID))

    def has_goal_on(self, position):
        return position in self._goals.keys(self._INDEX_POS)

    # --------------------------------------------------------------------------
    # Sokoban+
    # --------------------------------------------------------------------------

    def box_plus_id(self, pid):
        return self._sokoban_plus.box_plus_id(pid)

    def goal_plus_id(self, pid):
        return self._sokoban_plus.goal_plus_id(pid)

    @property
    def boxorder(self):
        return self._sokoban_plus.boxorder

    @boxorder.setter
    def boxorder(self, rv):
        self._sokoban_plus.boxorder = rv

    @property
    def goalorder(self):
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
        Generator for all configurations of boxes that result in solved board
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
        """
        Finds a list of (box_id, goal_id,) tuples. If Sokoban+ is enabled,
        boxes and goals are paired by Sokoban+ IDs, otherwise they are paired by
        regular IDs
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
        """
        Switches positions of boxes and goals pairs.

        Returns dictionary describing operations that need to pe performed on
        board cells for this switch.

        {
            # Positions of pusher cells from which pusher has to be removed
            # before switch
            'pusher_to_remove': [pusher_position1, pusher_position2, '...'],
            # Positions of pusher cells on which pusher has to be placed after
            # switch
            'pushers_to_place': [pusher_position1, pusher_position2, '...'],
            # Positions of board cells on which switch has to be performed
            'switches': [board_position1, board_position2, '...'],
        }
        """
        if self.boxes_count != self.goals_count:
            raise SokoengineError(
                "Unable to switch boxes and goals - counts are not the same"
            )

        retv = {
            'pusher_to_remove': [],
            'pushers_to_place': [],
            'switches': [],
        }

        for box_id, goal_id in self._box_goal_pairs():
            box_position = self.box_position(box_id)
            goal_position = self.goal_position(goal_id)

            if box_position != goal_position:
                if self.has_pusher_on(goal_position):
                    retv['pusher_to_remove'].append(goal_position)
                    retv['pushers_to_place'].append(box_position)
                    self.move_pusher_id(
                        self.pusher_id_on(goal_position), box_position
                    )

                self.move_box_id(box_id, goal_position)
                self._goals['id':goal_id] = box_position

                retv['switches'].append(box_position)
                retv['switches'].append(goal_position)

        return retv
