from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Union

from .puzzle import Puzzle


class Collection:
    """
    Collection of one or more game puzzles.
    """

    def __init__(
        self,
        title: str = "",
        author: str = "",
        created_at: str = "",
        updated_at: str = "",
        notes: Optional[List[str]] = None,
    ):
        self.title = title
        self.author = author
        self.created_at = created_at
        self.updated_at = updated_at
        self.notes: List[str] = notes or []
        self.puzzles: List[Puzzle] = []

    @staticmethod
    def _extension_to_tessellation_hint(path: Union[str, Path]) -> str:
        file_name, file_extension = os.path.splitext(path)
        if file_extension == ".tsb":
            return "trioban"
        elif file_extension == ".hsb":
            return "hexoban"
        else:
            return "sokoban"

    def load(self, path: Union[str, Path], puzzle_types_hint: Optional[str] = None):
        from .sok_file_format import SOKFileFormat

        with open(path, "r") as src_file:
            SOKFileFormat.read(
                src_file,
                self,
                puzzle_types_hint or self._extension_to_tessellation_hint(path),
            )

        for i in range(0, len(self.puzzles)):
            self.puzzles[i].id = i + 1
            for j in range(0, len(self.puzzles[i].snapshots)):
                self.puzzles[i].snapshots[j].id = j + 1

    def save(self, path: Union[str, Path]):
        from .sok_file_format import SOKFileFormat

        with open(path, "w") as dest_file:
            SOKFileFormat.write(self, dest_file)
