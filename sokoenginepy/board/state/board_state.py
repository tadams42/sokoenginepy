from collections import OrderedDict

from cached_property import cached_property

from ..piece import Piece
from ..sokoban_plus import SokobanPlus


class BoardState:
    """
    Stores positions, piece IDs and Sokoban+ IDs of all Piece-s on GameBoard
    """

    def __init__(self, variant_board):
        self._variant_board = variant_board
        self._boxes = OrderedDict()
        self._goals = OrderedDict()
        self._pushers = OrderedDict()
        self._sokoban_plus = None

        pusher_id = box_id = goal_id = Piece.DEFAULT_ID

        for position in range(0, variant_board.size):
            cell = variant_board[position]

            if cell.has_pusher:
                self._pushers[pusher_id] = Piece(position, pusher_id)
                pusher_id += 1

            if cell.has_box:
                self._boxes[box_id] = Piece(position, box_id)
                box_id += 1

            if cell.has_goal:
                self._goals[goal_id] = Piece(position, goal_id)
                goal_id += 1

    @property
    def board_size(self):
        return self._variant_board.size

    # --------------------------------------------------------------------------
    # Pushers
    # --------------------------------------------------------------------------

    @cached_property
    def pushers_count(self):
        return len(self._pushers)

    @property
    def pushers_ids(self):
        return self._pushers.keys()

    @cached_property
    def pushers_positions(self):
        return [p.position for p in self._pushers.values()]

    @cached_property
    def normalized_pusher_positions(self):
        retv = dict()
        for pusher in self._pushers.values():
            retv[pusher.id] = self._variant_board.normalized_pusher_position(
                pusher.position,
                excluded_positions=self.boxes_positions + list(retv.values())
            )
        return retv

    def pusher_position(self, id):
        return self._pushers[id].position

    def pusher_id(self, on_position):
        pusher = [
            p for p in self._pushers.values() if p.position == on_position
        ]
        return pusher[0].id

    # --------------------------------------------------------------------------
    # Boxes
    # --------------------------------------------------------------------------

    @cached_property
    def boxes_count(self):
        return len(self._boxes)

    @property
    def boxes_ids(self):
        return self._boxes.keys()

    @cached_property
    def boxes_positions(self):
        return [b.position for b in self._boxes.values()]

    def box_position(self, id):
        return self._boxes[id].position

    def box_id(self, on_position):
        box = [b for b in self._boxes.values() if b.position == on_position]
        return box[0].id

    # --------------------------------------------------------------------------
    # Goals
    # --------------------------------------------------------------------------

    @cached_property
    def goals_count(self):
        return len(self._goals)

    @property
    def goals_ids(self):
        return self._goals.keys()

    @cached_property
    def goals_positions(self):
        return [g.position for g in self._goals.values()]

    def goal_position(self, id):
        return self._goals[id].position

    def goal_id(self, on_position):
        goal = [g for g in self._goals.values() if g.position == on_position]
        return goal[0].id

    # --------------------------------------------------------------------------
    # Sokoban+
    # --------------------------------------------------------------------------

    @cached_property
    def _distinct_box_plus_ids(self):
        return set(box.plus_id for box in self._boxes.values())

    def box_plus_id(self, id):
        return self._boxes[id].plus_id

    def goal_plus_id(self, id):
        return self._goals[id].plus_id

    @property
    def boxorder(self):
        if self._sokoban_plus:
            return self._sokoban_plus.boxorder
        return ""

    @property
    def goalorder(self):
        if self._sokoban_plus:
            return self._sokoban_plus.goalorder
        return ""

    @property
    def is_sokoban_plus_enabled(self):
        if self._sokoban_plus:
            return self._sokoban_plus.is_enabled
        return False

    @is_sokoban_plus_enabled.setter
    def is_sokoban_plus_enabled(self, rv):
        if self._sokoban_plus:
            self._sokoban_plus.is_enabled = rv
            for box in self._boxes:
                box.plus_id = self._sokoban_plus.box_plus_id(box.id)
            for goal in self._goals:
                goal.plus_id = self._sokoban_plus.goal_plus_id(goal.id)

    @property
    def is_sokoban_plus_valid(self):
        if self._sokoban_plus:
            if not self._sokoban_plus.is_valid:
                return self._sokoban_plus.errors
        return True

    def set_sokoban_plus(self, boxorder, goalorder):
        self.is_sokoban_plus_enabled = False
        self._sokoban_plus = SokobanPlus(self.boxes_count, boxorder, goalorder)
