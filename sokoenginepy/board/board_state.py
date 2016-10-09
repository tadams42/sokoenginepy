from itertools import permutations

from cached_property import cached_property
from midict import MIDict

from ..common import DEFAULT_PIECE_ID
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
    def normalized_pusher_positions(self):
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

    def pusher_id(self, on_position):
        try:
            return self._pushers['position':on_position]
        except KeyError:
            raise KeyError("No pusher on position: {0}".format(on_position))

    def has_pusher(self, pid):
        return pid in self._pushers.keys(self._INDEX_ID)

    def has_pusher_on(self, position):
        return position in self._pushers.keys(self._INDEX_POS)

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

    def box_id(self, on_position):
        try:
            return self._boxes['position':on_position]
        except KeyError:
            raise KeyError("No box on position: {0}".format(on_position))

    def has_box(self, pid):
        return pid in self._boxes.keys(self._INDEX_ID)

    def has_box_on(self, position):
        return position in self._boxes.keys(self._INDEX_POS)

    # --------------------------------------------------------------------------
    # Goals
    # --------------------------------------------------------------------------

    @cached_property
    def goals_count(self):
        return len(self._goals)

    @cached_property
    def goals_ids(self):
        return list(self._goals.keys(self._INDEX_ID))

    @cached_property
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

    def goal_id(self, on_position):
        try:
            return self._goals['position':on_position]
        except KeyError:
            raise KeyError("No goal on position: {0}".format(on_position))

    def has_goal(self, pid):
        return pid in self._goals.keys(self._INDEX_ID)

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
                goal_id = self.goal_id(box_position)
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
