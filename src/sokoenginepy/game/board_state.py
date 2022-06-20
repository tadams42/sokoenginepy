from dataclasses import dataclass, field
from typing import ClassVar, List


@dataclass
class BoardState:
    """
    Sample of board state.

    See Also:
        - `.BoardManager`
        - `.HashedBoardManager`
    """

    #: Integer used for situations where board hash has not been calculated.
    NO_HASH: ClassVar[int] = 0

    #: Zobrist hash of state.
    #:
    #: See Also:
    #:     `.HashedBoardManager`
    zobrist_hash: int = NO_HASH

    #: Positions of pushers sorted by pusher ID.
    pushers_positions: List[int] = field(default_factory=list)

    #: Positions of boxes sorted by box ID.
    boxes_positions: List[int] = field(default_factory=list)
