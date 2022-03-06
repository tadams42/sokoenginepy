import os

from ..tessellation import Tessellation
from .sok_file_format import SOKFileFormat


class PuzzlesCollection:
    """
    Collection of :class:``.Puzzle``

    TODO: Convert to iterable and sequence
    """

    def __init__(self, title="", author="", created_at="", updated_at="", notes=""):
        self.title = title
        self.author = author
        self.created_at = created_at
        self.updated_at = updated_at
        self.notes = notes
        self.puzzles = []

    def clear(self):
        self.title = ""
        self.author = ""
        self.created_at = ""
        self.updated_at = ""
        self.notes = ""
        self.puzzles = []

    def reformat(self):
        for puzzle in self.puzzles:
            puzzle.reformat()

    @staticmethod
    def _extension_to_tessellation_hint(path):
        file_name, file_extension = os.path.splitext(path)
        if (
            file_extension == ".sok"
            or file_extension == ".txt"
            or file_extension == ".xsb"
        ):
            return Tessellation.SOKOBAN
        elif file_extension == ".tsb":
            return Tessellation.TRIOBAN
        elif file_extension == ".hsb":
            return Tessellation.HEXOBAN

        return Tessellation.SOKOBAN

    def load(self, path):
        with open(path, "r") as src_file:
            SOKFileFormat.read(
                src_file, self, self._extension_to_tessellation_hint(path)
            )

        for i in range(0, len(self.puzzles)):
            self.puzzles[i].pid = i + 1
            for j in range(0, len(self.puzzles[i].snapshots)):
                self.puzzles[i].snapshots[j].pid = j + 1

    def save(self, path):
        with open(path, "w") as dest_file:
            SOKFileFormat.write(self, dest_file)
