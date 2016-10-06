from ..common import UnknownVariantError, Variant


def board_factory(
    board_width=0, board_height=0, variant=Variant.SOKOBAN, board_str=""
):
    from .variant_board import VariantBoard
    from .hexoban_board import HexobanBoard
    from .octoban_board import OctobanBoard
    from .sokoban_board import SokobanBoard
    from .trioban_board import TriobanBoard

    variant = Variant.factory(variant)

    for klass in VariantBoard.__subclasses__():
        if variant.name.lower() in klass.__name__.lower():
            return klass(board_width, board_height, board_str)

    raise UnknownVariantError(variant)


_TESSELLATIONS = dict()


def tessellation_factory(variant=Variant.SOKOBAN):
    from .tessellation import Tessellation
    from .hexoban_tessellation import HexobanTessellation
    from .octoban_tessellation import OctobanTessellation
    from .sokoban_tessellation import SokobanTessellation
    from .trioban_tessellation import TriobanTessellation

    variant = Variant.factory(variant)

    for klass in Tessellation.__subclasses__():
        if variant.name.lower() in klass.__name__.lower():
            if variant not in _TESSELLATIONS.keys():
                _TESSELLATIONS[variant] = klass()
            return _TESSELLATIONS[variant]

    raise UnknownVariantError(variant)
