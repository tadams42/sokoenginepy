from ..core.helpers import PrettyPrintable, EqualityComparable
from ..core.board_cell import BoardCell
from .tessellation import TessellationType, INDEX
from .board_graph import BoardGraph
from ..io.output_settings import OutuputSettings
from ..io.text_utils import rle_encode, is_blank, parse_board_string


class VariantBoard(PrettyPrintable, EqualityComparable, BoardGraph):
    """
    Base board class for variant specific implementations.
    Implements concerns of
        - direct board editing
        - string (de)serialization
        - resizing

    All positions are int indexes of graph vertices. To convert 2D coordinate
    into vertice index, use INDEX method
    """

    def __init__(
        self, board_width=0, board_height=0,
        tessellation_type = TessellationType.SOKOBAN,
        board_str = ""
    ):
        if not is_blank(board_str):
            board_cells = self._parse_string(board_str)
            width = len(board_cells[0]) if len(board_cells) > 0 else 0
            height = len(board_cells)
            super().__init__(
                board_width=width, board_height=height,
                tessellation_type=tessellation_type
            )
            for y, row in enumerate(board_cells):
                for x, chr in enumerate(row):
                    self[x, y] = BoardCell(chr)
        else:
            super().__init__(board_width, board_height, tessellation_type)

    def _representation_attributes(self):
        return {
            'tessellation': self.tessellation_type,
            'width': self.width,
            'height': self.height,
            'board': self.to_s,
        }

    def __eq__(self, other):
        if (
            self.tessellation_type == other.tessellation_type and
            self.width == other.width and
            self.height == other.height
        ):
            for vertice in range(0, self.size):
                if self[vertice] != other[vertice]:
                    return False
            return True
        else:
            return False

    def _parse_string(self, board_str):
        """
        Override this in subclass to handle tessellation speciffic strings
        Should return list of strings where each string represents all BoardCell
        in single line of game board.
        """
        return parse_board_string(board_str)

    def to_s(self, output_settings = OutuputSettings()):
        """
        Override this in subclass to handle tessellation speciffic strings
        """
        # TODO
        pass

    def add_row_top(self):
        # TODO
        pass

    def add_row_bottom(self):
        # TODO
        pass

    def add_column_left(self):
        # TODO
        pass

    def add_column_right(self):
        # TODO
        pass

    def remove_row_top(self):
        # TODO
        pass

    def remove_row_bottom(self):
        # TODO
        pass

    def remove_column_left(self):
        # TODO
        pass

    def remove_column_right(self):
        # TODO
        pass

    def resize(self, new_width, new_height):
        # TODO
        pass

    def trim(self):
        # TODO
        pass

    def trim_left(self):
        # TODO
        pass

    def trim_right(self):
        # TODO
        pass

    def trim_top(self):
        # TODO
        pass

    def trim_bottom(self):
        # TODO
        pass

    def reverse_rows(self):
        # TODO
        pass

    def reverse_columns(self):
        # TODO
        pass
