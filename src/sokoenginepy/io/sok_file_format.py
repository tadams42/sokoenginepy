from __future__ import annotations

import re
from enum import Enum
from pathlib import Path
from typing import List, Optional

import arrow

from .puzzle import Puzzle
from .puzzle_types import PuzzleTypes
from .snapshot import Snapshot
from .utilities import is_blank
from .collection import Collection

_SELF_DIR = Path(__file__).absolute().resolve().parent
_SOK_FORMAT_SPEC_PATH = _SELF_DIR / "SOK_format_specification.txt"


def first_index_of(lst, predicate):
    return next((index for index, elem in enumerate(lst) if predicate(elem)), None)


def last_index_of(lst, predicate):
    candidate_index = first_index_of(reversed(lst), predicate)
    if candidate_index is not None:
        return len(lst) - candidate_index - 1
    return None


class SOKFileFormat:
    @classmethod
    def read(
        cls,
        src_stream,
        dest_collection: Collection,
        puzzle_type_hint: PuzzleTypes = PuzzleTypes.SOKOBAN,
    ):
        SOKReader(src_stream, dest_collection, puzzle_type_hint).read()

    @classmethod
    def write(cls, collection: Collection, dest_stream):
        SOKWriter(dest_stream).write(collection)


class SOKTags(str, Enum):
    AUTHOR = "Author"
    TITLE = "Title"
    GOALORDER = "goalorder"
    BOXORDER = "boxorder"
    SOLVER = "Solver"
    VARIANT = "Game"
    CREATED_AT = "Date created"
    SNAPSHOT_CREATED_AT = "Date"
    UPDATED_AT = "Date of last change"
    DURATION = "Time"
    RAW_FILE_NOTES = "::"
    TAG_DELIMITERS = "=:"


class SOKReader:
    def __init__(
        self, src_stream, dest_collection: Collection, puzzle_type_hint: PuzzleTypes
    ):
        self.coll_header_puzzle_type_hint: Optional[PuzzleTypes] = None
        self.src_stream = src_stream
        self.dest_collection = dest_collection
        self.supplied_puzzle_type_hint = puzzle_type_hint

    def read(self):
        self.src_stream.seek(0, 0)
        self.dest_collection.clear()
        self._split_input(self.src_stream.readlines())
        self._parse_title_lines()
        self._parse_collection_notes()
        self._parse_puzzles()

    def _split_input(self, input_lines: List[str]):
        first_board_line = first_index_of(input_lines, Puzzle.is_board)
        if first_board_line is not None:
            self.dest_collection.notes = input_lines[:first_board_line]
            remaining_lines = input_lines[first_board_line:]
        else:
            self.dest_collection.notes = input_lines
            remaining_lines = []

        self._split_puzzle_chunks(remaining_lines)
        self._split_snapshot_chunks()

    def _split_puzzle_chunks(self, lines):
        remaining_lines = lines
        while len(remaining_lines) > 0:
            puzzle = Puzzle()

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

            self.dest_collection.puzzles.append(puzzle)

    def _split_snapshot_chunks(self):
        for puzzle in self.dest_collection.puzzles:
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
                snap = Snapshot()

                first_note_line = first_index_of(
                    remaining_lines, lambda x: not Snapshot.is_snapshot(x)
                )
                if first_note_line is not None:
                    snap.moves = "".join(
                        moves_line.strip()
                        for moves_line in remaining_lines[:first_note_line]
                    )
                    remaining_lines = remaining_lines[first_note_line:]
                else:
                    snap.moves = "".join(
                        moves_line.strip() for moves_line in remaining_lines
                    )
                    remaining_lines = []

                if len(remaining_lines) > 0:
                    first_moves_line = first_index_of(
                        remaining_lines, Snapshot.is_snapshot
                    )

                    if first_moves_line is not None:
                        snap.notes = remaining_lines[:first_moves_line]
                        remaining_lines = remaining_lines[first_moves_line:]
                    else:
                        snap.notes = remaining_lines
                        remaining_lines = []
                else:
                    snap.notes = []

                puzzle.snapshots.append(snap)

    _tag_splitter = re.compile("|".join(map(re.escape, list(SOKTags.TAG_DELIMITERS))))

    def _get_tag_data(self, tag: str, line: str) -> Optional[str]:
        # TODO: If tag data contains split char, it will not get collected
        # ie. "Date created: 2015-02-03 13:42:32"
        components = self._tag_splitter.split(str(line))
        if components[0].strip().lower() == tag.strip().lower():
            return components[1].strip()
        return None

    @staticmethod
    def _is_tagged_as(tag, line: str) -> bool:
        return any(
            chr in list(SOKTags.TAG_DELIMITERS) for chr in line
        ) and line.lstrip().lower().startswith(tag.strip().lower())

    def _is_collection_tag_line(self, line: str) -> bool:
        return any(
            self._is_tagged_as(tag, line)
            for tag in (
                SOKTags.AUTHOR,
                SOKTags.TITLE,
                SOKTags.VARIANT,
                SOKTags.CREATED_AT,
                SOKTags.UPDATED_AT,
            )
        )

    def _is_puzzle_tag_line(self, line: str) -> bool:
        return any(
            self._is_tagged_as(tag, line)
            for tag in (
                SOKTags.AUTHOR,
                SOKTags.VARIANT,
                SOKTags.TITLE,
                SOKTags.BOXORDER,
                SOKTags.GOALORDER,
            )
        )

    def _is_snapshot_tag_line(self, line: str) -> bool:
        return any(
            self._is_tagged_as(tag, line)
            for tag in (
                SOKTags.AUTHOR,
                SOKTags.SOLVER,
                SOKTags.CREATED_AT,
                SOKTags.SNAPSHOT_CREATED_AT,
                SOKTags.DURATION,
            )
        )

    @staticmethod
    def _is_raw_file_notes_line(line: str) -> bool:
        return line.lstrip().startswith(SOKTags.RAW_FILE_NOTES)

    def _notes_before_puzzle(self, puzzle_index: int) -> List[str]:
        if puzzle_index == 0:
            return self.dest_collection.notes
        previous_puzzle = self.dest_collection.puzzles[puzzle_index - 1]
        if len(previous_puzzle.snapshots) > 0:
            return previous_puzzle.snapshots[-1].notes
        return previous_puzzle.notes

    def _notes_before_snapshot(
        self, puzzle_index: int, snapshot_index: int
    ) -> List[str]:
        puzzle = self.dest_collection.puzzles[puzzle_index]
        if snapshot_index == 0:
            return puzzle.notes
        return puzzle.snapshots[snapshot_index - 1].notes

    @staticmethod
    def _get_and_remove_title_line(notes: List[str]) -> str:
        """
        ::   Titles                                               ::
        ::   A title line is the last non-blank text line before  ::
        ::   a puzzle or a game, provided the line is preceded     ::
        ::   by a blank line or it is the only text line at this  ::
        ::   position in the file.                                ::
        ::                                                        ::
        ::   Title lines are optional unless a single or a last   ::
        ::   text line from a preceding puzzle, game, or file      ::
        ::   header can be mistaken for a title line.             ::
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
        for puzzle_index, puzzle in enumerate(self.dest_collection.puzzles):
            puzzle.title = self._get_and_remove_title_line(
                self._notes_before_puzzle(puzzle_index)
            )
            for snapshot_index, snap in enumerate(puzzle.snapshots):
                snap.title = self._get_and_remove_title_line(
                    self._notes_before_snapshot(puzzle_index, snapshot_index)
                )

    def _parse_collection_notes(self):
        self.coll_header_puzzle_type_hint = None

        remaining_lines = []
        found_val = None
        for line in self.dest_collection.notes:
            if self._is_collection_tag_line(line):
                found_val = found_val or self._get_tag_data(SOKTags.VARIANT, line)
                self.dest_collection.title = (
                    self.dest_collection.title
                    or self._get_tag_data(SOKTags.TITLE, line)
                    or ""
                )
                self.dest_collection.author = (
                    self.dest_collection.author
                    or self._get_tag_data(SOKTags.AUTHOR, line)
                    or ""
                )
                self.dest_collection.created_at = (
                    self.dest_collection.created_at
                    or self._get_tag_data(SOKTags.CREATED_AT, line)
                    or ""
                )
                self.dest_collection.updated_at = (
                    self.dest_collection.updated_at
                    or self._get_tag_data(SOKTags.UPDATED_AT, line)
                    or ""
                )
            elif not self._is_raw_file_notes_line(line):
                remaining_lines.append(line)

        if found_val:
            self.coll_header_puzzle_type_hint = PuzzleTypes[found_val.strip().upper()]

        self.dest_collection.notes = self._cleanup_whitespace(remaining_lines)

    def _parse_puzzles(self):
        for puzzle in self.dest_collection.puzzles:
            remaining_lines = []
            puzzle_type = None
            for line in puzzle.notes:
                if self._is_puzzle_tag_line(line):
                    puzzle_type = puzzle_type or self._get_tag_data(
                        SOKTags.VARIANT, line
                    )
                    puzzle.title = (
                        puzzle.title or self._get_tag_data(SOKTags.TITLE, line) or ""
                    )
                    puzzle.author = (
                        puzzle.author or self._get_tag_data(SOKTags.AUTHOR, line) or ""
                    )
                    puzzle.boxorder = (
                        puzzle.boxorder
                        or self._get_tag_data(SOKTags.BOXORDER, line)
                        or ""
                    )
                    puzzle.goalorder = (
                        puzzle.goalorder
                        or self._get_tag_data(SOKTags.GOALORDER, line)
                        or ""
                    )
                else:
                    remaining_lines.append(line)

            puzzle.notes = self._cleanup_whitespace(remaining_lines)

            if puzzle_type is not None:
                puzzle.puzzle_type = PuzzleTypes[puzzle_type.upper()]
            elif self.coll_header_puzzle_type_hint is not None:
                puzzle.puzzle_type = self.coll_header_puzzle_type_hint
            elif self.supplied_puzzle_type_hint is not None:
                puzzle.puzzle_type = self.supplied_puzzle_type_hint

            self._parse_snapshots(puzzle)

    def _parse_snapshots(self, puzzle: Puzzle):
        for snap in puzzle.snapshots:
            remaining_lines = []
            for line in snap.notes:
                if self._is_snapshot_tag_line(line):
                    snap.solver = (
                        snap.solver or self._get_tag_data(SOKTags.AUTHOR, line) or ""
                    )
                    snap.solver = (
                        snap.solver or self._get_tag_data(SOKTags.SOLVER, line) or ""
                    )
                    snap.created_at = (
                        snap.created_at
                        or self._get_tag_data(SOKTags.CREATED_AT, line)
                        or ""
                    )
                    snap.duration = (
                        snap.duration
                        or self._get_tag_data(SOKTags.DURATION, line)
                        or ""
                    )
                    snap.created_at = (
                        snap.created_at
                        or self._get_tag_data(SOKTags.SNAPSHOT_CREATED_AT, line)
                        or ""
                    )
                else:
                    remaining_lines.append(line)

            snap.notes = self._cleanup_whitespace(remaining_lines)
            snap.puzzle_type = puzzle.puzzle_type

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


class SOKWriter:
    def __init__(self, dest_stream):
        self.dest_stream = dest_stream

    def write(self, puzzle_or_collection: Collection):
        if isinstance(puzzle_or_collection, Puzzle):
            self._write_puzzle(puzzle_or_collection)
        else:
            self._write_collection(puzzle_or_collection)

    def _write_collection(self, puzzle_collection: Collection):
        self._write_collection_header(puzzle_collection)
        for puzzle in puzzle_collection.puzzles:
            self._write_puzzle(puzzle)

    def _write_puzzle(self, puzzle: Puzzle):
        if is_blank(puzzle.board):
            return

        if not is_blank(puzzle.title):
            self.dest_stream.write(puzzle.title.strip() + "\n\n")

        self.dest_stream.write(puzzle.board.rstrip() + "\n\n")

        written = False

        if puzzle.puzzle_type != PuzzleTypes.SOKOBAN:
            written = (
                self._write_tagged(SOKTags.VARIANT, str(puzzle.puzzle_type)) or written
            )

        if not is_blank(puzzle.boxorder) and not is_blank(puzzle.goalorder):
            written = self._write_tagged(SOKTags.BOXORDER, puzzle.boxorder) or written
            written = self._write_tagged(SOKTags.GOALORDER, puzzle.goalorder) or written

        puzzle_notes = "\n".join(puzzle.notes)
        if not is_blank(puzzle_notes):
            self.dest_stream.write(puzzle_notes.rstrip() + "\n")
            written = True

        if written:
            self.dest_stream.write("\n")

        for snap in puzzle.snapshots:
            self._write_snapshot(snap)

    def _write_collection_header(self, puzzle_collection: Collection):
        for line in open(_SOK_FORMAT_SPEC_PATH):
            self.dest_stream.write(line.rstrip() + "\n")

        self._write_tagged(
            SOKTags.CREATED_AT,
            puzzle_collection.created_at.strip() or arrow.utcnow().isoformat(),
        )
        self._write_tagged(
            SOKTags.UPDATED_AT,
            puzzle_collection.updated_at.strip() or arrow.utcnow().isoformat(),
        )

        self.dest_stream.write(
            "::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::" + "\n\n"
        )

        written = False
        written = (
            self._write_tagged(SOKTags.AUTHOR, puzzle_collection.author) or written
        )
        written = self._write_tagged(SOKTags.TITLE, puzzle_collection.title) or written

        puzzle_collection_notes = "\n".join(puzzle_collection.notes)
        if not is_blank(puzzle_collection_notes):
            self.dest_stream.write(puzzle_collection_notes.rstrip() + "\n")
            written = True

        if written:
            self.dest_stream.write("\n")

    def _write_snapshot(self, snap: Snapshot):
        if is_blank(snap.moves):
            return

        if not is_blank(snap.title):
            self.dest_stream.write(snap.title.strip() + "\n\n")

        self.dest_stream.write(snap.moves.strip() + "\n\n")

        written = True
        written = self._write_tagged(SOKTags.SOLVER, snap.solver) or written
        written = (
            self._write_tagged(SOKTags.SNAPSHOT_CREATED_AT, snap.created_at) or written
        )
        written = self._write_tagged(SOKTags.DURATION, snap.duration) or written

        snap_notes = "\n".join(snap.notes)
        if not is_blank(snap_notes):
            self.dest_stream.write(snap_notes.rstrip() + "\n")
            written = True

        if written:
            self.dest_stream.write("\n")

    def _write_tagged(self, tag: str, content: Optional[str]):
        if not content or is_blank(content) or is_blank(tag):
            return False

        self.dest_stream.write(tag.strip() + ": " + content.rstrip() + "\n")
        return True
