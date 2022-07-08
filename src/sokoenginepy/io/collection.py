from __future__ import annotations

import io
from pathlib import Path
from typing import List, Union

from ..game import Tessellation
from .puzzle import Puzzle


class Collection:
    """
    Collection of one or more game puzzles.

    Attributes:
        title (str): Collection title
        author (str): Collection author
        created_at (str): datetime string of unspecified format (it is not parsed)
        updated_at (str): datetime string of unspecified format (it is not parsed)
        notes (List[str]): collection notes
        puzzles (List[Puzzle]): collection puzzles
    """

    def __init__(
        self,
        title: str = "",
        author: str = "",
        created_at: str = "",
        updated_at: str = "",
        notes: str = "",
    ):
        self.title = title
        self.author = author
        self.created_at = created_at
        self.updated_at = updated_at
        self.notes = notes
        self.puzzles: List[Puzzle] = []

    def load(
        self,
        src: Union[
            str,
            Path,
            io.BufferedReader,
            io.TextIOWrapper,
            io.FileIO,
            io.StringIO,
            io.BytesIO,
        ],
        tessellation_hint: Tessellation = Tessellation.SOKOBAN,
    ):
        """
        Loads collection from ``src``.

        Loader supports SokobanYASC .sok format, but will happily try to load older,
        similar textual sokoban files (usually with extensions ``.txt``, ``.tsb`` or
        ``.hsb``).

        Arguments:
            src: source file path or input stream object
            tessellation_hint: If puzzles in file don't specify their game tessellation
                assume this value.
        """
        from .sok_file_format import SOKFileFormat

        if isinstance(src, (str, Path)):
            with open(src, "r") as f:
                SOKFileFormat.read(f, self, tessellation_hint)
        else:
            SOKFileFormat.read(src, self, tessellation_hint)

    def loads(
        self,
        data: Union[str, bytes],
        tessellation_hint: Tessellation = Tessellation.SOKOBAN,
    ):
        """
        Loads collections from ``data``.

        Arguments:
            data: raw collection data
            tessellation_hint: If puzzles in file don't specify their game tessellation
                assume this value.
        """
        if isinstance(data, bytes):
            data = data.decode(encoding="utf-8")
        f = io.StringIO(data)
        self.load(f, tessellation_hint)

    def dump(
        self,
        dst: Union[
            str,
            Path,
            io.BufferedWriter,
            io.TextIOWrapper,
            io.FileIO,
            io.StringIO,
            io.BytesIO,
        ],
    ):
        """
        Saves collection to ``dst`` in SokobanYASC .sok format.

        Note:
            Doesn't care about file extension if ``dst`` is path to file.

        Arguments:
            dst: Path to destination file or destination stream object.
        """
        from .sok_file_format import SOKFileFormat

        if isinstance(dst, (str, Path)):
            with open(dst, "w") as f:
                SOKFileFormat.write(self, f)
        else:
            SOKFileFormat.write(self, dst)

    def dumps(self) -> str:
        """Saves collection to `str`."""
        out = io.StringIO()
        self.dump(out)
        return out.getvalue()
