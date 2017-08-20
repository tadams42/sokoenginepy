try:
    from libsokoengine import BoardCell
except ImportError:
    from .board_cell import BoardCell

from .board_cell import (BoardCellCharacters, BoardConversionError,
                         IllegalBoardCharacterError)
