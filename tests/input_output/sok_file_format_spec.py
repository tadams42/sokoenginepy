import os

import pytest

from sokoenginepy import PuzzlesCollection, SOKFileFormat, Tessellation
from sokoenginepy.utilities import is_blank


@pytest.fixture
def input_files_root(resources_root):
    return os.path.join(resources_root, "test_data")


class DescribeSOKReader:
    def it_loads_regular_collection_file(self, input_files_root):
        collection = PuzzlesCollection()
        collection.load(os.path.join(input_files_root, "Original_and_Extra.sok"))

        assert len(collection.puzzles) == 91
        assert len(collection.puzzles[0].snapshots) == 6

        assert collection.puzzles[0].title == "Level 1"
        assert not is_blank(collection.notes)
        assert not is_blank(collection.puzzles[0].board)
        assert not is_blank(collection.puzzles[0].notes)
        assert not is_blank(collection.puzzles[0].snapshots[0].moves)

    def it_loads_puzzle_without_title(self, input_files_root):
        collection = PuzzlesCollection()
        collection.load(
            os.path.join(input_files_root, "parser_test_puzzle_no_title.sok")
        )

        assert is_blank(collection.puzzles[0].title)
        assert not is_blank(collection.puzzles[0].board)

    def it_loads_puzzle_with_multiple_snapshots(self, input_files_root):
        collection = PuzzlesCollection()
        collection.load(
            os.path.join(input_files_root, "parser_test_multiple_snapshots.sok")
        )

        assert len(collection.puzzles[0].snapshots) == 3
        assert collection.puzzles[0].snapshots[1].title == (
            "This is note for first snapshot, but parser "
            + "can't know that and should recognize it as heading of next snapshot."
        )

    def it_loads_last_snapshot_notes(self, input_files_root):
        collection = PuzzlesCollection()
        collection.load(
            os.path.join(input_files_root, "parser_test_last_snapshot_notes.sok")
        )

        title = "This is note for last snapshot, not heading line"
        note = "but parser can't know that and should recognize it as heading line"

        assert collection.puzzles[1].title == title
        assert collection.puzzles[1].notes == note

    class describe_choosing_puzzle_variant:
        def it_defaults_to_sokoban_if_not_specified(self, input_files_root):
            collection = PuzzlesCollection()
            with open(
                os.path.join(
                    input_files_root, "parser_test_variant_type_not_specified.sok"
                )
            ) as t:
                SOKFileFormat.read(t, collection, None)

            for puzzle in collection.puzzles:
                assert puzzle.tessellation == Tessellation.SOKOBAN.value

        def it_uses_value_from_colection_notes_even_if_hint_given(
            self, input_files_root
        ):
            collection = PuzzlesCollection()
            with open(
                os.path.join(
                    input_files_root, "parser_test_variant_type_specified_global.sok"
                )
            ) as t:
                SOKFileFormat.read(t, collection, Tessellation.OCTOBAN)

            for puzzle in collection.puzzles:
                assert puzzle.tessellation == Tessellation.TRIOBAN.value

        def it_snapshots_get_the_same_value_as_their_puzzle(self, input_files_root):
            collection = PuzzlesCollection()
            with open(
                os.path.join(
                    input_files_root, "parser_test_variant_type_specified_global.sok"
                )
            ) as t:
                SOKFileFormat.read(t, collection, Tessellation.OCTOBAN)

            for puzzle in collection.puzzles:
                for snapshot in puzzle.snapshots:
                    assert snapshot.tessellation == puzzle.tessellation

        def it_uses_value_from_puzzle_notes_and_ignores_hint_and_collection_notes(
            self, input_files_root
        ):
            collection = PuzzlesCollection()
            with open(
                os.path.join(
                    input_files_root, "parser_test_variant_type_specified_puzzle1.sok"
                )
            ) as t:
                SOKFileFormat.read(t, collection, Tessellation.OCTOBAN)

            assert collection.puzzles[0].tessellation == Tessellation.SOKOBAN.value
            assert collection.puzzles[1].tessellation == Tessellation.HEXOBAN.value

        def it_uses_value_from_hint_when_nothing_is_specified_in_file(
            self, input_files_root
        ):
            collection = PuzzlesCollection()
            with open(
                os.path.join(
                    input_files_root, "parser_test_variant_type_specified_puzzle2.sok"
                )
            ) as t:
                SOKFileFormat.read(t, collection, Tessellation.TRIOBAN)

            assert collection.puzzles[0].tessellation == Tessellation.TRIOBAN.value
            assert collection.puzzles[1].tessellation == Tessellation.HEXOBAN.value
