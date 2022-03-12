from __future__ import annotations

from enum import Enum
from typing import Union

from .. import utilities
from .hexoban_tessellation import HexobanTessellation
from .octoban_tessellation import OctobanTessellation
from .sokoban_tessellation import SokobanTessellation
from .trioban_tessellation import TriobanTessellation

TessellationOrDescription = Union[
    HexobanTessellation,
    OctobanTessellation,
    SokobanTessellation,
    TriobanTessellation,
    str,
]

AnyTessellation = Union[
    HexobanTessellation, OctobanTessellation, SokobanTessellation, TriobanTessellation
]


class Tessellation(Enum):
    """
    Enumerates all supported tessellations and provides factory method for them.
    """

    SOKOBAN = SokobanTessellation()
    TRIOBAN = TriobanTessellation()
    HEXOBAN = HexobanTessellation()
    OCTOBAN = OctobanTessellation()

    def __str__(self):
        return self.name.title()

    def __repr__(self):
        return "Tessellation." + self.name

    @classmethod
    def instance_from(
        cls, tessellation_or_description: TessellationOrDescription
    ) -> AnyTessellation:
        """
        Given a sokoban variant name (ie. "sokoban") produces tessellation object for
        that variant.
        """

        if (
            not tessellation_or_description
            or "sokoban" in str(tessellation_or_description).lower()
            or utilities.is_blank(str(tessellation_or_description))
        ):
            return cls.SOKOBAN.value
        elif "trioban" in str(tessellation_or_description).lower():
            return cls.TRIOBAN.value
        elif "hexoban" in str(tessellation_or_description).lower():
            return cls.HEXOBAN.value
        elif "octoban" in str(tessellation_or_description).lower():
            return cls.OCTOBAN.value
        else:
            raise ValueError(tessellation_or_description)
