from __future__ import annotations

import enum


class GraphType(enum.Enum):
    """
    Types of `BoardGraph`.
    """

    #: Directed graphs
    DIRECTED = 0

    #: Directed graphs with self loops and parallel edges
    DIRECTED_MULTI = 1
