try:
    from sokoenginepyext import VariantBoard
except ImportError:
    from .variant_board import VariantBoard, VariantBoardResizer
