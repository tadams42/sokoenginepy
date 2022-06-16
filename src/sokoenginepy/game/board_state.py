from typing import Final, List, Optional


class BoardState:
    """
    Sample of board state.
    """

    #: Integer used for situations where board has has not been calculated.
    NO_HASH: Final[int] = 0

    def __init__(
        self,
        pushers_positions: Optional[List[int]] = None,
        boxes_positions: Optional[List[int]] = None,
        zobrist_hash: int = NO_HASH,
    ):
        self.pushers_positions = pushers_positions or []
        self.boxes_positions = boxes_positions or []
        self.zobrist_hash = zobrist_hash or self.NO_HASH

    @property
    def pushers_positions(self) -> List[int]:
        """
        Positions of pushers sorted by pusher ID.
        """
        return self._pushers_positions

    @pushers_positions.setter
    def pushers_positions(self, rv: List[int]):
        self._pushers_positions = rv or []

    @property
    def boxes_positions(self) -> List[int]:
        """
        Positions of boxes sorted by box ID.
        """
        return self._boxes_positions

    @boxes_positions.setter
    def boxes_positions(self, rv: List[int]):
        self._boxes_positions = rv or []

    @property
    def zobrist_hash(self) -> int:
        """
        Zobrist hash of state (see `.HashedBoardManager`)
        """
        return self._zobrist_hash

    @zobrist_hash.setter
    def zobrist_hash(self, rv: int):
        self._zobrist_hash = rv or self.NO_HASH

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
            and self.zobrist_hash is not self.NO_HASH
            and self.zobrist_hash == other.zobrist_hash
        ) or (
            self.boxes_positions == other.boxes_positions
            and self.pushers_positions == other.pushers_positions
        )
