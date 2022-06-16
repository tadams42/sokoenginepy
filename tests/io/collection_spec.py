import tempfile
import textwrap
from pathlib import Path

import pytest

from sokoenginepy.game import Tessellation
from sokoenginepy.io import Collection, is_blank, snapshot


@pytest.fixture
def input_files_root(resources_root):
    return resources_root / "test_data"


class DescribeCollection:
    def it_loads_regular_collection_file(self, input_files_root):
        collection = Collection()
        collection.load(input_files_root / "Original_and_Extra.sok")

        assert len(collection.puzzles) == 91
        assert len(collection.puzzles[0].snapshots) == 6

        assert collection.title == "Original & Extra"
        assert collection.author == "Thinking Rabbit"
        assert collection.created_at == "2005-03-30  01:05:06"
        assert collection.updated_at == "2012-10-20  09:48:22"
        assert list(collection.notes) == [
            "Originate from: original.slc",
            "",
            "Some collection notes",
        ]

        puzzle = collection.puzzles[0]
        assert puzzle.title == "Level 1"
        assert puzzle.author == "author name"
        assert puzzle.boxorder == "1 2 3 4 5 6"
        assert puzzle.goalorder == "6 5 4 3 2 1"
        assert list(puzzle.notes) == ["Time: 00:01:00", "", "Some puzzle notes"]
        assert not is_blank(puzzle.board)

        expected_board = (
            "\n".join(
                textwrap.dedent(
                    """
                    #####
                    #   #
                    #$  #
                  ###  $##
                  #  $ $ #
                ### # ## #   ######
                #   # ## #####  ..#
                # $  $          ..#
                ##### ### #@##  ..#
                    #     #########
                    #######
                """
                )
                .lstrip("\n")
                .splitlines()
            )
            + "\n"
        )
        assert puzzle.board == expected_board

        snapshot = puzzle.snapshots[0]
        assert list(snapshot.notes) == [
            "Some snapshot notes",
            "Optimizer: YASS 2.86",
            "Time: 00:00:47",
        ]
        expected_moves_data = "".join(
            _.strip()
            for _ in (
                """
                ullluuuLUllDlldddrRRRRRRRRRRRRlllllllllllllulldRRRRRRRRRRRRRdrUlllllll
                uuululldDDuulldddrRRRRRRRRRRuRRlDllllllluuulLulDDDuulldddrRRRRRRRRRRdR
                RlUllllllluuulluuurDDluulDDDDDuulldddrRRRRRRRRRRRllllllluuuLLulDDDuull
                dddrRRRRRRRRRRuRDldR
                """
            ).splitlines()
        )
        assert snapshot.moves_data == expected_moves_data
        assert snapshot.solver == "only human"

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
        assert list(collection.puzzles[1].notes) == [note]

    def it_correctly_loads_mixed_tessellations_collection(self, input_files_root):
        collection = Collection()
        collection.load(input_files_root / "mixed_collection.sok")

        assert (
            sum(1 for _ in collection.puzzles if _.tessellation == Tessellation.SOKOBAN)
            == 4
        )
        assert (
            sum(1 for _ in collection.puzzles if _.tessellation == Tessellation.HEXOBAN)
            == 5
        )

        for puzzle in collection.puzzles:
            for snapshot in puzzle.snapshots:
                assert puzzle.tessellation == snapshot.tessellation

    class describe_choosing_puzzle_variant:
        def it_defaults_to_sokoban_if_not_specified(self, input_files_root):
            collection = Collection()
            collection.load(
                input_files_root / "parser_test_variant_type_not_specified.sok"
            )

            for puzzle in collection.puzzles:
                assert puzzle.tessellation == Tessellation.SOKOBAN

        def it_uses_value_from_collection_notes_even_if_hint_given(
            self, input_files_root
        ):
            collection = Collection()
            collection.load(
                input_files_root / "parser_test_variant_type_specified_global.sok",
                Tessellation.OCTOBAN,
            )

            for puzzle in collection.puzzles:
                assert puzzle.tessellation == Tessellation.TRIOBAN

        def it_snapshots_get_the_same_value_as_their_puzzle(self, input_files_root):
            collection = Collection()
            collection.load(
                input_files_root / "parser_test_variant_type_specified_global.sok",
                Tessellation.OCTOBAN,
            )

            for puzzle in collection.puzzles:
                for snapshot in puzzle.snapshots:
                    assert snapshot.tessellation == puzzle.tessellation

        def it_uses_value_from_puzzle_notes_and_ignores_hint_and_collection_notes(
            self, input_files_root
        ):
            collection = Collection()
            collection.load(
                input_files_root / "parser_test_variant_type_specified_puzzle1.sok",
                Tessellation.OCTOBAN,
            )

            assert collection.puzzles[0].tessellation == Tessellation.SOKOBAN
            assert collection.puzzles[1].tessellation == Tessellation.HEXOBAN

        def it_uses_value_from_hint_when_nothing_is_specified_in_file(
            self, input_files_root
        ):
            collection = Collection()
            collection.load(
                input_files_root / "parser_test_variant_type_specified_puzzle2.sok",
                Tessellation.TRIOBAN,
            )

            assert collection.puzzles[0].tessellation == Tessellation.TRIOBAN
            assert collection.puzzles[1].tessellation == Tessellation.HEXOBAN

    def it_correctly_writes_collection(self, input_files_root):
        original = Collection()
        original.load(input_files_root / "Original_and_Extra.sok")

        loaded = Collection()
        with tempfile.TemporaryDirectory() as dir_path:
            file_path = Path(dir_path) / "saved_original_and_extra.sok"
            original.save(file_path)
            loaded.load(file_path)

        assert len(original.puzzles) == len(loaded.puzzles)
        for attr in {"title", "author", "created_at", "updated_at", "notes"}:
            assert getattr(original, attr) == getattr(
                loaded, attr
            ), f"Mismatched Collection.{attr}"

        for p_idx in range(len(original.puzzles)):
            original_p = original.puzzles[p_idx]
            loaded_p = loaded.puzzles[p_idx]

            for attr in {
                "title",
                "author",
                "boxorder",
                "goalorder",
                "notes",
                "board",
            }:
                assert getattr(original_p, attr) == getattr(
                    loaded_p, attr
                ), f'Mismatched Puzzle.{attr} for puzzle "{original_p.title}"'

            assert len(original_p.snapshots) == len(loaded_p.snapshots)
            for s_idx in range(len(original_p.snapshots)):
                original_s = original_p.snapshots[s_idx]
                loaded_s = loaded_p.snapshots[s_idx]

                for attr in {"title", "solver", "notes", "moves_data"}:
                    assert getattr(original_s, attr) == getattr(loaded_s, attr), (
                        f"Mismatched Snapshot.{attr} for snapshot {original_p.title}: "
                        f"{original_s.title or s_idx}"
                    )
