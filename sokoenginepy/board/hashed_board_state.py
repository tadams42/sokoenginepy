import random

from midict import ValueExistsError

from .board_state import BoardState
from .exceptions import CellAlreadyOccupiedError


class HashedBoardState(BoardState):
    """
    Adds Zobrist hashing on top of board piece data efectively hashing board
    state whenever pieces data (like positions and/or Sokoban+ IDs) change.
    """

    def __init__(self, variant_board):
        super().__init__(variant_board)
        self._initial_position_hash = None
        self._position_hash = None
        self._initial_position_with_pushers_hash = None
        self._position_with_pushers_hash = None
        self._pushers_factors = None
        self._boxes_factors = None
        self._solutions_hashes = None
        self._zobrist_rehash()

    def _zobrist_rehash(self):
        """
        Recalculates Zobrist hash of board position from scratch.

        Zobrist hash is 64b board hash number derived from position of all
        pieces on it, different for each configuration of boxes and pushers.

        For most applications, it is only interesting too use hash of boxes'
        positions. Sometimes might be usefull to have hash derived from both,
        boxes' and pushers' positions. This method calculates initial value for
        both of these hashes.

        Boxes with same Sokoban+ ID are treated as equal meaning that if two of
        these boxes switch position, hash will not change. Note that this means
        that hash is different when Sokoban+ is enabled from the one when it is
        disabled

        Pushers are all treated equal, meaning that if two pushers switch
        position, hash will not change

        Note the following:
            - enabling/disabling Sokoban+ rehashes the board state
            - changing position of pieces only updates existing hash, it doesn't
              rehash whole board. This means that for example undoing box push
              would "undo" the hash value to the one that was before move was
              preformed
        """

        distinct_box_plus_ids = set(
            self.box_plus_id(box_id) for box_id in self.boxes_ids
        )

        random_pool_size = (
            # one random number for each position pusher can occupy
            self.board_size +
            # one random number for position each distinct box can occupy
            len(distinct_box_plus_ids) * self.board_size +
            # one random number for initial hash
            1
        )

        # generate required set of random numbers
        random_pool = set()
        while len(random_pool) < random_pool_size:
            random_pool.add(random.getrandbits(64))
        random_pool = list(random_pool)

        self._initial_position_hash = self._position_hash = random_pool[0]
        random_pool = random_pool[1:]

        # Store position factors for all distinct positions of all distinct boxes
        self._boxes_factors = dict()
        for box_plus_id in distinct_box_plus_ids:
            self._boxes_factors[box_plus_id] = random_pool[:self.board_size]
            random_pool = random_pool[self.board_size:]

        # Store position factors for all distinct pusher positions
        self._pushers_factors = random_pool[:self.board_size]

        # Hash from boxes positions
        for box_id in self.boxes_ids:
            self._position_hash ^= (
                self._boxes_factors[self.box_plus_id(box_id)]
                    [self.box_position(box_id)]
            )

        # Hash from pushers' and boxes' positions
        self._position_with_pushers_hash = \
            self._initial_position_with_pushers_hash = \
            self._position_hash
        for pusher_position in self.pushers_positions.values():
            self._position_with_pushers_hash ^= (
                self._pushers_factors[pusher_position]
            )

        # Reset solution hashes
        self._solutions_hashes = None

    @property
    def position_hash(self):
        """
        Board state hash constructed from current boxes layout and current
        boxes' Sokoban+ IDs.

        Boxes with same Sokoban+ ID are treated as equal meaning that if two of
        these boxes switch position, hash will not change. Note that this means
        that position_hash is different when Sokoban+ is enabled from the one
        when it is disabled

        Note the following:
            - enabling/disabling Sokoban+ rehashes the board
            - changing position of pieces only updates existing hash, it doesn't
              rehash whole board. This means that for example undoing box push
              would "undo" the hash value to the one that was before move was
              preformed
        """
        return self._position_hash

    def external_position_hash(self, position):
        """
        Given dict of boxes positions, ie: {id1: position1, id2: position2,},
        it calculates position_hash that position would have if it was applied
        to this board.

        Returns None in case len(position) != self.boxes_count
        """
        if (
            len(position) != self.boxes_count or
            len(position) != self.goals_count
        ):
            return None

        if self._initial_position_hash is None:
            self._zobrist_rehash()

        position_hash = self._initial_position_hash
        for box_id, box_position in position.items():
            position_hash ^= self._boxes_factors[
                self.box_plus_id(box_id)
            ][box_position]

        return position_hash

    def _move_box(self, box_id, box_plus_id, from_old_position, to_new_position):
        if self.has_pusher_on(to_new_position):
            raise CellAlreadyOccupiedError(
                "Box can't be placed onto pusher in position: {0}".format(
                    to_new_position
                )
            )

        try:
            self._boxes['id':box_id] = to_new_position
        except ValueExistsError:
            raise CellAlreadyOccupiedError(
                "Box can't be placed onto box in position: {0}".format(
                    to_new_position
                )
            )
        # update hashes
        self._position_hash ^= self._boxes_factors[box_plus_id][from_old_position]
        self._position_hash ^= self._boxes_factors[box_plus_id][to_new_position]
        self._position_with_pushers_hash ^= self._boxes_factors[box_plus_id][from_old_position]
        self._position_with_pushers_hash ^= self._boxes_factors[box_plus_id][to_new_position]

    def move_box(self, from_old_position, to_new_position):
        """
        Updates board state with changed box position.

        It doesn't verify if from_old_position and to_new_position are valid
        board positions.

        Raises KeyError in case there is no box on from_old_position.

        Raises CellAlreadyOccupiedError if there is a box or a pusher already on
        to_new_position
        """
        if from_old_position == to_new_position:
            return
        box_id = self.box_id(from_old_position)
        box_plus_id = self.box_plus_id(box_id)
        self._move_box(box_id, box_plus_id, from_old_position, to_new_position)

    def move_box_id(self, box_id, to_new_position):
        """
        Updates board state with changed box position.

        It doesn't verify if from_old_position and to_new_position are valid
        board positions.

        Raises KeyError in case there is no box with box_id

        Raises CellAlreadyOccupiedError if there is a box or a pusher already on
        to_new_position
        """
        from_old_position = self.box_position(box_id)
        if from_old_position == to_new_position:
            return
        box_plus_id = self.box_plus_id(box_id)
        self._move_box(box_id, box_plus_id, from_old_position, to_new_position)

    def _move_pusher(self, pusher_id, from_old_position, to_new_position):
        if self.has_box_on(to_new_position):
            raise CellAlreadyOccupiedError(
                "Pusher can't be placed onto box in position: {0}".format(
                    to_new_position
                )
            )

        try:
            self._pushers['id':pusher_id] = to_new_position
        except ValueExistsError:
            raise CellAlreadyOccupiedError(
                "Pusher can't be placed onto pusher in position: {0}".format(
                    to_new_position
                )
            )
        # Update hashes
        self._position_with_pushers_hash ^= self._pushers_factors[from_old_position]
        self._position_with_pushers_hash ^= self._pushers_factors[to_new_position]

    def move_pusher(self, from_old_position, to_new_position):
        """
        Updates board state with changed pusher position.

        It doesn't verify if from_old_position and to_new_position are valid
        board positions.

        Raises KeyError in case there is no pusher on from_old_position.

        Raises CellAlreadyOccupiedError if there is a box or a pusher already on
        to_new_position
        """
        if from_old_position == to_new_position:
            return
        pusher_id = self.pusher_id(from_old_position)
        self._move_pusher(pusher_id, from_old_position, to_new_position)

    def move_pusher_id(self, pusher_id, to_new_position):
        """
        Updates board state with changed pusher position.

        It doesn't verify if from_old_position and to_new_position are valid
        board positions.

        Raises KeyError in case there is no pusher with pusher_id

        Raises CellAlreadyOccupiedError if there is a box or a pusher already on
        to_new_position
        """
        from_old_position = self.pusher_position(pusher_id)
        if from_old_position == to_new_position:
            return
        self._move_pusher(pusher_id, from_old_position, to_new_position)

    @BoardState.boxorder.setter
    def boxorder(self, rv):
        old_plus_enabled = self.is_sokoban_plus_enabled
        BoardState.boxorder.fset(self, rv)
        if self.is_sokoban_plus_enabled != old_plus_enabled:
            self._zobrist_rehash()

    @BoardState.goalorder.setter
    def goalorder(self, rv):
        old_plus_enabled = self.is_sokoban_plus_enabled
        BoardState.goalorder.fset(self, rv)
        if self.is_sokoban_plus_enabled != old_plus_enabled:
            self._zobrist_rehash()

    @BoardState.is_sokoban_plus_enabled.setter
    def is_sokoban_plus_enabled(self, rv):
        old_plus_enabled = self.is_sokoban_plus_enabled
        BoardState.is_sokoban_plus_enabled.fset(self, rv)
        if self.is_sokoban_plus_enabled != old_plus_enabled:
            self._zobrist_rehash()

    def is_solved(self):
        if self._initial_position_hash is None:
            self._zobrist_rehash()

        if not self._solutions_hashes:
            self._solutions_hashes = set(
                h for h in [
                    self.external_position_hash(solution)
                    for solution in self.solutions()
                ] if h
            )

        return self._position_hash in self._solutions_hashes

    def switch_boxes_and_goals(self):
        # TODO
        pass
