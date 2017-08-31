try:
    from sokoenginepyext import (BoardCell, BoardConversionError,
                                 IllegalBoardCharacterError)
except ImportError:
    from .board_cell import (BoardCell, BoardConversionError,
                             IllegalBoardCharacterError)

from .board_cell import BoardCellCharacters
