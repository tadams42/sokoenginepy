import random
from copy import deepcopy

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
        set_size = (
            # for each pusher on each board position generate random 64b integer
            self.pushers_count * self.board_size +
            # for each distinct box plus id generate random 64b integer
            len(self._distinct_box_plus_ids) * self.board_size +
            # generate one random 64b int for initial board hash
            1
        )

        pool = set()
        while len(pool) < set_size:
            pool.add(random.getrandbits(64))
        return list(pool)

    @property
    def zobrist_hash(self):
        """
        Zobrist hash of board position: 64b board hash number derived from
        position of all pieces on it, different for each configuration of boxes.

        Boxes are diferentiated by their plus ID if Sokoban+ is enabled,
        otherwise they are not diferentiated.

        TODO - pusher position shouldn't influence this hash - for equal boxes
        positions, and different pusher possitions, hash should return same
        number

        Transposition tables using these hashes must be reinitialized in the
        event of
            - Enabling or disabling Sokoban+
            - direct board cell editing

        Movement (transfer) of boxes preserves initial hash and doesn't require
        re-initialization of transposition table.
        """
        if self._zobrist_hash is not None:
            return self._zobrist_hash

        random_pool = self._random_pool
        self._zobrist_hash = random_pool[0]
        random_pool = random_pool[1:]

        for pusher_id in self.pushers_ids:
            # Assign position hashes to pusher
            self._pusher_hashes[pusher_id] = random_pool[:self.board_size]
            random_pool = random_pool[self.board_size:]
            # Add pusher position hash to board hash
            self._zobrist_hash ^= self._pusher_hashes[pusher_id][
                self.pusher_position(pusher_id)
            ]

        # Assign position hashes to all distinct boxes
        for box_plus_id in self._distinct_box_plus_ids:
            self._box_hashes[box_plus_id] = random_pool[:self.board_size]
            random_pool = random_pool[self.board_size:]

        # Add boxes to board hash
        for box_id in self.boxes_ids:
            self._zobrist_hash ^= self._box_hashes[
                self.box_plus_id(box_id)
            ][
                self.box_position(box_id)
            ]

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
        for pusher_id in self.pushers_ids:
            self._normalized_zobrist_hash ^= self._pusher_hashes[pusher_id][
                self.pusher_position(pusher_id)
            ]
        # Add pushers on normalized positions
        for pusher_id in self.pushers_ids:
            self._normalized_zobrist_hash ^= self._pusher_hashes[pusher_id][
                self.normalized_pusher_positions[pusher_id]
            ]

        return self._normalized_zobrist_hash

    def transfer_box(self, old_position, new_position):
        """
        Transfers box from old_positionto to new_position. This method preserves
        piece IDs and is recommended for board movement implementations (direct
        editing of BoardCell doesn't guarantee piece IDs preservation)

        Fails if:
            - box can't be dropped onto new_position position because there is
              an obstacle on it.
            - old_position doesn't contain box
        """

        if old_position == new_position:
            return

        box_id = self.box_id(old_position)
        box_plus_id = self.box_plus_id(box_id)

        self._boxes['id':box_id] = new_position
        # Remove old position hash
        self._zobrist_hash ^= self._box_hashes[box_plus_id][old_position]
        # Add new position hash
        self._zobrist_hash ^= self._box_hashes[box_plus_id][new_position]

    def transfer_pusher(self, old_position, new_position):
        """
        Transfers pusher from old_positionto to new_position. This method
        preserves piece IDs and is recommended for board movement
        implementations (direct editing of BoardCell doesn't guarantee piece
        IDs preservation)

        Fails if:
            - pusher can't be dropped onto new_position position because there
              is an obstacle on it.
            - old_position doesn't contain pusher
        """

        if old_position == new_position:
            return

        pusher_id = self.pusher_id(old_position)

        self._pushers['id':pusher_id] = new_position
        # Remove old position hash
        self._zobrist_hash ^= self._pusher_hashes[pusher_id][old_position]
        # Add new position hash
        self._zobrist_hash ^= self._pusher_hashes[pusher_id][new_position]

    def modify_box_position(self, old_position, new_position):
        """
        Forces position of a piece old_position to new_position.
        preserving piece ID and board hash.
        """
        # TODO
        pass

    def modify_goal_position(self, old_position, new_position):
        # TODO
        pass

    def modify_pusher_position(self, old_position, new_position):
        # TODO
        pass

    def modify_box_position_from_id(self, box_id, new_position):
        # TODO
        pass

    def modify_goal_position_from_id(self, goal_id, new_position):
        # TODO
        pass

    def modify_pusher_position_from_id(self, pusher_id, new_position):
        # TODO
        pass

    def is_solved(self):
        # TODO
        pass

    def solutions(self):
        # TODO
        pass

    def apply(self, state):
        # TODO
        pass

    def switch_boxes_and_goals(self):
        # TODO
        pass
