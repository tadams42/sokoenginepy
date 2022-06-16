from __future__ import annotations

import io
import re
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Final, List, Optional, Pattern, Tuple, Union

import arrow

from .collection import Collection
from .hexoban import HexobanPuzzle, HexobanSnapshot
from .octoban import OctobanPuzzle, OctobanSnapshot
from .puzzle import Puzzle
from .snapshot import Snapshot
from .sokoban import SokobanPuzzle, SokobanSnapshot
from .trioban import TriobanPuzzle, TriobanSnapshot
from .utilities import is_blank

if TYPE_CHECKING:
    from ..game import Tessellation

_SELF_DIR = Path(__file__).absolute().resolve().parent
_SOK_FORMAT_SPEC_PATH = _SELF_DIR / "SOK_format_specification.txt"


class SOKFileFormat:
    @classmethod
    def read(
        cls,
        src: Union[io.StringIO, io.TextIOWrapper],
        dest: Collection,
        tessellation_hint: Optional[Tessellation] = None,
    ):
        from ..game import Tessellation

        SOKReader(src, dest, tessellation_hint or Tessellation.SOKOBAN).read()

    @classmethod
    def write(cls, src: Collection, dest: Union[io.StringIO, io.TextIOWrapper]):
        SOKWriter(dest).write(src)


class SOKReader:
    def __init__(
        self,
        src: Union[io.StringIO, io.TextIOWrapper],
        dest: Collection,
        tessellation_hint: Tessellation,
    ):
        self.src = src
        self.dest = dest
        self.supplied_tessellation_hint = tessellation_hint
        self._data: CollectionData

    def read(self):
        self._parse()
        self._copy()

    def _parse(self):
        self.src.seek(0, 0)
        self._data = CollectionData()
        self._split_input(self.src.readlines())
        self._parse_title_lines()
        self._parse_notes()

    def _copy(self):
        from ..game import Tessellation

        self.dest.title = self._data.title or ""
        self.dest.author = self._data.author or ""
        self.dest.created_at = self._data.created_at or ""
        self.dest.updated_at = self._data.updated_at or ""
        self.dest.notes = self._data.notes

        for puzzle_data in self._data.puzzles:
            if puzzle_data.tessellation == Tessellation.SOKOBAN:
                puzzle = SokobanPuzzle(board=puzzle_data.board)
                snapshot_klass = SokobanSnapshot
            elif puzzle_data.tessellation == Tessellation.HEXOBAN:
                puzzle = HexobanPuzzle(board=puzzle_data.board)
                snapshot_klass = HexobanSnapshot
            elif puzzle_data.tessellation == Tessellation.TRIOBAN:
                puzzle = TriobanPuzzle(board=puzzle_data.board)
                snapshot_klass = TriobanSnapshot
            elif puzzle_data.tessellation == Tessellation.OCTOBAN:
                puzzle = OctobanPuzzle(board=puzzle_data.board)
                snapshot_klass = OctobanSnapshot
            else:
                raise ValueError(
                    f"Missing implementation for {puzzle_data.tessellation}!"
                )

            for attr in {"title", "author", "boxorder", "goalorder", "notes"}:
                setattr(puzzle, attr, getattr(puzzle_data, attr))

            for snapshot_data in puzzle_data.snapshots:
                snapshot = snapshot_klass(moves_data=snapshot_data.moves_data or "")
                for attr in {"title", "solver", "notes"}:
                    setattr(snapshot, attr, getattr(snapshot_data, attr))
                puzzle.snapshots.append(snapshot)

            self.dest.puzzles.append(puzzle)

    def _split_input(self, input_lines: List[str]):
        first_board_line = first_index_of(input_lines, Puzzle.is_board)
        if first_board_line is not None:
            self._data.notes = input_lines[:first_board_line]
            remaining_lines = input_lines[first_board_line:]
        else:
            self._data.notes = input_lines
            remaining_lines = []

        self._split_puzzle_chunks(remaining_lines)
        self._split_snapshot_chunks()

    def _split_puzzle_chunks(self, lines: List[str]):
        remaining_lines = lines
        while remaining_lines:
            puzzle = PuzzleData()

            first_note_line = first_index_of(
                remaining_lines, lambda x: not Puzzle.is_board(x)
            )
            if first_note_line is not None:
                puzzle.board = "".join(remaining_lines[:first_note_line])
                remaining_lines = remaining_lines[first_note_line:]
            else:
                puzzle.board = "".join(remaining_lines)
                remaining_lines = []

            if len(remaining_lines) > 0:
                first_board_line = first_index_of(remaining_lines, Puzzle.is_board)

                if first_board_line is not None:
                    puzzle.notes = remaining_lines[:first_board_line]
                    remaining_lines = remaining_lines[first_board_line:]
                else:
                    puzzle.notes = remaining_lines
                    remaining_lines = []
            else:
                puzzle.notes = []

            self._data.puzzles.append(puzzle)

    def _split_snapshot_chunks(self):
        for puzzle in self._data.puzzles:
            remaining_lines = puzzle.notes

            first_moves_line = first_index_of(remaining_lines, Snapshot.is_snapshot)
            if first_moves_line is not None:
                puzzle.notes = remaining_lines[:first_moves_line]
                remaining_lines = remaining_lines[first_moves_line:]
            else:
                puzzle.notes = remaining_lines
                remaining_lines = []

            puzzle.snapshots = []

            while len(remaining_lines) > 0:
                snapshot = SnapshotData()

                first_note_line = first_index_of(
                    remaining_lines, lambda x: not Snapshot.is_snapshot(x)
                )
                if first_note_line is not None:
                    snapshot.moves_data = "".join(
                        moves_line.strip()
                        for moves_line in remaining_lines[:first_note_line]
                    )
                    remaining_lines = remaining_lines[first_note_line:]
                else:
                    snapshot.moves_data = "".join(
                        moves_line.strip() for moves_line in remaining_lines
                    )
                    remaining_lines = []

                if len(remaining_lines) > 0:
                    first_moves_line = first_index_of(
                        remaining_lines, Snapshot.is_snapshot
                    )

                    if first_moves_line is not None:
                        snapshot.notes = remaining_lines[:first_moves_line]
                        remaining_lines = remaining_lines[first_moves_line:]
                    else:
                        snapshot.notes = remaining_lines
                        remaining_lines = []
                else:
                    snapshot.notes = []

                puzzle.snapshots.append(snapshot)

    def _notes_before_puzzle(self, puzzle_index: int) -> List[str]:
        if puzzle_index == 0:
            return self._data.notes
        previous_puzzle = self._data.puzzles[puzzle_index - 1]
        if len(previous_puzzle.snapshots) > 0:
            return previous_puzzle.snapshots[-1].notes
        return previous_puzzle.notes

    def _notes_before_snapshot(
        self, puzzle_index: int, snapshot_index: int
    ) -> List[str]:
        puzzle = self._data.puzzles[puzzle_index]
        if snapshot_index == 0:
            return puzzle.notes
        return puzzle.snapshots[snapshot_index - 1].notes

    @staticmethod
    def _get_and_remove_title_line(notes: List[str]) -> str:
        """
        :: Titles                                                 ::
        ::   A title line is the last non-blank text line before  ::
        ::   a board, a saved game, or a solution, provided the   ::
        ::   line is preceded by a blank line or it is the only   ::
        ::   text line at this position in the file.              ::
        ::                                                        ::
        ::   Title lines are optional unless a single or a last   ::
        ::   text line from a preceding puzzle, saved game,       ::
        ::   solution, or file header can be mistaken for a title ::
        ::   line.                                                ::
        """
        candidate_index = last_index_of(notes, lambda x: not is_blank(x))
        if candidate_index is None:
            return ""

        preceding_index = None
        if candidate_index > 0:
            preceding_index = candidate_index - 1

        following_index = None
        if candidate_index < len(notes) - 1:
            following_index = candidate_index + 1

        preceding_ok = is_blank(notes[preceding_index]) if preceding_index else True

        following_ok = is_blank(notes[following_index]) if following_index else True

        if preceding_ok and following_ok:
            title_line = notes[candidate_index].strip()
            del notes[candidate_index]
            return title_line

        return ""

    def _parse_title_lines(self):
        for puzzle_index, puzzle in enumerate(self._data.puzzles):
            puzzle.title = self._get_and_remove_title_line(
                self._notes_before_puzzle(puzzle_index)
            )
            for snapshot_index, snapshot in enumerate(puzzle.snapshots):
                snapshot.title = self._get_and_remove_title_line(
                    self._notes_before_snapshot(puzzle_index, snapshot_index)
                )

    def _parse_notes(self):
        remaining_lines = SOKTags.extract_collection_attributes(
            self._data, self._data.notes
        )
        self._data.notes = self._cleanup_whitespace(remaining_lines)

        for puzzle_data in self._data.puzzles:
            remaining_lines = SOKTags.extract_puzzle_attributes(
                puzzle_data,
                puzzle_data.notes,
                self._data.header_tessellation_hint,
                self.supplied_tessellation_hint,
            )
            puzzle_data.notes = self._cleanup_whitespace(remaining_lines)

            for snapshot in puzzle_data.snapshots:
                remaining_lines = SOKTags.extract_snapshot_attributes(
                    snapshot, snapshot.notes
                )
                snapshot.notes = self._cleanup_whitespace(remaining_lines)

    @staticmethod
    def _cleanup_whitespace(lst) -> List[str]:
        i = first_index_of(lst, lambda x: not is_blank(x))
        if i is None:
            return []
        lst = lst[i:]

        i = last_index_of(lst, lambda x: not is_blank(x))
        if i is not None:
            lst = lst[: i + 1]

        return "\n".join(line.strip() for line in lst).split("\n")


@dataclass
class SnapshotData:
    moves_data: Optional[str] = None
    title: Optional[str] = None
    solver: Optional[str] = None
    notes: List[str] = field(default_factory=list)


@dataclass
class PuzzleData:
    board: Optional[str] = None
    tessellation: Optional[Tessellation] = None
    title: Optional[str] = None
    author: Optional[str] = None
    boxorder: Optional[str] = None
    goalorder: Optional[str] = None
    notes: List[str] = field(default_factory=list)
    snapshots: List[SnapshotData] = field(default_factory=list, init=False, repr=False)


@dataclass
class CollectionData:
    title: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    notes: List[str] = field(default_factory=list)
    header_tessellation_hint: Optional[Tessellation] = None
    puzzles: List[PuzzleData] = field(default_factory=list, init=False, repr=False)


class SOKTags:
    AUTHOR: Final[str] = "Author"
    TITLE: Final[str] = "Title"
    COLLECTION: Final[str] = "Collection"
    GOALORDER: Final[str] = "goalorder"
    BOXORDER: Final[str] = "boxorder"
    SOLVER: Final[str] = "Solver"
    VARIANT: Final[str] = "Game"
    DATE_CREATED: Final[str] = "Date Created"
    DATE_OF_LAST_CHANGE: Final[str] = "Date of Last Change"
    RAW_FILE_NOTES: Final[str] = "::"
    TAG_DELIMITERS: Final[str] = "=:"

    COLLECTION_TAGS: Final[Dict[str, str]] = {
        AUTHOR: "author",
        TITLE: "title",
        COLLECTION: "title",
        VARIANT: "",
        DATE_CREATED: "created_at",
        DATE_OF_LAST_CHANGE: "updated_at",
    }

    PUZZLE_TAGS: Final[Dict[str, str]] = {
        TITLE: "title",
        AUTHOR: "author",
        BOXORDER: "boxorder",
        GOALORDER: "goalorder",
        VARIANT: "",
    }

    SNAPSHOT_TAGS: Final[Dict[str, str]] = {
        TITLE: "title",
        AUTHOR: "solver",
        SOLVER: "solver",
    }

    @classmethod
    def extract_collection_attributes(
        cls, dest: CollectionData, notes: List[str]
    ) -> List[str]:
        from ..game import Tessellation

        remaining_lines = []
        tessellation = None
        for line in notes:
            if cls.is_raw_file_notes_line(line):
                continue

            was_tagged = False
            for tag, attr in cls.COLLECTION_TAGS.items():
                found, value = cls.get_tag_data(tag, line)
                if found:
                    if tag == cls.VARIANT:
                        tessellation = value
                    else:
                        setattr(dest, attr, value)
                    was_tagged = True
                    break

            if not was_tagged:
                remaining_lines.append(line)

        if not is_blank(tessellation):
            dest.header_tessellation_hint = Tessellation[tessellation.strip().upper()]

        return remaining_lines

    @classmethod
    def extract_puzzle_attributes(
        cls,
        dest: PuzzleData,
        notes: List[str],
        collection_header_tessellation_hint: Optional[Tessellation],
        supplied_tessellation_hint: Optional[Tessellation],
    ) -> List[str]:
        from ..game import Tessellation

        remaining_lines = []
        tessellation = None
        for line in notes:
            was_tagged = False
            for tag, attr in cls.PUZZLE_TAGS.items():
                found, value = cls.get_tag_data(tag, line)
                if found:
                    if tag == cls.VARIANT:
                        tessellation = value
                    else:
                        setattr(dest, attr, value)
                    was_tagged = True
                    break

            if not was_tagged:
                remaining_lines.append(line)

        if not is_blank(tessellation):
            dest.tessellation = Tessellation[tessellation.strip().upper()]
        elif collection_header_tessellation_hint is not None:
            dest.tessellation = collection_header_tessellation_hint
        elif supplied_tessellation_hint is not None:
            dest.tessellation = supplied_tessellation_hint
        else:
            dest.tessellation = Tessellation.SOKOBAN

        return remaining_lines

    @classmethod
    def extract_snapshot_attributes(
        cls, dest: SnapshotData, notes: List[str]
    ) -> List[str]:
        remaining_lines = []
        for line in notes:
            was_tagged = False
            for tag, attr in cls.SNAPSHOT_TAGS.items():
                found, value = cls.get_tag_data(tag, line)
                if found:
                    setattr(dest, attr, value)
                    was_tagged = True
                    break

            if not was_tagged:
                remaining_lines.append(line)

        return remaining_lines

    _TAG_SPLITTER: Final[Pattern] = re.compile(
        "|".join(map(re.escape, list(TAG_DELIMITERS)))
    )

    @classmethod
    def get_tag_data(cls, tag: str, line: str) -> Tuple[bool, Optional[str]]:
        """
        If it successfully extracts ``tag`` data from ``line``, it returns tuple
        ``(True, extracted_value). Otherwise, returns tuple ``(false, None)``.
        """
        components = cls._TAG_SPLITTER.split(str(line), 1)
        if components[0].strip().lower() == tag.strip().lower():
            return (True, "".join(components[1:]).strip())
        return (False, None)

    @classmethod
    def is_raw_file_notes_line(cls, line: str) -> bool:
        return line.lstrip().startswith(cls.RAW_FILE_NOTES)

    @classmethod
    def write_tagged(
        cls, dest: Union[io.StringIO, io.TextIOWrapper], tag: str, data: Optional[str]
    ) -> bool:
        if not data or is_blank(data) or is_blank(tag):
            return False
        dest.write(tag.strip() + ": " + data.rstrip() + "\n")
        return True


class SOKWriter:
    def __init__(self, dest: Union[io.StringIO, io.TextIOWrapper]):
        self.dest = dest

    def write(self, src: Collection):
        self._write_collection_header(src)
        for puzzle in src.puzzles:
            self._write_puzzle(puzzle)

    def _write_collection_header(self, src: Collection):
        for line in open(_SOK_FORMAT_SPEC_PATH):
            self.dest.write(line.rstrip() + "\n")

        SOKTags.write_tagged(
            self.dest,
            SOKTags.DATE_CREATED,
            src.created_at.strip() or arrow.utcnow().isoformat(),
        )
        SOKTags.write_tagged(
            self.dest,
            SOKTags.DATE_OF_LAST_CHANGE,
            src.updated_at.strip() or arrow.utcnow().isoformat(),
        )

        self.dest.write(
            "::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::" + "\n\n"
        )

        written = False
        written = (
            SOKTags.write_tagged(self.dest, SOKTags.COLLECTION, src.title) or written
        )
        written = SOKTags.write_tagged(self.dest, SOKTags.AUTHOR, src.author) or written

        puzzle_collection_notes = "\n".join(src.notes)
        if not is_blank(puzzle_collection_notes):
            self.dest.write(puzzle_collection_notes.rstrip() + "\n")
            written = True

        if written:
            self.dest.write("\n")

    def _write_puzzle(self, src: Puzzle):
        from ..game import Tessellation

        if is_blank(src.board):
            return

        if not is_blank(src.title):
            self.dest.write(src.title.strip() + "\n\n")

        self.dest.write(src.board.rstrip() + "\n\n")

        written = False

        if src.tessellation != Tessellation.SOKOBAN:
            written = (
                SOKTags.write_tagged(
                    self.dest, SOKTags.VARIANT, str(src.tessellation.value).lower()
                )
                or written
            )

        if not is_blank(src.boxorder) and not is_blank(src.goalorder):
            written = (
                SOKTags.write_tagged(self.dest, SOKTags.BOXORDER, src.boxorder)
                or written
            )
            written = (
                SOKTags.write_tagged(self.dest, SOKTags.GOALORDER, src.goalorder)
                or written
            )

        if not is_blank(src.author):
            written = (
                SOKTags.write_tagged(self.dest, SOKTags.AUTHOR, src.author) or written
            )

        puzzle_notes = "\n".join(src.notes)
        if not is_blank(puzzle_notes):
            self.dest.write(puzzle_notes.rstrip() + "\n")
            written = True

        if written:
            self.dest.write("\n")

        for snapshot in src.snapshots:
            self._write_snapshot(snapshot)

    def _write_snapshot(self, src: Snapshot):
        if is_blank(src.moves_data):
            return

        if not is_blank(src.title):
            self.dest.write(src.title.strip() + "\n")

        self.dest.write("\n".join(textwrap.wrap(src.moves_data.strip(), 70)) + "\n")

        written = SOKTags.write_tagged(self.dest, SOKTags.SOLVER, src.solver)

        snap_notes = "\n".join(src.notes)
        if not is_blank(snap_notes):
            self.dest.write(snap_notes.rstrip() + "\n")
            written = True

        if written:
            self.dest.write("\n")


def first_index_of(lst, predicate):
    return next((index for index, elem in enumerate(lst) if predicate(elem)), None)


def last_index_of(lst, predicate):
    candidate_index = first_index_of(reversed(lst), predicate)
    if candidate_index is not None:
        return len(lst) - candidate_index - 1
    return None
