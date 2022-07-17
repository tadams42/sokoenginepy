from __future__ import annotations

from typing import Final


class Config:
    """
    Various constants used across game package. Since they are needed by many modules
    it made more sense to place them here in their own class, than into one or more
    other classes.
    """

    #: Max board width
    MAX_WIDTH: Final[int] = 4096

    #: Max board height
    MAX_HEIGHT: Final[int] = 4096

    #: Invalid board position
    NO_POS: Final[int] = -1

    #: Default ID for pieces for situations whe one is needed and **must** be provided.
    #:
    #: See Also:
    #:     - :class:`.BoardManager`
    #:     - :class:`.PusherStep`
    DEFAULT_ID: Final[int] = 1

    #: Invalid, non-existing ID of a piece. It is used in situations where it would
    #: be OK to use `None`, but this is more specific and has same type as piece IDs
    #: have.
    #:
    #: See Also:
    #:     - :class:`.BoardManager`
    #:     - :class:`.PusherStep`
    NO_ID: Final[int] = -1
