import os
import re
from enum import Enum

import arrow

from .. import utilities
from ..board import VariantBoard
from ..snapshot import Snapshot
from ..tessellation import Tessellation
from .puzzle import Puzzle, PuzzleSnapshot


class SOKFileFormat:
    @classmethod
    def read(cls, src_stream, dest_collection, tessellation_hint=Tessellation.SOKOBAN):
        SOKReader(src_stream, dest_collection, tessellation_hint).read()

    @classmethod
    def write(cls, puzzle_or_collection, dest_stream):
        SOKWriter(dest_stream).write(puzzle_or_collection)


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
    def __init__(self, src_stream, dest_collection, tessellation_hint):
        self.coll_header_tessellation_hint = None
        self.src_stream = src_stream
        self.dest_collection = dest_collection
        self.supplied_tessellation_hint = str(
            Tessellation.instance_from(tessellation_hint).value
        ).lower()

    def read(self):
        self.src_stream.seek(0, 0)
        self.dest_collection.clear()
        self._split_input(self.src_stream.readlines())
        self._parse_title_lines()
        self._parse_collection_notes()
        self._parse_puzzles()

    def _split_input(self, input_lines):
        first_board_line = utilities.first_index_of(
            input_lines, VariantBoard.is_board_string
        )
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

            first_note_line = utilities.first_index_of(
                remaining_lines, lambda x: not VariantBoard.is_board_string(x)
            )
            if first_note_line is not None:
                puzzle.board = "".join(remaining_lines[:first_note_line])
                remaining_lines = remaining_lines[first_note_line:]
            else:
                puzzle.board = "".join(remaining_lines)
                remaining_lines = []

            if len(remaining_lines) > 0:
                first_board_line = utilities.first_index_of(
                    remaining_lines, VariantBoard.is_board_string
                )

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

            first_moves_line = utilities.first_index_of(
                remaining_lines, Snapshot.is_snapshot_string
            )
            if first_moves_line is not None:
                puzzle.notes = remaining_lines[:first_moves_line]
                remaining_lines = remaining_lines[first_moves_line:]
            else:
                puzzle.notes = remaining_lines
                remaining_lines = []

            puzzle.snapshots = []

            while len(remaining_lines) > 0:
                snap = PuzzleSnapshot()

                first_note_line = utilities.first_index_of(
                    remaining_lines, lambda x: not Snapshot.is_snapshot_string(x)
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
                    first_moves_line = utilities.first_index_of(
                        remaining_lines, Snapshot.is_snapshot_string
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

    def _get_tag_data(self, tag, line):
        # TODO: If tag data contains split char, it will not get collected
        # ie. "Date created: 2015-02-03 13:42:32"
        components = self._tag_splitter.split(str(line))
        if components[0].strip().lower() == tag.strip().lower():
            return components[1].strip()
        return None

    @staticmethod
    def _is_tagged_as(tag, line):
        return any(
            chr in list(SOKTags.TAG_DELIMITERS) for chr in line
        ) and line.lstrip().lower().startswith(tag.strip().lower())

    def _is_collection_tag_line(self, line):
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

    def _is_puzzle_tag_line(self, line):
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

    def _is_snapshot_tag_line(self, line):
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
    def _is_raw_file_notes_line(line):
        return line.lstrip().startswith(SOKTags.RAW_FILE_NOTES)

    def _notes_before_puzzle(self, puzzle_index):
        if puzzle_index == 0:
            return self.dest_collection.notes
        prevoius_puzzle = self.dest_collection.puzzles[puzzle_index - 1]
        if len(prevoius_puzzle.snapshots) > 0:
            return prevoius_puzzle.snapshots[-1].notes
        return prevoius_puzzle.notes

    def _notes_before_snapshot(self, puzzle_index, snapshot_index):
        puzzle = self.dest_collection.puzzles[puzzle_index]
        if snapshot_index == 0:
            return puzzle.notes
        return puzzle.snapshots[snapshot_index - 1].notes

    @staticmethod
    def _get_and_remove_title_line(notes):
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
        candidate_index = utilities.last_index_of(
            notes, lambda x: not utilities.is_blank(x)
        )
        if candidate_index is None:
            return ""

        preceeding_index = None
        if candidate_index > 0:
            preceeding_index = candidate_index - 1

        following_index = None
        if candidate_index < len(notes) - 1:
            following_index = candidate_index + 1

        preceeding_ok = (
            utilities.is_blank(notes[preceeding_index]) if preceeding_index else True
        )

        following_ok = (
            utilities.is_blank(notes[following_index]) if following_index else True
        )

        if preceeding_ok and following_ok:
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
        self.coll_header_tessellation_hint = None

        remaining_lines = []
        for line in self.dest_collection.notes:
            if self._is_collection_tag_line(line):
                self.coll_header_tessellation_hint = (
                    self.coll_header_tessellation_hint
                    or self._get_tag_data(SOKTags.VARIANT, line)
                )
                self.dest_collection.title = (
                    self.dest_collection.title
                    or self._get_tag_data(SOKTags.TITLE, line)
                )
                self.dest_collection.author = (
                    self.dest_collection.author
                    or self._get_tag_data(SOKTags.AUTHOR, line)
                )
                self.dest_collection.created_at = (
                    self.dest_collection.created_at
                    or self._get_tag_data(SOKTags.CREATED_AT, line)
                )
                self.dest_collection.updated_at = (
                    self.dest_collection.updated_at
                    or self._get_tag_data(SOKTags.UPDATED_AT, line)
                )
            elif not self._is_raw_file_notes_line(line):
                remaining_lines.append(line)

        if self.coll_header_tessellation_hint:
            self.coll_header_tessellation_hint = (
                self.coll_header_tessellation_hint.strip().lower()
            )

        self.dest_collection.notes = self._cleanup_whitespace(remaining_lines)

    def _parse_puzzles(self):
        for puzzle in self.dest_collection.puzzles:
            remaining_lines = []
            tess = None
            for line in puzzle.notes:
                if self._is_puzzle_tag_line(line):
                    tess = tess or self._get_tag_data(SOKTags.VARIANT, line)
                    puzzle.title = puzzle.title or self._get_tag_data(
                        SOKTags.TITLE, line
                    )
                    puzzle.author = puzzle.author or self._get_tag_data(
                        SOKTags.AUTHOR, line
                    )
                    puzzle.boxorder = puzzle.boxorder or self._get_tag_data(
                        SOKTags.BOXORDER, line
                    )
                    puzzle.goalorder = puzzle.goalorder or self._get_tag_data(
                        SOKTags.GOALORDER, line
                    )
                else:
                    remaining_lines.append(line)

            puzzle.notes = self._cleanup_whitespace(remaining_lines)

            if tess is not None:
                puzzle.tessellation = tess
            elif self.coll_header_tessellation_hint is not None:
                puzzle.tessellation = self.coll_header_tessellation_hint
            elif self.supplied_tessellation_hint is not None:
                puzzle.tessellation = self.supplied_tessellation_hint

            self._parse_snapshots(puzzle)

    def _parse_snapshots(self, puzzle):
        for snap in puzzle.snapshots:
            remaining_lines = []
            for line in snap.notes:
                if self._is_snapshot_tag_line(line):
                    snap.solver = snap.solver or self._get_tag_data(
                        SOKTags.AUTHOR, line
                    )
                    snap.solver = snap.solver or self._get_tag_data(
                        SOKTags.SOLVER, line
                    )
                    snap.created_at = snap.created_at or self._get_tag_data(
                        SOKTags.CREATED_AT, line
                    )
                    snap.duration = snap.duration or self._get_tag_data(
                        SOKTags.DURATION, line
                    )
                    snap.created_at = snap.created_at or self._get_tag_data(
                        SOKTags.SNAPSHOT_CREATED_AT, line
                    )
                else:
                    remaining_lines.append(line)

            snap.notes = self._cleanup_whitespace(remaining_lines)
            snap.tessellation = puzzle.tessellation

    @staticmethod
    def _cleanup_whitespace(lst):
        i = utilities.first_index_of(lst, lambda x: not utilities.is_blank(x))
        if i is None:
            return ""
        lst = lst[i:]

        i = utilities.last_index_of(lst, lambda x: not utilities.is_blank(x))
        if i is not None:
            lst = lst[: i + 1]

        return "\n".join(line.strip() for line in lst)


class SOKWriter:
    def __init__(self, dest_stream):
        self.dest_stream = dest_stream

    def write(self, puzzle_or_collection):
        if isinstance(puzzle_or_collection, Puzzle):
            self._write_puzzle(puzzle_or_collection)
        else:
            self._write_collection(puzzle_or_collection)

    def _write_collection(self, puzzle_collection):
        self._write_collection_header(puzzle_collection)
        for puzzle in puzzle_collection.puzzles:
            self._write_puzzle(puzzle)

    def _write_puzzle(self, puzzle):
        if utilities.is_blank(puzzle.board):
            return

        if not utilities.is_blank(puzzle.title):
            self.dest_stream.write(puzzle.title.strip() + "\n\n")

        self.dest_stream.write(puzzle.board.rstrip() + "\n\n")

        written = False

        if puzzle.tessellation != Tessellation.SOKOBAN:
            written = (
                self._write_tagged(SOKTags.VARIANT, str(puzzle.tessellation)) or written
            )

        if not utilities.is_blank(puzzle.boxorder) and not utilities.is_blank(
            puzzle.goalorder
        ):

            written = self._write_tagged(SOKTags.BOXORDER, puzzle.boxorder) or written
            written = self._write_tagged(SOKTags.GOALORDER, puzzle.goalorder) or written

        if not utilities.is_blank(puzzle.notes):
            self.dest_stream.write(puzzle.notes.rstrip() + "\n")
            written = True

        if written:
            self.dest_stream.write("\n")

        for snap in puzzle.snapshots:
            self._write_snapshot(snap)

    def _write_collection_header(self, puzzle_collection):

        for line in open(
            os.path.join(utilities.RESOURCES_ROOT, "SOK_format_specification.txt")
        ):
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

        if not utilities.is_blank(puzzle_collection.notes):
            self.dest_stream.write(puzzle_collection.notes.rstrip() + "\n")
            written = True

        if written:
            self.dest_stream.write("\n")

    def _write_snapshot(self, snap):
        if utilities.is_blank(snap.moves):
            return

        if not utilities.is_blank(snap.title):
            self.dest_stream.write(snap.title.strip() + "\n\n")

        self.dest_stream.write(snap.moves.strip() + "\n\n")

        written = True
        written = self._write_tagged(SOKTags.SOLVER, snap.solver) or written
        written = (
            self._write_tagged(SOKTags.SNAPSHOT_CREATED_AT, snap.created_at) or written
        )
        written = self._write_tagged(SOKTags.DURATION, snap.duration) or written

        if not utilities.is_blank(snap.notes):
            self.dest_stream.write(snap.notes.rstrip() + "\n")
            written = True

        if written:
            self.dest_stream.write("\n")

    def _write_tagged(self, tag, content):
        if utilities.is_blank(content) or utilities.is_blank(tag):
            return False

        self.dest_stream.write(tag.strip() + ": " + content.rstrip() + "\n")
        return True
