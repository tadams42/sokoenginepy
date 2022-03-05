import random

from ... import utilities
from ..board_manager import BoardManager
from ..piece import DEFAULT_PIECE_ID


class HashedBoardManager(BoardManager):
    """:class:`.BoardManager` with Zobrist hashing

    Adds Zobrist hashing on top of :class:`.BoardManager` and keeps it up to date
    when pieces are moved.

    Zobrist hash is 64b integer hash derived from positions of all boxes and pushers
    on board.

    When initialized, :class:`.HashedBoardManager` hashes board using positions and
    IDs of boxes and pushers and produces 64b integer hash. After that, whenever
    position of piece changes, this hash is updated. The ``Zobrist`` part means
    hashing is deterministic which then means that undoing movement will return hash
    value to previous one. All this allows for creation of position tables that
    contain many board layouts and can be quickly compared (since we are not
    comparing positions but only hashes of these positions). Being able to quickly
    compare and find current board layout in some big table, speeds up searching
    through game space which is needed for effective solver implementations.

    Boxes with same Sokoban+ ID are treated as equal meaning that if two of these
    boxes switch position, hash will not change. This also means that hash is
    different when Sokoban+ is enabled from the one when it is disabled

    Pushers are all treated equal, meaning that if two pushers switch position, hash
    will not change

    Notes:
        - enabling/disabling Sokoban+ rehashes the board state
        - changing position of pieces only updates existing hash, it doesn't rehash
          whole board. This means that for example undoing box push would "undo" the
          hash value to the one that was before move was preformed
    """

    def __init__(self, variant_board, boxorder=None, goalorder=None):
        super().__init__(variant_board, boxorder, goalorder)
        self._initial_state_hash = None
        self._state_hash = None
        self._pushers_factors = None
        self._boxes_factors = None
        self._solutions_hashes = None
        self._zobrist_rehash()

    def _zobrist_rehash(self):
        """Recalculates Zobrist hash of board position from scratch."""
        distinct_box_plus_ids = set(
            self.box_plus_id(box_id) for box_id in self.boxes_ids
        )

        # We need random numbers only for this number of positions
        board_without_walls_size = self.board.size - len(self.walls_positions)

        random_pool_size = (
            # one random number for each position pusher can occupy
            board_without_walls_size
            # one random number for position each distinct box can occupy
            + len(distinct_box_plus_ids) * board_without_walls_size
            # one random number for initial hash
            + 1
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

        self._initial_state_hash = self._state_hash = random_pool[0]
        random_pool = random_pool[1:]

        # Store position factors for all distinct positions of all distinct
        # boxes
        self._boxes_factors = dict()
        for box_plus_id in distinct_box_plus_ids:
            self._boxes_factors[box_plus_id] = self._insert_wall_zeroes(
                random_pool[:board_without_walls_size]
            )
            random_pool = random_pool[board_without_walls_size:]

        # Store position factors for all distinct pusher positions
        self._pushers_factors = self._insert_wall_zeroes(
            random_pool[:board_without_walls_size]
        )

        for box_id in self.boxes_ids:
            self._state_hash ^= self._boxes_factors[self.box_plus_id(box_id)][
                self.box_position(box_id)
            ]

        for pusher_position in self.pushers_positions.values():
            self._state_hash ^= self._pushers_factors[pusher_position]

    def _insert_wall_zeroes(self, lst):
        src_index = 0

        def choose(position):
            nonlocal src_index
            if position in self.walls_positions:
                return None
            else:
                src_index += 1
                return lst[src_index - 1]

        return [choose(pos) for pos in range(self.board.size)]

    @property
    def state_hash(self):
        """Zobrist hash of current board state."""
        if self._state_hash is None or self._initial_state_hash is None:
            self._zobrist_rehash()
        return self._state_hash

    @property
    def initial_state_hash(self):
        """
        Zobrist hash of initial board state (before any movement happened).
        """
        if self._state_hash is None or self._initial_state_hash is None:
            self._zobrist_rehash()
        return self._initial_state_hash

    def external_state_hash(self, board_state):
        """
        Calculates Zobrist hash of given ``board_state`` as if that ``board_state``
        was applied to initial ``board`` (to board where no movement happened).

        ``board_state`` must meet following requirement:

            len(board_state.boxes_positions) == self.boxes_count
            and len(board_state.boxes_positions) == self.goals_count

        Returns:
            int or None: Value of hash or None if it can't be calculated
        """
        if (
            len(board_state.boxes_positions) != self.boxes_count
            or len(board_state.boxes_positions) != self.goals_count
        ):
            return None

        retv = self.initial_state_hash
        for index, box_position in enumerate(board_state.boxes_positions):
            retv ^= self._boxes_factors[self.box_plus_id(DEFAULT_PIECE_ID + index)][
                box_position
            ]

        for pusher_position in board_state.pushers_positions:
            retv ^= self._pushers_factors[pusher_position]

        board_state.zobrist_hash = retv

        return retv

    def _box_moved(self, old_position, to_new_position):
        if old_position != to_new_position:
            box_plus_id = self.box_plus_id(self.box_id_on(to_new_position))
            self._state_hash ^= self._boxes_factors[box_plus_id][old_position]
            self._state_hash ^= self._boxes_factors[box_plus_id][to_new_position]

    def _pusher_moved(self, old_position, to_new_position):
        if old_position != to_new_position:
            self._state_hash ^= self._pushers_factors[old_position]
            self._state_hash ^= self._pushers_factors[to_new_position]

    @BoardManager.boxorder.setter
    def boxorder(self, rv):
        old_plus_enabled = self.is_sokoban_plus_enabled
        BoardManager.boxorder.fset(self, rv)
        if self.is_sokoban_plus_enabled != old_plus_enabled:
            self._solutions_hashes = None
            self._zobrist_rehash()

    @BoardManager.goalorder.setter
    def goalorder(self, rv):
        old_plus_enabled = self.is_sokoban_plus_enabled
        BoardManager.goalorder.fset(self, rv)
        if self.is_sokoban_plus_enabled != old_plus_enabled:
            self._solutions_hashes = None
            self._zobrist_rehash()

    def enable_sokoban_plus(self):
        old_plus_enabled = self.is_sokoban_plus_enabled
        super().enable_sokoban_plus()
        if self.is_sokoban_plus_enabled != old_plus_enabled:
            self._solutions_hashes = None
            self._zobrist_rehash()

    def disable_sokoban_plus(self):
        old_plus_enabled = self.is_sokoban_plus_enabled
        super().disable_sokoban_plus()
        if self.is_sokoban_plus_enabled != old_plus_enabled:
            self._solutions_hashes = None
            self._zobrist_rehash()

    @property
    def is_solved(self):
        return self.state_hash in self.solutions_hashes

    @property
    def solutions_hashes(self):
        if not self._solutions_hashes:
            self._solutions_hashes = set(
                h
                for h in (
                    self.external_state_hash(solution) for solution in self.solutions()
                )
                if h
            )
        return self._solutions_hashes

    @property
    def state(self):
        retv = super().state
        retv.zobrist_hash = self.state_hash
        return retv
