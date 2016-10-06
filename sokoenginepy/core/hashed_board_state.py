from copy import deepcopy
import random
from .board_state import BoardState


class HashedBoardState(BoardState):
    """
    Adds Zobrist hashing on top of board piece data efectively hashing board
    state whenever pieces data (like positions and/or Sokoban+ IDs) change.
    """

    def __init__(self, variant_board):
        super().__init__(variant_board)
        self._zobrist_hash = None
        self._normalized_zobrist_hash = None
        self._pusher_hashes = dict()
        self._box_hashes = dict()

    @property
    def _random_pool(self):
        """
        - for each pusher on each board position enerate random 64b integer
        - for each distinct box plus id generate random 64b integer
        - generate one random 64b int for initial board hash
        """
        set_size = (
            1 + self.board_size * len(self._distinct_box_plus_ids) *
            self.pushers_count
        )

        pool = set()
        while len(pool) < set_size:
            pool.add(random.getrandbits(64))
        return list(pool)

    @property
    def zobrist_hash(self):
        """
        64b board hash number derived from position of all pieces on it.
        """
        if self._zobrist_hash is not None:
            return self._zobrist_hash

        random_pool = self._random_pool
        self._zobrist_hash = random_pool[0]
        random_pool = random_pool[1:]

        for pusher in self._pushers.values():
            # Assign position hashes to pusher
            self._pusher_hashes[pusher.id] = random_pool[:self.board_size]
            random_pool = random_pool[self.board_size:]
            # yapf: disable
            # Add pusher position hash to board hash
            self._zobrist_hash ^= self._pusher_hashes[pusher.id][pusher.position]
            # yapf: enable

        # Assign position hashes to all distinct boxes
        for box_plus_id in self._distinct_box_plus_ids:
            self._box_hashes[box_plus_id] = random_pool[:self.board_size]
            random_pool = random_pool[self.board_size:]

        # Add boxes to board hash
        for box in self._boxes.values():
            self._zobrist_hash ^= self._box_hashes[box.plus_id][box.position]

        return self._zobrist_hash

    @property
    def normalized_zobrist_hash(self):
        """
        Like self.zobrist_hash, but with all pushers placed on their normalized
        positions
        """
        if self._normalized_zobrist_hash is not None:
            return self._normalized_zobrist_hash

        self._normalized_zobrist_hash = deepcopy(self.zobrist_hash)

        # remove pushers from hash
        for pusher in self._pushers.values():
            self._normalized_zobrist_hash ^= self._pusher_hashes[pusher.id][
                pusher.position
            ]
        # Add pushers on normalized positions
        for pusher in self._pushers.values():
            self._normalized_zobrist_hash ^= self._pusher_hashes[pusher.id][
                self.normalized_pusher_positions[pusher.id]
            ]

        return self._normalized_zobrist_hash

    def transfer_box(self, old_position, new_position):
        if old_position == new_position:
            return

        box = [b for b in self._boxes.values() if b.position == old_position][0]

        box.position = new_position
        # Remove old position hash
        self._zobrist_hash ^= self._box_hashes[box.plus_id][old_position]
        # Add new position hash
        self._zobrist_hash ^= self._box_hashes[box.plus_id][new_position]

    def transfer_pusher(self, old_position, new_position):
        if old_position == new_position:
            return

        pusher = [
            p for p in self._pushers.values() if p.position == old_position
        ][0]

        pusher.position = new_position
        # Remove old position hash
        self._zobrist_hash ^= self._pusher_hashes[pusher.id][old_position]
        # Add new position hash
        self._zobrist_hash ^= self._pusher_hashes[pusher.id][new_position]
