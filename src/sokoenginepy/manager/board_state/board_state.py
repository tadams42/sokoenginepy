class BoardState:
    """
    Sample of board state.

    Attributes:
        pushers_positions(list): Positions of pushers sorted by pusher ID
        boxes_positions(list): Positions of boxes sorted by box ID
        zobrist_hash(int): Zobrist hash of state (see `.HashedBoardManager`)
    """

    def __init__(
        self, pushers_positions=None, boxes_positions=None,
        zobrist_hash=None
    ):
        self._pushers_positions = pushers_positions
        self._boxes_positions = boxes_positions
        self._zobrist_hash = zobrist_hash

    @property
    def pushers_positions(self):
        return self._pushers_positions or []

    @pushers_positions.setter
    def pushers_positions(self, rv):
        self._pushers_positions = rv

    @property
    def boxes_positions(self):
        return self._boxes_positions or []

    @boxes_positions.setter
    def boxes_positions(self, rv):
        self._boxes_positions = rv

    @property
    def zobrist_hash(self):
        return self._zobrist_hash or 0

    @zobrist_hash.setter
    def zobrist_hash(self, rv):
        self._zobrist_hash = rv

    def __str__(self):
        prefix = (len(self.__class__.__name__) + 2) * ' '
        return '\n'.join([
            '<{} pushers_positions: {},'.format(
                self.__class__.__name__,
                self.pushers_positions
            ),
            prefix + 'boxes_positions: {},'.format(self.boxes_positions),
            prefix + 'zobrist_hash: {}'.format(self.zobrist_hash) + '>'
        ])

    def __repr__(self):
        return (
            "{}(pushers_positions={}, boxes_positions={}, zobrist_hash={})".
            format(
                self.__class__.__name__,
                repr(self.pushers_positions),
                repr(self.boxes_positions),
                repr(self.zobrist_hash)
            )
        )

    def __eq__(self, other):
        return (
            self.zobrist_hash is not None
            and self.zobrist_hash is not 0
            and self.zobrist_hash == other.zobrist_hash
        ) or (
            self.boxes_positions == other.boxes_positions
            and self.pushers_positions == other.pushers_positions
        )
