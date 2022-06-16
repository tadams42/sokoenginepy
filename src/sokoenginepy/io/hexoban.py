from __future__ import annotations

from typing import List, Optional, Tuple

from .puzzle import Puzzle
from .puzzle_parsing import PuzzleParser, PuzzlePrinter, PuzzleResizer
from .rle import Rle
from .snapshot import Snapshot


class HexobanSnapshot(Snapshot):
    def __init__(self, moves_data: str = ""):
        from ..game import Tessellation

        super().__init__(tessellation=Tessellation.HEXOBAN, moves_data=moves_data)


class HexobanPuzzle(Puzzle):
    def __init__(self, width: int = 0, height: int = 0, board: Optional[str] = None):
        """
        Arguments:
            width: number of columns
            height: number of rows
            board: If not blank, it will be parsed and board will be created from it,
                ignoring ``width`` and ``height``.
        """
        from ..game import Tessellation

        super().__init__(
            tessellation=Tessellation.HEXOBAN,
            width=width,
            height=height,
            board=board,
            resizer_cls=HexobanPuzzleResizer,
            parser_cls=HexobanPuzzleParser,
            printer_cls=HexobanPuzzlePrinter,
        )


class HexobanTextConverter:
    def convert_to_string(
        self,
        parsed_board: List[str],
        width: int,
        height: int,
        use_visible_floor: bool,
    ) -> str:
        from ..game import index_1d

        floor = Puzzle.VISIBLE_FLOOR if use_visible_floor else Puzzle.FLOOR

        retv: List[str] = []
        for row in range(0, height):
            line = ""
            if row % 2 == 1:
                # beginning half hex for odd rows
                line += floor

            for col in range(0, width):
                puzzle_char = parsed_board[index_1d(col, row, width)]

                line += floor
                if Puzzle.is_empty_floor(puzzle_char):
                    line += floor
                else:
                    line += puzzle_char

            retv.append(line)

        retv = PuzzleParser.normalize_width(retv, floor)
        if self.is_type1(retv):
            retv = self.remove_column_right(retv)

        return "\n".join(retv)

    def is_type1(self, strings: List[str]) -> bool:
        from ..game import Y

        rmnf = self._find_rightmost_non_floor(strings)

        if rmnf is None:
            return False
        elif rmnf > 0:
            y = Y(rmnf, PuzzleParser.calculate_width(strings))
            return y % 2 == 0
        else:  # rmnf == 0
            return True

    @staticmethod
    def _find_rightmost_non_floor(strings: List[str]) -> Optional[int]:
        from ..game import X, Y, index_1d

        def rightmost_finder(strings: List[str], row_parity: int):
            cell_found = False
            height = len(strings)
            width = len(strings[0])
            x = y = 0

            for row in range(row_parity % 2, height, 2):
                for col in range(0, width):
                    if not Puzzle.is_empty_floor(strings[row][col]):
                        cell_found = True
                        if col > x or (col >= x and row > y):
                            x = col
                            y = row

            if cell_found:
                return index_1d(x, y, width)

            return None

        normalized = HexobanPuzzleParser.normalize_width(strings)
        width = len(normalized[0]) if normalized else 0
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

    def convert_to_internal(self, board: str) -> Tuple[List[str], bool]:
        # Converts textual Hexoban into 2D array and validates textual layout
        (
            parsed,
            width,
            height,
            even_row_x_parity,
            odd_row_x_parity,
        ) = self._preparse_board(board)

        # Handle empty board
        if width == 0 or height == 0:
            return [], True

        elif even_row_x_parity < 0 or odd_row_x_parity < 0:
            internal = height * [int(width / 2) * Puzzle.VISIBLE_FLOOR]
            return internal, True

        layout_ok = True
        internal: List[str] = []

        for y in range(0, height):
            if not layout_ok:
                break
            internal_line = ""
            for x in range(0, width):
                if not layout_ok:
                    break

                layout_ok, should_copy_cell = self._analyze_text_cell_position(
                    parsed[y][x], x, y, odd_row_x_parity, even_row_x_parity
                )

                if layout_ok and should_copy_cell:
                    internal_line += parsed[y][x]

            if layout_ok:
                internal.append(internal_line)

        if layout_ok:
            internal = PuzzleParser.normalize_width(internal, Puzzle.VISIBLE_FLOOR)

        return internal, layout_ok

    def _is_type2(self, strings: List[str]) -> bool:
        return not self.is_type1(strings)

    @staticmethod
    def _analyze_text_cell_position(
        cell: str, x: int, y: int, odd_row_x_parity: int, even_row_x_parity: int
    ) -> Tuple[bool, bool]:
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
                layout_ok = Puzzle.is_empty_floor(cell)
                is_cell_for_layout = True
        else:  # odd rows
            if x == 0:  # row start half hexes are always layout cells
                layout_ok = Puzzle.is_empty_floor(cell)
                is_cell_for_layout = True
            else:
                if x_parity == odd_row_x_parity:
                    is_cell_for_layout = False
                else:  # Cell is part of layout, it must be empty
                    layout_ok = Puzzle.is_empty_floor(cell)
                    is_cell_for_layout = True

        should_copy_cell = layout_ok and not is_cell_for_layout

        return layout_ok, should_copy_cell

    def _preparse_board(self, board: str) -> Tuple[List[str], int, int, int, int]:
        from ..game import X, Y

        parsed: List[str] = PuzzleParser.cleaned_board_lines(board)
        width = len(parsed[0]) if parsed else 0
        height = len(parsed)

        even_row_x_parity = odd_row_x_parity = -1

        if height != 0 and width != 0:
            # Compensate for scheme2
            has_non_floor_left_in_odd_row = False

            for i in range(0, height):
                if has_non_floor_left_in_odd_row:
                    break
                has_non_floor_left_in_odd_row = has_non_floor_left_in_odd_row or (
                    i % 2 == 1 and not Puzzle.is_empty_floor(parsed[i][0])
                )

            if has_non_floor_left_in_odd_row:
                parsed = self.add_column_left(parsed)
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

        return parsed, width, height, even_row_x_parity, odd_row_x_parity

    @staticmethod
    def add_column_left(strings: List[str]) -> List[str]:
        return [Puzzle.VISIBLE_FLOOR + line for line in strings]

    @staticmethod
    def add_column_right(strings: List[str]) -> List[str]:
        return [line + Puzzle.VISIBLE_FLOOR for line in strings]

    @staticmethod
    def add_row_top(strings: List[str]) -> List[str]:
        w = HexobanPuzzleParser.calculate_width(strings)
        return [w * Puzzle.VISIBLE_FLOOR] + strings

    @staticmethod
    def remove_column_right(strings: List[str]) -> List[str]:
        return [line[:-1] for line in strings]

    @staticmethod
    def reverse_columns(strings: List[str]) -> List[str]:
        return ["".join(c for c in reversed(line)) for line in strings]

    @staticmethod
    def remove_row_top(strings: List[str]) -> List[str]:
        return strings[1:]

    @staticmethod
    def remove_row_bottom(strings: List[str]) -> List[str]:
        return strings[:-1]

    @staticmethod
    def _find_first_non_floor(strings: List[str]):
        from ..game import index_1d

        normalized = HexobanPuzzleParser.normalize_width(strings)
        width = len(normalized[0]) if normalized else 0
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

                if not Puzzle.is_empty_floor(normalized[row][column]) and (
                    column > x or row > y
                ):
                    x = column
                    y = row
                    non_floor_found = True

        if non_floor_found:
            return index_1d(x, y, width)

        # Empty board, assuming scheme1
        return index_1d(1, 0, width)


class HexobanPuzzlePrinter(PuzzlePrinter):
    def print(
        self,
        parsed_board: List[str],
        width: int,
        height: int,
        use_visible_floor: bool,
        rle_encode: bool,
    ) -> str:
        retv = HexobanTextConverter().convert_to_string(
            parsed_board, width, height, use_visible_floor
        )
        if rle_encode:
            return Rle.encode(retv)
        return retv


class HexobanPuzzleParser(PuzzleParser):
    def parse(self, board: str) -> List[str]:
        parsed, layout_ok = HexobanTextConverter().convert_to_internal(board)

        if layout_ok:
            return parsed

        raise ValueError(
            "String can't be parsed to HexobanPuzzle. Probable cause is invalid "
            "text layout meaning either missing or misaligned filler floor "
            "characters."
        )


class HexobanPuzzleResizer(PuzzleResizer):
    def reverse_columns(
        self, parsed_board: List[str], width: int, height: int
    ) -> Tuple[List[str], int, int]:
        converter = HexobanTextConverter()

        printed_board = converter.convert_to_string(
            parsed_board, width, height, True
        ).splitlines()

        if converter.is_type1(printed_board):
            printed_board = converter.add_column_left(printed_board)
        else:
            printed_board = converter.add_column_right(printed_board)

        printed_board = converter.reverse_columns(printed_board)
        printed_board = converter.remove_column_right(printed_board)

        new_parsed_board, layout_ok = converter.convert_to_internal(
            "\n".join(printed_board)
        )
        new_width = len(new_parsed_board[0]) if new_parsed_board else 0
        new_height = len(new_parsed_board)

        return list("".join(new_parsed_board)), new_width, new_height

    def add_row_top(
        self, parsed_board: List[str], width: int, height: int
    ) -> Tuple[List[str], int, int]:
        converter = HexobanTextConverter()

        printed_board = converter.convert_to_string(
            parsed_board, width, height, True
        ).splitlines()

        printed_board = converter.add_row_top(printed_board)

        new_parsed_board, layout_ok = converter.convert_to_internal(
            "\n".join(printed_board)
        )
        new_width = len(new_parsed_board[0]) if new_parsed_board else 0
        new_height = len(new_parsed_board)

        return list("".join(new_parsed_board)), new_width, new_height

    def remove_row_top(
        self, parsed_board: List[str], width: int, height: int
    ) -> Tuple[List[str], int, int]:
        converter = HexobanTextConverter()

        printed_board = converter.convert_to_string(
            parsed_board, width, height, True
        ).splitlines()

        printed_board = converter.remove_row_top(printed_board)

        new_parsed_board, layout_ok = converter.convert_to_internal(
            "\n".join(printed_board)
        )
        new_width = len(new_parsed_board[0]) if new_parsed_board else 0
        new_height = len(new_parsed_board)

        return list("".join(new_parsed_board)), new_width, new_height

    def remove_row_bottom(
        self, parsed_board: List[str], width: int, height: int
    ) -> Tuple[List[str], int, int]:
        converter = HexobanTextConverter()

        printed_board = converter.convert_to_string(
            parsed_board, width, height, True
        ).splitlines()

        printed_board = converter.remove_row_bottom(printed_board)

        new_parsed_board, layout_ok = converter.convert_to_internal(
            "\n".join(printed_board)
        )
        new_width = len(new_parsed_board[0]) if new_parsed_board else 0
        new_height = len(new_parsed_board)

        return list("".join(new_parsed_board)), new_width, new_height
