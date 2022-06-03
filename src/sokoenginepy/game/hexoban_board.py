from __future__ import annotations

from typing import List, Optional, Tuple, Type

from ..io import Puzzle
from .board_cell import BoardCell
from .sokoban_board import SokobanBoard
from .utilities import X, Y, index_1d
from .variant_board import VariantBoard, VariantBoardResizer


class HexobanBoard(VariantBoard):
    def __init__(
        self,
        board_width: int = 0,
        board_height: int = 0,
        board_str: Optional[str] = None,
    ):
        super().__init__(
            tessellation_or_description="hexoban",
            board_width=board_width,
            board_height=board_height,
            board_str=board_str,
        )

    @property
    def _resizer_class(self) -> Type[HexobanBoardResizer]:
        return HexobanBoardResizer

    def _parse_string(self, board_str: str) -> List[str]:
        parsed, layout_ok = HexobanTextConverter().convert_to_internal(board_str)

        if layout_ok:
            return parsed
        else:
            raise ValueError(
                "String can't be converted to HexobanBoard. Probable because is invalid "
                "text layout meaning either missing or misaligned filler spaces."
            )

    def to_str(self, use_visible_floor: bool = False) -> str:
        return HexobanTextConverter().convert_to_string(self, use_visible_floor)


class HexobanBoardResizer(VariantBoardResizer):
    def __init__(self, hexoban_board: HexobanBoard):
        super().__init__(hexoban_board)

    def reverse_columns(self, reconfigure_edges: bool):
        converter = HexobanTextConverter()
        tmp = SokobanBoard(board_str=converter.convert_to_string(self.board))

        if converter.is_type1(self.board):
            tmp._resizer.add_column_left(reconfigure_edges=False)
        else:
            tmp._resizer.add_column_right(reconfigure_edges=False)

        tmp._resizer.reverse_columns(reconfigure_edges=False)
        tmp._resizer.remove_column_right(reconfigure_edges=False)

        self.board._reinit_with_string(str(tmp), reconfigure_edges)

    def add_row_top(self, reconfigure_edges: bool):
        converter = HexobanTextConverter()
        tmp = SokobanBoard(board_str=converter.convert_to_string(self.board))
        tmp._resizer.add_row_top(reconfigure_edges=False)
        self.board._reinit_with_string(str(tmp), reconfigure_edges)

    def remove_row_top(self, reconfigure_edges: bool):
        converter = HexobanTextConverter()
        tmp = SokobanBoard(board_str=converter.convert_to_string(self.board))
        tmp._resizer.remove_row_top(reconfigure_edges=False)
        self.board._reinit_with_string(str(tmp), reconfigure_edges)

    def remove_row_bottom(self, reconfigure_edges: bool):
        converter = HexobanTextConverter()
        tmp = SokobanBoard(board_str=converter.convert_to_string(self.board))
        tmp._resizer.remove_row_bottom(reconfigure_edges=False)
        self.board._reinit_with_string(str(tmp), reconfigure_edges)


class HexobanTextConverter:
    def convert_to_internal(self, src_str: str) -> Tuple[List[str], bool]:
        # Converts textual Hexoban into 2D array and validates textual layout
        (
            parsed,
            width,
            height,
            even_row_x_parity,
            odd_row_x_parity,
        ) = self._preparse_board(src_str)

        # Handle empty board
        if width == 0 or height == 0:
            return [], True
        elif even_row_x_parity < 0 or odd_row_x_parity < 0:
            internal = height * [int(width / 2) * BoardCell.VISIBLE_FLOOR + "\n"]
            return internal, True

        layout_ok = True
        internal: List[str] = []

        for y in range(0, height):
            if not layout_ok:
                break
            internal_line = []
            for x in range(0, width):
                if not layout_ok:
                    break

                layout_ok, should_copy_cell = self._analyze_text_cell_position(
                    parsed[y][x], x, y, odd_row_x_parity, even_row_x_parity
                )

                if layout_ok and should_copy_cell:
                    internal_line.append(parsed[y][x])

            if layout_ok:
                internal.append("".join(internal_line))

        if layout_ok:
            internal = HexobanBoard._normalize_width(internal)

        return internal, layout_ok

    def convert_to_string(
        self,
        hexoban_board: HexobanBoard,
        use_visible_floor: bool = False,
    ) -> str:
        floor_character = BoardCell(Puzzle.FLOOR).to_str(use_visible_floor)

        retv = []
        for row in range(0, hexoban_board.height):
            line = []
            if row % 2 == 1:
                # beginning half hex for odd rows
                line.append(floor_character)

            for col in range(0, hexoban_board.width):
                line.append(floor_character)
                line.append(
                    hexoban_board[index_1d(col, row, hexoban_board.width)].to_str(
                        use_visible_floor
                    )
                )

            retv.append("".join(line))

        retv = HexobanBoard._normalize_width(retv, floor_character)
        if self._is_type1(retv):
            retv = self._remove_column_right(retv)

        return "\n".join(retv)

    def is_type1(self, hexoban_board: HexobanBoard) -> bool:
        return self._is_type1(HexobanBoard._cleaned_board_lines(str(hexoban_board)))

    def _is_type1(self, string_list: List[str]) -> bool:
        rnfp = self._find_rightmost_non_floor(string_list)

        if rnfp is None:
            return False
        elif rnfp > 0:
            y = Y(rnfp, HexobanBoard._calculate_width(string_list))
            return y % 2 == 0
        else:  # rnfp == 0
            return True

    def _is_type2(self, string_list: List[str]) -> bool:
        return not self._is_type1(string_list)

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

    def _preparse_board(
        self, board_string: str
    ) -> Tuple[List[str], int, int, int, int]:
        parsed: List[str] = []

        parsed = HexobanBoard._cleaned_board_lines(board_string)
        width = len(parsed[0]) if len(parsed) > 0 else 0
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

        return parsed, width, height, even_row_x_parity, odd_row_x_parity

    def _add_column_left(self, string_list: List[str]) -> List[str]:
        return [Puzzle.FLOOR + line for line in string_list]

    def _add_column_right(self, string_list: List[str]) -> List[str]:
        return [line + Puzzle.FLOOR for line in string_list]

    @staticmethod
    def _remove_column_right(string_list: List[str]) -> List[str]:
        return [line[:-1] for line in string_list]

    @staticmethod
    def _find_first_non_floor(string_list: List[str]):
        normalized = HexobanBoard._normalize_width(string_list)
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

    @staticmethod
    def _find_rightmost_non_floor(string_list: List[str]) -> Optional[int]:
        def rightmost_finder(string_list: List[str], row_parity: int):
            cell_found = False
            height = len(string_list)
            width = len(string_list[0])
            x = y = 0

            for row in range(row_parity % 2, height, 2):
                for col in range(0, width):
                    if not Puzzle.is_empty_floor(string_list[row][col]):
                        cell_found = True
                        if col > x or (col >= x and row > y):
                            x = col
                            y = row

            if cell_found:
                return index_1d(x, y, width)

            return None

        normalized = HexobanBoard._normalize_width(string_list)
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