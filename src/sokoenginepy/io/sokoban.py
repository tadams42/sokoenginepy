from __future__ import annotations

from .puzzle_parsing import PuzzleParser, PuzzlePrinter, PuzzleResizer


class Sokoban:
    @classmethod
    def parser(cls):
        return PuzzleParser()

    @classmethod
    def printer(cls):
        return PuzzlePrinter()

    @classmethod
    def resizer(cls):
        return PuzzleResizer()
