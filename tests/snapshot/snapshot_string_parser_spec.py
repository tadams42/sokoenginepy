import pytest

from sokoenginepy import AtomicMove, Direction, SolvingMode, Tessellation
from sokoenginepy.snapshot.snapshot_string_parser import SnapshotStringParser

from ..fixtures import SnapshotFactory


@pytest.fixture
def parser():
    return SnapshotStringParser()


@pytest.fixture
def sokoban_snapshot():
    return SnapshotFactory(
        tessellation_or_description=Tessellation.SOKOBAN,
        moves_data="lurdLURD{lurd}LURD",
    )


class DescribeSnapshotStringParser:
    class Describe_convert:
        def it_ignores_spaces_and_current_position_character(self, parser):
            success = parser._parse("  \n **  \t l ", Tessellation.SOKOBAN.value)
            assert success
            assert parser._resulting_solving_mode == SolvingMode.FORWARD
            assert parser._resulting_moves == [AtomicMove(Direction.LEFT)]

        def it_accepts_blank_input_as_empty_forward_snapshot(self, parser):
            success = parser._parse("  \n   \t  ", Tessellation.SOKOBAN.value)
            assert success
            assert parser._resulting_solving_mode == SolvingMode.FORWARD
            assert parser._resulting_moves == []

        def it_fails_on_non_snapshot_characters(self, parser):
            success = parser._parse("ZOMG! ", Tessellation.SOKOBAN.value)
            assert not success
            assert (
                parser._first_encountered_error
                == "Illegal characters found in snapshot string"
            )

        def it_sets_mode_to_reverse_if_jumps_are_found(self, parser):
            success = parser._parse("[lurd] ", Tessellation.SOKOBAN.value)
            assert success
            for atomic_move in parser._resulting_moves:
                assert atomic_move.is_jump

        def it_ignores_empty_jump_and_pusher_selection_sequences(self, parser):
            success = parser._parse("[]lurd", Tessellation.SOKOBAN.value)
            assert success
            assert len(parser._resulting_moves) == 4

        def it_detects_reverse_snapshot_while_ignoring_empty_jumps(self, parser):
            success = parser._parse("[]lurd", Tessellation.SOKOBAN.value)
            assert success
            assert parser._resulting_solving_mode == SolvingMode.REVERSE

        def it_fails_on_rle_errors(self, parser):
            success = parser._parse("((4l)", Tessellation.SOKOBAN.value)
            assert not success
            assert parser._first_encountered_error == "Rle decoding board string failed"

        def it_fails_on_non_matched_sequence_separators(self, parser):
            success = parser._parse("[lurd", Tessellation.SOKOBAN.value)
            assert not success
            assert (
                parser._first_encountered_error
                == "Tokenizing snapshot string elements failed. Maybe there are unmatched parentheses"
            )

        def it_fails_on_moves_illegal_in_context_of_requested_tessellation(
            self, parser
        ):
            success = parser._parse("Nlurd", Tessellation.SOKOBAN.value)
            assert not success
            assert (
                parser._first_encountered_error
                == "Snapshot string contains directions not supported by requested tessellation"
            )

        def it_correctly_detects_jumps(self, parser):
            success = parser._parse("[lurd] ", Tessellation.SOKOBAN.value)
            assert success
            for atomic_move in parser._resulting_moves:
                assert atomic_move.is_jump

        def it_correctly_detects_pusher_selections(self, parser):
            success = parser._parse("{lurd} ", Tessellation.SOKOBAN.value)
            assert success
            for atomic_move in parser._resulting_moves:
                assert atomic_move.is_pusher_selection

    class Describe_convert_token:
        def it_fails_on_moves_illegal_in_context_of_requested_tessellation(
            self, parser
        ):
            parser._convert_token("Nlurd", Tessellation.SOKOBAN.value)
            assert (
                parser._first_encountered_error
                == "Snapshot string contains directions not supported by requested tessellation"
            )

        def it_fails_on_jumps_that_contain_pushes(self, parser):
            parser._resulting_moves = []
            parser._convert_token("lurD", Tessellation.SOKOBAN.value, is_jump=True)
            assert (
                parser._first_encountered_error
                == "Jump sequence in snapshot string contains atomic pushes. This is not allowed"
            )

        def it_fails_on_pusher_selections_that_contain_pushes(self, parser):
            parser._resulting_moves = []
            parser._convert_token(
                "lurD", Tessellation.SOKOBAN.value, is_pusher_change=True
            )
            assert (
                parser._first_encountered_error
                == "Pusher change sequence in snapshot string contains atomic pushes. This is not allowed"
            )

        def it_appends_converted_moves_to_parser_resulting_moves(self, parser):
            parser._resulting_moves = []
            parser._convert_token("lurD", Tessellation.SOKOBAN.value)
            assert parser._resulting_moves == [
                AtomicMove(Direction.LEFT),
                AtomicMove(Direction.UP),
                AtomicMove(Direction.RIGHT),
                AtomicMove(Direction.DOWN, box_moved=True),
            ]

    class Describe_convert_from_string:
        def it_replaces_internal_data_with_atomic_moves_from_string(
            self, parser, sokoban_snapshot
        ):
            parser.convert_from_string("LURD", sokoban_snapshot)
            assert len(sokoban_snapshot) == 4
            assert sokoban_snapshot[0] == AtomicMove(Direction.LEFT, box_moved=True)
            assert sokoban_snapshot[1] == AtomicMove(Direction.UP, box_moved=True)
            assert sokoban_snapshot[2] == AtomicMove(Direction.RIGHT, box_moved=True)
            assert sokoban_snapshot[3] == AtomicMove(Direction.DOWN, box_moved=True)

        def it_raises_on_parsing_errors(self, parser, sokoban_snapshot):
            with pytest.raises(ValueError):
                parser.convert_from_string("42", sokoban_snapshot)
