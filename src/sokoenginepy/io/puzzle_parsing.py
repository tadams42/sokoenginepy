from __future__ import annotations

from copy import deepcopy
from typing import List, Tuple

from .puzzle import Puzzle
from .rle import Rle
from .utilities import is_blank


class PuzzleResizer:
    def add_row_top(
        self, parsed_board: List[str], width: int, height: int
    ) -> Tuple[List[str], int, int]:
        from ..game import index_1d

        old_body = parsed_board
        old_height = height

        new_height = height + 1
        new_width = width
        new_body = new_height * new_width * [Puzzle.VISIBLE_FLOOR]

        for x in range(0, new_width):
            for y in range(0, old_height):
                new_body[index_1d(x, y + 1, new_width)] = old_body[
                    index_1d(x, y, new_width)
                ]

        return new_body, new_width, new_height

    def add_row_bottom(
        self, parsed_board: List[str], width: int, height: int
    ) -> Tuple[List[str], int, int]:
        from ..game import index_1d

        old_body = parsed_board
        old_height = height

        new_height = height + 1
        new_width = width
        new_body = new_height * new_width * [Puzzle.VISIBLE_FLOOR]

        for x in range(0, new_width):
            for y in range(0, old_height):
                new_body[index_1d(x, y, new_width)] = old_body[
                    index_1d(x, y, new_width)
                ]

        return new_body, new_width, new_height

    def add_column_left(
        self, parsed_board: List[str], width: int, height: int
    ) -> Tuple[List[str], int, int]:
        from ..game import index_1d

        old_body = parsed_board
        old_width = width

        new_height = height
        new_width = width + 1
        new_body = new_height * new_width * [Puzzle.VISIBLE_FLOOR]

        for x in range(0, old_width):
            for y in range(0, new_height):
                new_body[index_1d(x + 1, y, new_width)] = old_body[
                    index_1d(x, y, old_width)
                ]

        return new_body, new_width, new_height

    def add_column_right(
        self, parsed_board: List[str], width: int, height: int
    ) -> Tuple[List[str], int, int]:
        from ..game import index_1d

        old_body = parsed_board
        old_width = width

        new_height = height
        new_width = width + 1
        new_body = new_height * new_width * [Puzzle.VISIBLE_FLOOR]

        for x in range(0, old_width):
            for y in range(0, new_height):
                new_body[index_1d(x, y, new_width)] = old_body[
                    index_1d(x, y, old_width)
                ]

        return new_body, new_width, new_height

    def remove_row_top(
        self, parsed_board: List[str], width: int, height: int
    ) -> Tuple[List[str], int, int]:
        from ..game import index_1d

        old_body = parsed_board

        new_height = height - 1
        new_width = width
        if new_height <= 0:
            return [], 0, 0
        new_body = new_height * new_width * [Puzzle.VISIBLE_FLOOR]

        for x in range(0, new_width):
            for y in range(0, new_height):
                new_body[index_1d(x, y, new_width)] = old_body[
                    index_1d(x, y + 1, new_width)
                ]

        return new_body, new_width, new_height

    def remove_row_bottom(
        self, parsed_board: List[str], width: int, height: int
    ) -> Tuple[List[str], int, int]:
        from ..game import index_1d

        old_body = parsed_board

        new_height = height - 1
        new_width = width
        if new_height <= 0:
            return [], 0, 0
        new_body = new_height * new_width * [Puzzle.VISIBLE_FLOOR]

        for x in range(0, new_width):
            for y in range(0, new_height):
                new_body[index_1d(x, y, new_width)] = old_body[
                    index_1d(x, y, new_width)
                ]

        return new_body, new_width, new_height

    def remove_column_left(
        self, parsed_board: List[str], width: int, height: int
    ) -> Tuple[List[str], int, int]:
        from ..game import index_1d

        old_body = parsed_board
        old_width = width

        new_height = height
        new_width = width - 1
        if new_width <= 0:
            return [], 0, 0
        new_body = new_height * new_width * [Puzzle.VISIBLE_FLOOR]

        for x in range(0, new_width):
            for y in range(0, new_height):
                new_body[index_1d(x, y, new_width)] = old_body[
                    index_1d(x + 1, y, old_width)
                ]

        return new_body, new_width, new_height

    def remove_column_right(
        self, parsed_board: List[str], width: int, height: int
    ) -> Tuple[List[str], int, int]:
        from ..game import index_1d

        old_body = parsed_board
        old_width = width

        new_height = height
        new_width = width - 1
        if new_width <= 0:
            return [], 0, 0
        new_body = new_height * new_width * [Puzzle.VISIBLE_FLOOR]

        for x in range(0, new_width):
            for y in range(0, new_height):
                new_body[index_1d(x, y, new_width)] = old_body[
                    index_1d(x, y, old_width)
                ]

        return new_body, new_width, new_height

    def trim_left(
        self, parsed_board: List[str], width: int, height: int
    ) -> Tuple[List[str], int, int]:
        from ..game import index_1d

        amount = width
        for y in range(0, height):
            border_found = False
            for x in range(0, width):
                border_found = Puzzle.is_border_element(
                    parsed_board[index_1d(x, y, width)]
                )
                if border_found and x < amount:
                    amount = x
                    break

        new_body = deepcopy(parsed_board)
        new_width = width
        new_height = height
        for _ in range(0, amount):
            new_body, new_width, new_height = self.remove_column_left(
                new_body, new_width, new_height
            )

        return new_body, new_width, new_height

    def trim_right(
        self, parsed_board: List[str], width: int, height: int
    ) -> Tuple[List[str], int, int]:
        new_body = deepcopy(parsed_board)
        new_width = width
        new_height = height

        new_body, new_width, new_height = self.reverse_columns(
            new_body, new_width, new_height
        )
        new_body, new_width, new_height = self.trim_left(
            new_body, new_width, new_height
        )
        new_body, new_width, new_height = self.reverse_columns(
            new_body, new_width, new_height
        )

        return new_body, new_width, new_height

    def trim_top(
        self, parsed_board: List[str], width: int, height: int
    ) -> Tuple[List[str], int, int]:
        from ..game import index_1d

        amount = height
        for x in range(0, width):
            border_found = False
            for y in range(0, height):
                border_found = Puzzle.is_border_element(
                    parsed_board[index_1d(x, y, width)]
                )
                if border_found:
                    if y < amount:
                        amount = y
                    break

        new_body = deepcopy(parsed_board)
        new_width = width
        new_height = height

        for _ in range(0, amount):
            new_body, new_width, new_height = self.remove_row_top(
                new_body, new_width, new_height
            )

        return new_body, new_width, new_height

    def trim_bottom(
        self, parsed_board: List[str], width: int, height: int
    ) -> Tuple[List[str], int, int]:
        new_body = deepcopy(parsed_board)
        new_width = width
        new_height = height

        new_body, new_width, new_height = self.reverse_rows(
            new_body, new_width, new_height
        )
        new_body, new_width, new_height = self.trim_top(new_body, new_width, new_height)
        new_body, new_width, new_height = self.reverse_rows(
            new_body, new_width, new_height
        )

        return new_body, new_width, new_height

    def reverse_rows(
        self, parsed_board: List[str], width: int, height: int
    ) -> Tuple[List[str], int, int]:
        from ..game import index_1d

        old_body = deepcopy(parsed_board)

        new_body = width * height * [Puzzle.VISIBLE_FLOOR]

        for x in range(0, width):
            for y in range(0, height):
                new_body[index_1d(x, y, width)] = str(
                    old_body[index_1d(x, height - y - 1, width)]
                )

        return new_body, width, height

    def reverse_columns(
        self, parsed_board: List[str], width: int, height: int
    ) -> Tuple[List[str], int, int]:
        from ..game import index_1d

        old_body = deepcopy(parsed_board)

        new_body = width * height * [Puzzle.VISIBLE_FLOOR]

        for x in range(0, width):
            for y in range(0, height):
                new_body[index_1d(x, y, width)] = str(
                    old_body[index_1d(width - x - 1, y, width)]
                )

        return new_body, width, height


class PuzzleParser:
    def parse(self, board: str) -> List[str]:
        return self.cleaned_board_lines(board)

    @classmethod
    def calculate_width(cls, strings: List[str]) -> int:
        """Width of list of strings as length of longest string in that list."""
        width = 0
        for line in strings:
            if len(line) > width:
                width = len(line)
        return width

    @classmethod
    def normalize_width(cls, strings: List[str], fill_chr: str = " ") -> List[str]:
        """
        Normalizes length of strings in ``string_list``.

        All strings are modified to be as long as the longest one in list. Missing
        characters in string are appended using ``fill_chr``.
        """
        width = cls.calculate_width(strings)
        return [l + (fill_chr * (width - len(l))) for l in strings]

    @classmethod
    def cleaned_board_lines(cls, line: str) -> List[str]:
        """
        Converts line into width-normalized, decoded list of board lines suitable for
        conversion into proper board object.
        """
        if is_blank(line):
            return []

        if not Puzzle.is_board(line):
            raise ValueError("Illegal characters found in board string")

        return cls.normalize_width(Rle.decode(line).split("\n"))


class PuzzlePrinter:
    def print(
        self,
        parsed_board: List[str],
        width: int,
        height: int,
        use_visible_floor: bool,
        rle_encode: bool,
    ) -> str:
        from ..game import index_1d

        retv_list: List[str] = []

        for y in range(height):
            tmp: str = ""
            for x in range(width):
                c = parsed_board[index_1d(x, y, width)]
                if Puzzle.is_empty_floor(c):
                    c = Puzzle.VISIBLE_FLOOR if use_visible_floor else Puzzle.FLOOR
                tmp += c

            retv_list.append(tmp)

        retv = "\n".join(retv_list)

        if rle_encode:
            retv = Rle.encode(retv)

        return retv
