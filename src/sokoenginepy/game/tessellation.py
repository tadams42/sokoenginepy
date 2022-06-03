from __future__ import annotations

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..io import is_blank
    from .hexoban_tessellation import HexobanTessellation
    from .octoban_tessellation import OctobanTessellation
    from .sokoban_tessellation import SokobanTessellation
    from .trioban_tessellation import TriobanTessellation

else:
    try:
        from sokoenginepyext.game import (
            HexobanTessellation,
            OctobanTessellation,
            SokobanTessellation,
            TriobanTessellation,
        )
        from sokoenginepyext.io import is_blank
    except ImportError:
        from ..io import is_blank
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


class Tessellation:
    """
    Enumerates all supported tessellations and provides factory method for them.
    """

    SOKOBAN = SokobanTessellation()
    TRIOBAN = TriobanTessellation()
    HEXOBAN = HexobanTessellation()
    OCTOBAN = OctobanTessellation()

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
            or is_blank(str(tessellation_or_description))
        ):
            return cls.SOKOBAN
        elif "trioban" in str(tessellation_or_description).lower():
            return cls.TRIOBAN
        elif "hexoban" in str(tessellation_or_description).lower():
            return cls.HEXOBAN
        elif "octoban" in str(tessellation_or_description).lower():
            return cls.OCTOBAN
        else:
            raise ValueError(tessellation_or_description)
