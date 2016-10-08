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
        # For some reason following doesn't always work
        # return self._pushers.keys('id')
        return list(self._pushers.keys(0))

    @property
    def pushers_positions(self):
        # For some reason following doesn't always work
        # return self._pushers.keys('position')
        return list(self._pushers.keys(1))

    @cached_property
    def normalized_pusher_positions(self):
        retv = dict()
        excluded = list(self.boxes_positions)
        for pid, position in self._pushers.iteritems():
            retv[pid] = self._variant_board.normalized_pusher_position(
                position, excluded_positions=excluded
            )
            excluded = excluded + [retv[pid]]
        return retv

    def pusher_position(self, pid):
        return self._pushers['id':pid]

    def pusher_id(self, on_position):
        return self._pushers['position':on_position]

    # --------------------------------------------------------------------------
    # Boxes
    # --------------------------------------------------------------------------

    @cached_property
    def boxes_count(self):
        return len(self._boxes)

    @cached_property
    def boxes_ids(self):
        # For some reason following doesn't always work
        # return self._boxes.keys('id')
        return list(self._boxes.keys(0))

    @property
    def boxes_positions(self):
        # For some reason following doesn't always work
        # return self._boxes.keys('position')
        return list(self._boxes.keys(1))

    def box_position(self, pid):
        return self._boxes['id':pid]

    def box_id(self, on_position):
        return self._boxes['position':on_position]

    # --------------------------------------------------------------------------
    # Goals
    # --------------------------------------------------------------------------

    @cached_property
    def goals_count(self):
        return len(self._goals)

    @cached_property
    def goals_ids(self):
        # For some reason following doesn't always work
        # return self._goals.keys('id')
        return list(self._goals.keys(0))

    @property
    def goals_positions(self):
        # For some reason following doesn't always work
        # return self._goals.keys('position')
        return list(self._goals.keys(1))

    def goal_position(self, pid):
        return self._goals['id':pid]

    def goal_id(self, on_position):
        return self._goals['position':on_position]

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
