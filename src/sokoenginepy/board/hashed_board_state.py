import random

from .. import utilities
from .board_state import BoardState


class HashedBoardState(BoardState, metaclass=utilities.InheritableDocstrings):
    """:class:`.BoardState` with Zobrist hashing

    Adds Zobrist hashing on top of :class:`.BoardState` and keeps it up to date
    when pieces are moved.

    Zobrist hash is 64b integer hash derived from positions of all boxes on
    board.

    For most applications, it is only interesting to use hash of boxes'
    positions. Sometimes might be usefull to have hash derived from both,
    boxes' and pushers' positions.

    Boxes with same Sokoban+ ID are treated as equal meaning that if two of
    these boxes switch position, hash will not change. This also means that
    hash is different when Sokoban+ is enabled from the one when it is disabled

    Pushers are all treated equal, meaning that if two pushers switch position,
    hash will not change

    Notes:
        - enabling/disabling Sokoban+ rehashes the board state
        - changing position of pieces only updates existing hash, it doesn't
          rehash whole board. This means that for example undoing box push
          would "undo" the hash value to the one that was before move was
          preformed
    """

    def __init__(self, variant_board):
        super().__init__(variant_board)
        self._initial_layout_hash = None
        self._layout_hash = None
        self._initial_with_pushers_hash = None
        self._layout_with_pushers_hash = None
        self._pushers_factors = None
        self._boxes_factors = None
        self._solutions_hashes = None
        self._zobrist_rehash()

    def _zobrist_rehash(self):
        """Recalculates Zobrist hash of board position from scratch."""
        distinct_box_plus_ids = set(
            self.box_plus_id(box_id) for box_id in self.boxes_ids
        )

        random_pool_size = (
            # one random number for each position pusher can occupy
            self.board.size +
            # one random number for position each distinct box can occupy
            len(distinct_box_plus_ids) * self.board.size +
            # one random number for initial hash
            1
        )

        # generate required set of random numbers
        # state_backup = random.getstate()
        # Seeding to constant always produces same sequence which then ensures
        # that equal board layouts always produce equal hash
        # random.seed(42)
        random_pool = set()
        while len(random_pool) < random_pool_size:
            random_pool.add(random.getrandbits(64))
        random_pool = list(random_pool)
        # random.setstate(state_backup)

        self._initial_layout_hash = self._layout_hash = random_pool[0]
        random_pool = random_pool[1:]

        # Store position factors for all distinct positions of all distinct
        # boxes
        self._boxes_factors = dict()
        for box_plus_id in distinct_box_plus_ids:
            self._boxes_factors[box_plus_id] = random_pool[:self.board.size]
            random_pool = random_pool[self.board.size:]

        # Store position factors for all distinct pusher positions
        self._pushers_factors = random_pool[:self.board.size]

        # Hash from boxes positions
        for box_id in self.boxes_ids:
            self._layout_hash ^= (
                self._boxes_factors[self.box_plus_id(box_id)]
                [self.box_position(box_id)]
            )

        # Hash from pushers' and boxes' positions
        self._layout_with_pushers_hash = \
            self._initial_with_pushers_hash = \
            self._layout_hash
        for pusher_position in self.pushers_positions.values():
            self._layout_with_pushers_hash ^= (
                self._pushers_factors[pusher_position]
            )

        # Reset solution hashes
        self._solutions_hashes = None

    @property
    def boxes_layout_hash(self):
        """Board hash.

        Constructed from current boxes layout and current boxes' Sokoban+ IDs.
        """
        return self._layout_hash

    @property
    def boxes_and_pushers_layout_hash(self):
        """Board hash.

        Constructed from current boxes layout, current boxes' Sokoban+ IDs and
        current pushers' layout
        """
        return self._layout_with_pushers_hash

    def external_position_hash(self, boxes_positions):
        """Same as :attr:`.boxes_layout_hash` but calculated for arbitrarily
        board layout.

        Given dict of boxes positions, it calculates :attr:`.boxes_layout_hash`
        that position would have if it was applied to this board.

        Args:
            boxes_positions(dict): map of boxes' ids and positions, ie::

                {id1: position1, id2: position2}

        Note:
            Returns None in case len(boxes_positions) != self.boxes_count
        """
        if (len(boxes_positions) != self.boxes_count or
                len(boxes_positions) != self.goals_count):
            return None

        if self._initial_layout_hash is None:
            self._zobrist_rehash()

        retv = self._initial_layout_hash
        for box_id, box_position in boxes_positions.items():
            retv ^= self._boxes_factors[self.box_plus_id(box_id)][box_position]

        return retv

    def _box_moved(self, old_position, to_new_position):
        if old_position != to_new_position:
            box_plus_id = self.box_plus_id(self.box_id_on(to_new_position))

            self._layout_hash ^= self._boxes_factors[box_plus_id][old_position]
            self._layout_hash ^= self._boxes_factors[box_plus_id
                                                    ][to_new_position]
            self._layout_with_pushers_hash ^= self._boxes_factors[box_plus_id
                                                                 ][old_position]
            self._layout_with_pushers_hash ^= self._boxes_factors[box_plus_id][
                to_new_position
            ]

    def _pusher_moved(self, old_position, to_new_position):
        if old_position != to_new_position:
            self._layout_with_pushers_hash ^= self._pushers_factors[old_position]
            self._layout_with_pushers_hash ^= self._pushers_factors[
                to_new_position
            ]

    @BoardState.boxorder.setter
    @copy_ancestor_docstring
    def boxorder(self, rv):
        old_plus_enabled = self.is_sokoban_plus_enabled
        BoardState.boxorder.fset(self, rv)
        if self.is_sokoban_plus_enabled != old_plus_enabled:
            self._zobrist_rehash()

    @BoardState.goalorder.setter
    @copy_ancestor_docstring
    def goalorder(self, rv):
        old_plus_enabled = self.is_sokoban_plus_enabled
        BoardState.goalorder.fset(self, rv)
        if self.is_sokoban_plus_enabled != old_plus_enabled:
            self._zobrist_rehash()

    @copy_ancestor_docstring
    def enable_sokoban_plus(self):
        old_plus_enabled = self.is_sokoban_plus_enabled
        super().enable_sokoban_plus()
        if self.is_sokoban_plus_enabled != old_plus_enabled:
            self._zobrist_rehash()

    @copy_ancestor_docstring
    def disable_sokoban_plus(self):
        old_plus_enabled = self.is_sokoban_plus_enabled
        super().disable_sokoban_plus()
        if self.is_sokoban_plus_enabled != old_plus_enabled:
            self._zobrist_rehash()

    def is_solved(self):
        if self._initial_layout_hash is None:
            self._zobrist_rehash()

        if not self._solutions_hashes:
            self._solutions_hashes = set(
                h
                for h in [
                    self.external_position_hash(solution)
                    for solution in self.solutions()
                ] if h
            )

        return self._layout_hash in self._solutions_hashes

    @property
    def solution_hashes(self):
        # regenerate solution hashes
        self.is_solved()
        return self._solutions_hashes

    @copy_ancestor_docstring
    def switch_boxes_and_goals(self):
        retv = super().switch_boxes_and_goals()
        self._solutions_hashes = None
        return retv
