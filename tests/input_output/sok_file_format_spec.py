from helpers import TEST_RESOURCES_ROOT
from sokoenginepy.common import Variant, is_blank
from sokoenginepy.input_output import PuzzlesCollection, SOKFileFormat

INPUT_FILES_ROOT = TEST_RESOURCES_ROOT.child('test_data')


class DescribeSOKReader:

    def it_loads_regular_collection_file(self):
        collection = PuzzlesCollection()
        collection.load(INPUT_FILES_ROOT.child('Original_and_Extra.sok'))

        assert len(collection.puzzles) == 91
        assert len(collection.puzzles[0].snapshots) == 6

        assert collection.puzzles[0].title == 'Level 1'
        assert not is_blank(collection.notes)
        assert not is_blank(collection.puzzles[0].board)
        assert not is_blank(collection.puzzles[0].notes)
        assert not is_blank(collection.puzzles[0].snapshots[0].moves)

    def it_loads_puzzle_without_title(self):
        collection = PuzzlesCollection()
        collection.load(
            INPUT_FILES_ROOT.child('parser_test_puzzle_no_title.sok')
        )

        assert is_blank(collection.puzzles[0].title)
        assert not is_blank(collection.puzzles[0].board)

    def it_loads_puzzle_with_multiple_snapshots(self):
        collection = PuzzlesCollection()
        collection.load(
            INPUT_FILES_ROOT.child('parser_test_multiple_snapshots.sok')
        )

        assert len(collection.puzzles[0].snapshots) == 3
        assert collection.puzzles[0].snapshots[1].title == (
            "This is note for first snapshot, but parser " +
            "can't know that and should recognize it as heading of next snapshot."
        )

    def it_loads_last_snapshot_notes(self):
        collection = PuzzlesCollection()
        collection.load(
            INPUT_FILES_ROOT.child('parser_test_last_snapshot_notes.sok')
        )

        title = "This is note for last snapshot, not heading line"
        note = "but parser can't know that and should recognize it as heading line"

        assert collection.puzzles[1].title == title
        assert collection.puzzles[1].notes == note

    class describe_choosing_puzzle_variant:

        def it_defaults_to_sokoban_if_not_specified(self):
            collection = PuzzlesCollection()
            with open(
                INPUT_FILES_ROOT.
                child('parser_test_variant_type_not_specified.sok')
            ) as t:
                SOKFileFormat.read(t, collection, None)

            for puzzle in collection.puzzles:
                assert puzzle.variant == Variant.SOKOBAN

        def it_uses_value_from_colection_notes_even_if_hint_given(self):
            collection = PuzzlesCollection()
            with open(
                INPUT_FILES_ROOT.
                child('parser_test_variant_type_specified_global.sok')
            ) as t:
                SOKFileFormat.read(t, collection, Variant.OCTOBAN)

            for puzzle in collection.puzzles:
                assert puzzle.variant == Variant.TRIOBAN

        def it_snapshots_get_the_same_value_as_their_puzzle(self):
            collection = PuzzlesCollection()
            with open(
                INPUT_FILES_ROOT.
                child('parser_test_variant_type_specified_global.sok')
            ) as t:
                SOKFileFormat.read(t, collection, Variant.OCTOBAN)

            for puzzle in collection.puzzles:
                for snapshot in puzzle.snapshots:
                    assert snapshot.variant == puzzle.variant

        def it_uses_value_from_puzzle_notes_and_ignores_hint_and_collection_notes(
            self
        ):
            collection = PuzzlesCollection()
            with open(
                INPUT_FILES_ROOT.
                child('parser_test_variant_type_specified_puzzle1.sok')
            ) as t:
                SOKFileFormat.read(t, collection, Variant.OCTOBAN)

            assert collection.puzzles[0].variant == Variant.SOKOBAN
            assert collection.puzzles[1].variant == Variant.HEXOBAN

        def it_uses_value_from_hint_when_nothing_is_specified_in_file(self):
            collection = PuzzlesCollection()
            with open(
                INPUT_FILES_ROOT.
                child('parser_test_variant_type_specified_puzzle2.sok')
            ) as t:
                SOKFileFormat.read(t, collection, Variant.TRIOBAN)

            assert collection.puzzles[0].variant == Variant.TRIOBAN
            assert collection.puzzles[1].variant == Variant.HEXOBAN
