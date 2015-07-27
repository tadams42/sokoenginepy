from ..core import (
    PrettyPrintable, EqualityComparable, TessellationType, INDEX
)
from ..game import BoardCell
from ..io import OutputSettings, rle_encode, is_blank, parse_board_string,\
    RleCharacters

from .board_graph import BoardGraph


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
                    self[INDEX(x, y, self.width)] = BoardCell(chr)
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

    def to_s(self, output_settings = OutputSettings()):
        """
        Override this in subclass to handle tessellation speciffic strings
        """
        rows = []
        for y in range(0, self.height):
            row = "".join([
                cell.to_s(output_settings.use_visible_floors)
                for cell in [
                    self._graph.node[INDEX(x, y, self.width)]['cell']
                    for x in range(0, self.width)
                ]
            ])
            if output_settings.rle_encode:
                row = rle_encode(row)
            rows.append(row)

        if output_settings.rle_encode:
            return RleCharacters.RLE_ROW_SEPARATOR.value.join(rows)
        else:
            return "\n".join(rows)

    def _debug_draw_positions(self, positions):
        tmp = self._graph.copy()
        for vertice in positions:
            self[vertice] = BoardCell('@')
        print(self.to_s(OutputSettings(use_visible_floors=True)))
        self._graph = tmp

    def add_row_top(self):
        old_body = self._graph
        old_height = self.height

        self._reinit(self.width, self.height + 1)

        for x in range(0, self.width):
            for y in range(0, old_height):
                self._graph.node[INDEX(x, y + 1, self.width)]['cell'] =\
                    old_body.node[INDEX(x, y, self.width)]['cell']

    def add_row_bottom(self):
        old_body = self._graph
        old_height = self.height

        self._reinit(self.width, self.height + 1)

        for x in range(0, self.width):
            for y in range(0, old_height):
                self._graph.node[INDEX(x, y, self.width)]['cell'] =\
                    old_body.node[INDEX(x, y, self.width)]['cell']

    def add_column_left(self):
        old_body = self._graph
        old_width = self.width

        self._reinit(self.width + 1, self.height)

        for x in range(0, old_width):
            for y in range(0, self.height):
                self._graph.node[INDEX(x + 1, y, self.width)]['cell'] =\
                    old_body.node[INDEX(x, y, old_width)]['cell']

    def add_column_right(self):
        old_body = self._graph
        old_width = self.width

        self._reinit(self.width + 1, self.height)

        for x in range(0, old_width):
            for y in range(0, self.height):
                self._graph.node[INDEX(x, y, self.width)]['cell'] =\
                    old_body.node[INDEX(x, y, old_width)]['cell']

    def remove_row_top(self):
        old_body = self._graph

        self._reinit(self.width, self.height - 1)

        for x in range(0, self.width):
            for y in range(0, self.height):
                self._graph.node[INDEX(x, y, self.width)]['cell'] =\
                    old_body.node[INDEX(x, y + 1, self.width)]['cell']

    def remove_row_bottom(self):
        old_body = self._graph

        self._reinit(self.width, self.height - 1)

        for x in range(0, self.width):
            for y in range(0, self.height):
                self._graph.node[INDEX(x, y, self.width)]['cell'] =\
                    old_body.node[INDEX(x, y, self.width)]['cell']

    def remove_column_left(self):
        old_body = self._graph
        old_width = self.width

        self._reinit(self.width - 1, self.height)

        for x in range(0, self.width):
            for y in range(0, self.height):
                self._graph.node[INDEX(x, y, self.width)]['cell'] =\
                    old_body.node[INDEX(x + 1, y, old_width)]['cell']

    def remove_column_right(self):
        old_body = self._graph
        old_width = self.width

        self._reinit(self.width - 1, self.height)

        for x in range(0, self.width):
            for y in range(0, self.height):
                self._graph.node[INDEX(x, y, self.width)]['cell'] =\
                    old_body.node[INDEX(x, y, old_width)]['cell']

    def resize(self, new_width, new_height):
        if new_height != self.height:
            if new_height > self.height:
                amount = new_height - self.height
                for i in range(0, amount):
                    self.add_row_bottom()
            else:
                amount = self.height - new_height
                for i in range(0, amount):
                    self.remove_row_bottom()

        if new_width != self.width:
            if new_width > self.width:
                amount = new_width - self.width
                for i in range(0, amount):
                    self.add_column_right()
            else:
                amount = self.width - new_width
                for i in range(0, amount):
                    self.remove_column_right()

    def trim(self):
        self.trim_top()
        self.trim_bottom()
        self.trim_left()
        self.trim_right()

    def trim_left(self):
        amount = self.width
        for y in range(0, self.height):
            border_found = False
            for x in range(0, self.width):
                border_found = self[INDEX(x, y, self.width)].is_border_element
                if border_found:
                    if x < amount:
                        amount = x
                    break

        for i in range(0, amount):
            self.remove_column_left()

    def trim_right(self):
        self.reverse_columns()
        self.trim_left()
        self.reverse_columns()

    def trim_top(self):
        amount = self.height
        for x in range(0, self.width):
            border_found = False
            for y in range(0, self.height):
                border_found = self[INDEX(x, y, self.width)].is_border_element
                if border_found:
                    if y < amount:
                        amount = y
                    break

        for i in range(0, amount):
            self.remove_row_top()

    def trim_bottom(self):
        self.reverse_rows()
        self.trim_top()
        self.reverse_rows()

    def reverse_rows(self):
        old_body = self._graph

        self._reinit(self.width, self.height)

        for x in range(0, self.width):
            for y in range(0, self.height):
                self[INDEX(x, y, self.width)] = \
                    old_body.node[INDEX(x, self.height - y - 1, self.width)]['cell']

    def reverse_columns(self):
        old_body = self._graph

        self._reinit(self.width, self.height)

        for x in range(0, self.width):
            for y in range(0, self.height):
                self[INDEX(x, y, self.width)] = \
                    old_body.node[INDEX(self.width - x - 1, y, self.width)]['cell']
