import pytest
from sokoenginepy.io import Collection, PuzzleTypes, is_blank


@pytest.fixture
def input_files_root(resources_root):
    return resources_root / "test_data"


class DescribeSOKReader:
    def it_loads_regular_collection_file(self, input_files_root):
        collection = Collection()
        collection.load(input_files_root / "Original_and_Extra.sok")

        assert len(collection.puzzles) == 91
        assert len(collection.puzzles[0].snapshots) == 6

        assert collection.puzzles[0].title == "Level 1"
        assert not is_blank("\n".join(collection.notes))
        assert not is_blank(collection.puzzles[0].board)
        assert not is_blank("\n".join(collection.puzzles[0].notes))
        assert not is_blank(collection.puzzles[0].snapshots[0].moves)

    def it_loads_puzzle_without_title(self, input_files_root):
        collection = Collection()
        collection.load(input_files_root / "parser_test_puzzle_no_title.sok")

        assert is_blank(collection.puzzles[0].title)
        assert not is_blank(collection.puzzles[0].board)

    def it_loads_puzzle_with_multiple_snapshots(self, input_files_root):
        collection = Collection()
        collection.load(input_files_root / "parser_test_multiple_snapshots.sok")

        assert len(collection.puzzles[0].snapshots) == 3
        assert collection.puzzles[0].snapshots[1].title == (
            "This is note for first snapshot, but parser "
            + "can't know that and should recognize it as heading of next snapshot."
        )

    def it_loads_last_snapshot_notes(self, input_files_root):
        collection = Collection()
        collection.load(input_files_root / "parser_test_last_snapshot_notes.sok")

        title = "This is note for last snapshot, not heading line"
        note = "but parser can't know that and should recognize it as heading line"

        assert collection.puzzles[1].title == title
        assert collection.puzzles[1].notes == [note]

    class describe_choosing_puzzle_variant:
        def it_defaults_to_sokoban_if_not_specified(self, input_files_root):
            collection = Collection()
            collection.load(
                input_files_root / "parser_test_variant_type_not_specified.sok"
            )

            for puzzle in collection.puzzles:
                assert puzzle.puzzle_type == PuzzleTypes.SOKOBAN

        def it_uses_value_from_collection_notes_even_if_hint_given(
            self, input_files_root
        ):
            collection = Collection()
            collection.load(
                input_files_root / "parser_test_variant_type_specified_global.sok",
                PuzzleTypes.OCTOBAN,
            )

            for puzzle in collection.puzzles:
                assert puzzle.puzzle_type == PuzzleTypes.TRIOBAN

        def it_snapshots_get_the_same_value_as_their_puzzle(self, input_files_root):
            collection = Collection()
            collection.load(
                input_files_root / "parser_test_variant_type_specified_global.sok",
                PuzzleTypes.OCTOBAN,
            )

            for puzzle in collection.puzzles:
                for snapshot in puzzle.snapshots:
                    assert snapshot.puzzle_type == puzzle.puzzle_type

        def it_uses_value_from_puzzle_notes_and_ignores_hint_and_collection_notes(
            self, input_files_root
        ):
            collection = Collection()
            collection.load(
                input_files_root / "parser_test_variant_type_specified_puzzle1.sok",
                PuzzleTypes.OCTOBAN,
            )

            assert collection.puzzles[0].puzzle_type == PuzzleTypes.SOKOBAN
            assert collection.puzzles[1].puzzle_type == PuzzleTypes.HEXOBAN

        def it_uses_value_from_hint_when_nothing_is_specified_in_file(
            self, input_files_root
        ):
            collection = Collection()
            collection.load(
                input_files_root / "parser_test_variant_type_specified_puzzle2.sok",
                PuzzleTypes.TRIOBAN,
            )

            assert collection.puzzles[0].puzzle_type == PuzzleTypes.TRIOBAN
            assert collection.puzzles[1].puzzle_type == PuzzleTypes.HEXOBAN
