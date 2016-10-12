from ..board import (BoardConversionError, BoardEncodingCharacters,
                     is_empty_floor, parse_board_string)
from ..common import (RleCharacters, Variant, calculate_width, normalize_width,
                      rle_encode)
from ..input_output import OutputSettings
from .sokoban_board import SokobanBoard
from .tessellation import X, Y, index_1d
from .variant_board import VariantBoard, VariantBoardResizer


class HexobanBoard(VariantBoard):
    """Implements :class:`.VariantBoard` for Hexoban variant."""

    def __init__(self, board_width=0, board_height=0, board_str=""):
        super().__init__(
            board_width=board_width,
            board_height=board_height,
            variant=Variant.HEXOBAN,
            board_str=board_str
        )

    @property
    def _resizer_class(self):
        return HexobanBoardResizer

    def _parse_string(self, board_str):
        parsed, layout_ok = HexobanTextConverter(
        ).convert_to_internal(board_str)

        if layout_ok:
            return parsed
        else:
            raise BoardConversionError(BoardConversionError.INVALID_LAYOUT)

    def to_s(self, output_settings=OutputSettings()):
        return HexobanTextConverter().convert_to_string(self, output_settings)


class HexobanBoardResizer(VariantBoardResizer):

    def __init__(self, hexoban_board):
        super().__init__(hexoban_board)

    def reverse_columns(self, reconfigure_edges):
        converter = HexobanTextConverter()
        tmp = SokobanBoard(board_str=converter.convert_to_string(self.board))

        if converter.is_type1(self.board):
            tmp._resizer.add_column_left(reconfigure_edges=False)
        else:
            tmp._resizer.add_column_right(reconfigure_edges=False)

        tmp._resizer.reverse_columns(reconfigure_edges=False)
        tmp._resizer.remove_column_right(reconfigure_edges=False)

        self.board._reinit_with_string(tmp.to_s(), reconfigure_edges)

    def add_row_top(self, reconfigure_edges):
        converter = HexobanTextConverter()
        tmp = SokobanBoard(board_str=converter.convert_to_string(self.board))
        tmp._resizer.add_row_top(reconfigure_edges=False)
        self.board._reinit_with_string(tmp.to_s(), reconfigure_edges)

    def remove_row_top(self, reconfigure_edges):
        converter = HexobanTextConverter()
        tmp = SokobanBoard(board_str=converter.convert_to_string(self.board))
        tmp._resizer.remove_row_top(reconfigure_edges=False)
        self.board._reinit_with_string(tmp.to_s(), reconfigure_edges)

    def remove_row_bottom(self, reconfigure_edges):
        converter = HexobanTextConverter()
        tmp = SokobanBoard(board_str=converter.convert_to_string(self.board))
        tmp._resizer.remove_row_bottom(reconfigure_edges=False)
        self.board._reinit_with_string(tmp.to_s(), reconfigure_edges)


class HexobanTextConverter:

    def __init__(self, output_settings=OutputSettings()):
        self.output_settings = output_settings

    def _debug_print(self, input, expected):
        print(
            "{0:<30}{1:<30}{2:<30}{3:<30}".
            format("input", "expected", "converted", "internal")
        )

        input_lines = input.splitlines()
        expected_lines = expected.splitlines()
        converted_lines = HexobanBoard(board_str=input).to_s(
            output_settings=OutputSettings(use_visible_floors=True)
        ).splitlines()
        internal_lines = self.convert_to_internal(input)[0]

        for i in range(0, len(internal_lines)):
            print(
                "{0:<30}{1:<30}{2:<30}{3:<30}".format(
                    input_lines[i], expected_lines[i], converted_lines[i],
                    internal_lines[i]
                )
            )

    def convert_to_internal(self, src_str):
        # Converts textual Hexoban into 2D array and validates textual layout

        parsed, width, height, even_row_x_parity, odd_row_x_parity = \
            self._preparse_board(src_str)

        # Handle empty board
        if width == 0 or height == 0:
            return [], True
        elif even_row_x_parity < 0 or odd_row_x_parity < 0:
            internal = height * [
                int(width / 2) * BoardEncodingCharacters.VISIBLE_FLOOR.value +
                '\n'
            ]
            return internal, True

        layout_ok = True
        internal = []

        for y in range(0, height):
            if not layout_ok:
                break
            internal_line = []
            for x in range(0, width):
                if not layout_ok:
                    break

                layout_ok, should_copy_cell = self._analyze_text_cell_position(
                    (parsed[y][x],
                     x,
                     y,
                     odd_row_x_parity,
                     even_row_x_parity,)
                )

                if layout_ok and should_copy_cell:
                    internal_line.append(parsed[y][x])

            if layout_ok:
                internal.append(''.join(internal_line))

        if layout_ok:
            internal = normalize_width(internal)

        return internal, layout_ok

    def convert_to_string(
        self, hexoban_board, output_settings=OutputSettings()
    ):
        self.output_settings = output_settings

        retv = []
        for row in range(0, hexoban_board.height):
            line = []
            if row % 2 == 1:
                # beginning half hex for odd rows
                line.append(self.floor_character)

            for col in range(0, hexoban_board.width):
                line.append(self.floor_character)
                line.append(
                    hexoban_board[index_1d(col, row, hexoban_board.width)]
                    .to_s(self.output_settings.use_visible_floors)
                )

            retv.append("".join(line))

        retv = normalize_width(retv, self.floor_character)
        if self._is_type1(retv):
            retv = self._remove_column_right(retv)

        if output_settings.rle_encode:
            return RleCharacters.RLE_ROW_SEPARATOR.value.join(
                rle_encode(line) for line in retv
            )
        else:
            return "\n".join(retv)

    def is_type1(self, hexoban_board):
        return self._is_type1(parse_board_string(hexoban_board.to_s()))

    def _is_type1(self, string_list):
        rnfp = self._find_rightmost_non_floor(string_list)
        if (rnfp > 0):
            y = Y(rnfp, calculate_width(string_list))
            return y % 2 == 0
        elif (rnfp == 0):
            return True
        return False

    def _is_type2(self, string_list):
        return not self._is_type1(string_list)

    def _analyze_text_cell_position(self, position_data):
        cell, x, y, odd_row_x_parity, even_row_x_parity = position_data

        y_parity = y % 2
        x_parity = x % 2

        layout_ok = True
        # Is current cell part of board or only part of textual layout?
        is_cell_for_layout = False
        should_copy_cell = False

        # Check if textual encoding (layout) is legal. Positions of all
        # board elements in textual layout depend on position of first
        # non floor element. If that element is (odd column, even row)
        # than all other element in even rows must be in odd columns.
        # Other cells in even rows must be empty cells and their purpose
        # is to define board textual layout (they are not board elements).
        if y_parity == 0:  # even rows
            if x_parity == even_row_x_parity:
                is_cell_for_layout = False
            else:  # Cell is part of layout, it must be empty
                layout_ok = is_empty_floor(cell)
                is_cell_for_layout = True
        else:  # odd rows
            if x == 0:  # row start half hexes are always layout cells
                layout_ok = is_empty_floor(cell)
                is_cell_for_layout = True
            else:
                if x_parity == odd_row_x_parity:
                    is_cell_for_layout = False
                else:  # Cell is part of layout, it must be empty
                    layout_ok = is_empty_floor(cell)
                    is_cell_for_layout = True

        should_copy_cell = layout_ok and not is_cell_for_layout

        return (layout_ok,
                should_copy_cell,)

    def _preparse_board(self, board_string):
        parsed = []

        parsed = normalize_width(parse_board_string(board_string))
        width = len(parsed[0]) if len(parsed) > 0 else 0
        height = len(parsed)

        even_row_x_parity = odd_row_x_parity = -1

        if height != 0 and width != 0:
            # Compensate for scheme2
            has_non_floor_left_in_odd_row = False

            for i in range(0, height):
                if has_non_floor_left_in_odd_row:
                    break
                has_non_floor_left_in_odd_row = (
                    has_non_floor_left_in_odd_row or
                    (i % 2 == 1 and not is_empty_floor(parsed[i][0]))
                )

            if has_non_floor_left_in_odd_row:
                parsed = self._add_column_left(parsed)
                width += 1

            # Calculate parities
            first_cell = self._find_first_non_floor(parsed)
            if first_cell is not None:
                first_cell_x_parity = X(first_cell, width) % 2
                first_cell_y_parity = Y(first_cell, width) % 2

                if first_cell_y_parity == 0:
                    even_row_x_parity = first_cell_x_parity
                else:
                    even_row_x_parity = (first_cell_x_parity + 1) % 2

                odd_row_x_parity = (even_row_x_parity + 1) % 2

        return (parsed,
                width,
                height,
                even_row_x_parity,
                odd_row_x_parity,)

    @property
    def floor_character(self):
        return (
            BoardEncodingCharacters.VISIBLE_FLOOR.value
            if self.output_settings.use_visible_floors else
            BoardEncodingCharacters.FLOOR.value
        )

    def _add_column_left(self, string_list):
        return [self.floor_character + line for line in string_list]

    def _add_column_right(self, string_list):
        return [line + self.floor_character for line in string_list]

    def _remove_column_right(self, string_list):
        return [line[:-1] for line in string_list]

    def _find_first_non_floor(self, string_list):
        normalized = normalize_width(string_list)
        width = len(normalized[0]) if len(normalized) > 0 else 0
        height = len(normalized)

        if width == 0 or height == 0:
            return None

        x = y = 0
        non_floor_found = False

        for row in range(0, height):
            if non_floor_found:
                break
            for column in range(0, width):
                if non_floor_found:
                    break

                if (not is_empty_floor(normalized[row][column]) and (column > x or row > y)):
                    x = column
                    y = row
                    non_floor_found = True

        if non_floor_found:
            return index_1d(x, y, width)

        # Empty board, assuming scheme1
        return index_1d(1, 0, width)

    def _find_rightmost_non_floor(self, string_list):

        def rightmost_finder(string_list, row_parity):
            cell_found = False
            height = len(string_list)
            width = len(string_list[0])
            x = y = 0

            for row in range(row_parity % 2, height, 2):
                for col in range(0, width):
                    if not is_empty_floor(string_list[row][col]):
                        cell_found = True
                        if col > x or (col >= x and row > y):
                            x = col
                            y = row

            if cell_found:
                return index_1d(x, y, width)

            return None

        normalized = normalize_width(string_list)
        width = len(normalized[0]) if len(normalized) > 0 else 0
        height = len(normalized)

        if width == 0 or height == 0:
            return None

        rightmost_in_even_rows = rightmost_finder(normalized, 0)
        rightmost_in_odd_rows = rightmost_finder(normalized, 1)

        if rightmost_in_even_rows is None or rightmost_in_odd_rows is None:
            return index_1d(0, 0, width)

        odd_x = X(rightmost_in_odd_rows, width)
        odd_y = Y(rightmost_in_odd_rows, width)
        even_x = X(rightmost_in_even_rows, width)
        even_y = Y(rightmost_in_even_rows, width)

        if odd_x > even_x:
            return rightmost_in_odd_rows
        elif even_x > odd_x:
            return rightmost_in_even_rows

        return rightmost_in_odd_rows if odd_y > even_y else rightmost_in_even_rows
