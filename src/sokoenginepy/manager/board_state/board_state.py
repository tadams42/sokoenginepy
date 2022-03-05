from typing import Optional, Sequence


class BoardState:
    """
    Sample of board state.

    Attributes:
        pushers_positions: Positions of pushers sorted by pusher ID
        boxes_positions: Positions of boxes sorted by box ID
        zobrist_hash: Zobrist hash of state (see `.HashedBoardManager`)
    """

    UNKNOWN_ZOBRIST_HASH = 0

    def __init__(
        self,
        pushers_positions: Optional[Sequence[int]] = None,
        boxes_positions: Optional[Sequence[int]] = None,
        zobrist_hash: int = UNKNOWN_ZOBRIST_HASH,
    ):
        self.pushers_positions = pushers_positions or []
        self.boxes_positions = boxes_positions or []
        self.zobrist_hash = zobrist_hash or self.UNKNOWN_ZOBRIST_HASH

    @property
    def pushers_positions(self) -> Sequence[int]:
        return self._pushers_positions

    @pushers_positions.setter
    def pushers_positions(self, rv: Sequence[int]):
        self._pushers_positions = rv or []

    @property
    def boxes_positions(self) -> Sequence[int]:
        return self._boxes_positions

    @boxes_positions.setter
    def boxes_positions(self, rv: Sequence[int]):
        self._boxes_positions = rv or []

    @property
    def zobrist_hash(self) -> int:
        return self._zobrist_hash

    @zobrist_hash.setter
    def zobrist_hash(self, rv: int):
        self._zobrist_hash = rv or self.UNKNOWN_ZOBRIST_HASH

    def __str__(self) -> str:
        prefix = (len(self.__class__.__name__) + 2) * " "
        return "\n".join(
            [
                "<{} pushers_positions: {},".format(
                    self.__class__.__name__, self.pushers_positions
                ),
                prefix + "boxes_positions: {},".format(self.boxes_positions),
                prefix + "zobrist_hash: {}".format(self.zobrist_hash) + ">",
            ]
        )

    def __repr__(self) -> str:
        return "{}(pushers_positions={}, boxes_positions={}, zobrist_hash={})".format(
            self.__class__.__name__,
            repr(self.pushers_positions),
            repr(self.boxes_positions),
            repr(self.zobrist_hash),
        )

    def __eq__(self, other) -> bool:
        return (
            self.zobrist_hash is not None
            and self.zobrist_hash is not self.UNKNOWN_ZOBRIST_HASH
            and self.zobrist_hash == other.zobrist_hash
        ) or (
            self.boxes_positions == other.boxes_positions
            and self.pushers_positions == other.pushers_positions
        )
