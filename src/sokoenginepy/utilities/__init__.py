from .coordinate_helpers import (COLUMN, ROW, X, Y, index_1d, is_on_board_1d,
                                 is_on_board_2d)
from .dict_helpers import except_keys, inverted
from .docstring_inheritance import InheritableDocstrings
from .flip_dict import Flipdict
from .helpers import RESOURCES_ROOT, first_index_of, last_index_of, utcnow
from .rle import RleCharacters, rle_decode, rle_encode
from .text_utils import (calculate_width, contains_only_digits_and_spaces,
                         drop_blank, drop_empty, ending_digits, is_blank,
                         normalize_width)


class SokoengineError(RuntimeError):
    """
    Base class for all sokoenginepy exceptions.
    """
    pass
