from hamcrest import assert_that, equal_to
from sokoenginepy.io import is_blank, SOKFileFormat
from sokoenginepy import PuzzlesCollection, Variant
from helpers import TEST_RESOURCES_ROOT


INPUT_FILES_ROOT = TEST_RESOURCES_ROOT.child('test_data')


class DescribeSOKReader(object):
    def test_loads_regular_collection_file(self):
        collection = PuzzlesCollection()
        collection.load(INPUT_FILES_ROOT.child('Original_and_Extra.sok'))

        assert_that(len(collection.puzzles), equal_to(91))
        assert_that(len(collection.puzzles[0].snapshots), equal_to(6))

        assert_that(collection.puzzles[0].title, equal_to('Level 1'))
        assert_that(is_blank(collection.notes), equal_to(False))
        assert_that(is_blank(collection.puzzles[0].board), equal_to(False))
        assert_that(is_blank(collection.puzzles[0].notes), equal_to(False))
        assert_that(is_blank(collection.puzzles[0].snapshots[0].moves),
                    equal_to(False))

    def test_loads_puzzle_without_title(self):
        collection = PuzzlesCollection()
        collection.load(INPUT_FILES_ROOT.child('parser_test_puzzle_no_title.sok'))

        assert_that(is_blank(collection.puzzles[0].title), equal_to(True))
        assert_that(is_blank(collection.puzzles[0].board), equal_to(False))

    def test_loads_puzzle_with_multiple_snapshots(self):
        collection = PuzzlesCollection()
        collection.load(INPUT_FILES_ROOT.child('parser_test_multiple_snapshots.sok'))

        assert_that(len(collection.puzzles[0].snapshots), equal_to(3))
        assert_that(collection.puzzles[0].snapshots[1].title, equal_to(
            "This is note for first snapshot, but parser " +
            "can't know that and should recognize it as heading of next snapshot."
        ))

    def test_loads_last_snapshot_notes(self):
        collection = PuzzlesCollection()
        collection.load(INPUT_FILES_ROOT.child('parser_test_last_snapshot_notes.sok'))

        title = "This is note for last snapshot, not heading line"
        note = "but parser can't know that and should recognize it as heading line"

        assert_that(collection.puzzles[1].title, equal_to(title))
        assert_that(collection.puzzles[1].notes, equal_to(note))

    class describe_choosing_puzzle_variant(object):
        def test_defaults_to_sokoban_if_not_specified(self):
            collection = PuzzlesCollection()
            with open(INPUT_FILES_ROOT.child('parser_test_variant_type_not_specified.sok')) as t:
                SOKFileFormat.read(t, collection, None)

            for puzzle in collection.puzzles:
                assert_that(puzzle.variant, equal_to(Variant.SOKOBAN))

        def test_uses_value_from_colection_notes_even_if_hint_given(self):
            collection = PuzzlesCollection()
            with open(INPUT_FILES_ROOT.child('parser_test_variant_type_specified_global.sok')) as t:
                SOKFileFormat.read(t, collection, Variant.OCTOBAN)

            for puzzle in collection.puzzles:
                assert_that(puzzle.variant, equal_to(Variant.TRIOBAN))

        def test_snapshots_get_the_same_value_as_their_puzzle(self):
            collection = PuzzlesCollection()
            with open(INPUT_FILES_ROOT.child('parser_test_variant_type_specified_global.sok')) as t:
                SOKFileFormat.read(t, collection, Variant.OCTOBAN)

            for puzzle in collection.puzzles:
                for snapshot in puzzle.snapshots:
                    assert_that(snapshot.variant, equal_to(puzzle.variant))

        def test_uses_value_from_puzzle_notes_and_ignores_hint_and_collection_notes(self):
            collection = PuzzlesCollection()
            with open(INPUT_FILES_ROOT.child('parser_test_variant_type_specified_puzzle1.sok')) as t:
                SOKFileFormat.read(t, collection, Variant.OCTOBAN)

            assert_that(collection.puzzles[0].variant, equal_to(Variant.SOKOBAN))
            assert_that(collection.puzzles[1].variant, equal_to(Variant.HEXOBAN))

        def test_uses_value_from_hint_when_nothing_is_specified_in_file(self):
            collection = PuzzlesCollection()
            with open(INPUT_FILES_ROOT.child('parser_test_variant_type_specified_puzzle2.sok')) as t:
                SOKFileFormat.read(t, collection, Variant.TRIOBAN)

            assert_that(collection.puzzles[0].variant, equal_to(Variant.TRIOBAN))
            assert_that(collection.puzzles[1].variant, equal_to(Variant.HEXOBAN))
