import pytest

from sokoenginepy.common import Direction
from sokoenginepy.snapshot import (AtomicMove, SnapshotConversionError,
                                   SnapshotStringParser)
from sokoenginepy.tessellation import tessellation_factory


@pytest.fixture
def parser():
    return SnapshotStringParser()


class DescribeSnapshotTextParser:

    class Describe_convert:

        def it_ignores_spaces_and_current_position_character(self, parser):
            success = parser.convert(
                "  \n **  \t l ", tessellation_factory("Sokoban")
            )
            assert success
            assert parser._resulting_solving_mode == 'forward'
            assert parser._resulting_moves == [AtomicMove(Direction.LEFT)]

        def it_accepts_blank_input_as_empty_forward_snapshot(self, parser):
            success = parser.convert(
                "  \n   \t  ", tessellation_factory("Sokoban")
            )
            assert success
            assert parser._resulting_solving_mode == 'forward'
            assert parser._resulting_moves == []

        def it_fails_on_non_snapshot_characters(self, parser):
            success = parser.convert("ZOMG! ", tessellation_factory("Sokoban"))
            assert not success
            assert parser._first_encountered_error == SnapshotConversionError.NON_SNAPSHOT_CHARACTERS_FOUND

        def it_sets_mode_to_reverse_if_jumps_are_found(self, parser):
            success = parser.convert("[lurd] ", tessellation_factory("Sokoban"))
            assert success
            for atomic_move in parser._resulting_moves:
                assert atomic_move.is_jump

        def it_ignores_empty_jump_and_pusher_selection_sequences(self, parser):
            success = parser.convert("[]lurd", tessellation_factory("Sokoban"))
            assert success
            assert len(parser._resulting_moves) == 4

        def it_detects_reverse_snapshot_while_ignoring_empty_jumps(
            self, parser
        ):
            success = parser.convert("[]lurd", tessellation_factory("Sokoban"))
            assert success
            assert parser._resulting_solving_mode == 'reverse'

        def it_fails_on_rle_errors(self, parser):
            success = parser.convert("((4l)", tessellation_factory("Sokoban"))
            assert not success
            assert parser._first_encountered_error == SnapshotConversionError.RLE_DECODING_ERROR

        def it_fails_on_non_matched_sequence_separators(self, parser):
            success = parser.convert("[lurd", tessellation_factory("Sokoban"))
            assert not success
            assert parser._first_encountered_error == SnapshotConversionError.TOKENIZATION_ERROR

        def it_fails_on_moves_illegal_in_context_of_requested_tessellation(
            self, parser
        ):
            success = parser.convert("Nlurd", tessellation_factory("Sokoban"))
            assert not success
            assert parser._first_encountered_error == SnapshotConversionError.NON_VARIANT_CHARACTERS_FOUND

        def it_correctly_detects_jumps(self, parser):
            success = parser.convert("[lurd] ", tessellation_factory("Sokoban"))
            assert success
            for atomic_move in parser._resulting_moves:
                assert atomic_move.is_jump

        def it_correctly_detects_pusher_selections(self, parser):
            success = parser.convert("{lurd} ", tessellation_factory("Sokoban"))
            assert success
            for atomic_move in parser._resulting_moves:
                assert atomic_move.is_pusher_selection

    class Describe_convert_token:

        def it_fails_on_moves_illegal_in_context_of_requested_tessellation(
            self, parser
        ):
            parser._convert_token("Nlurd", tessellation_factory("Sokoban"))
            assert parser._first_encountered_error == SnapshotConversionError.NON_VARIANT_CHARACTERS_FOUND

        def it_fails_on_jumps_that_contain_pushes(self, parser):
            parser._resulting_moves = []
            parser._convert_token(
                "lurD", tessellation_factory("Sokoban"), is_jump=True
            )
            assert parser._first_encountered_error == SnapshotConversionError.JUMP_CONTAINS_PUSHES

        def it_fails_on_pusher_selections_that_contain_pushes(self, parser):
            parser._resulting_moves = []
            parser._convert_token(
                "lurD", tessellation_factory("Sokoban"), is_pusher_change=True
            )
            assert parser._first_encountered_error == SnapshotConversionError.PUSHER_CHANGE_CONTAINS_PUSHES

        def it_appends_converted_moves_to_parser_resulting_moves(self, parser):
            parser._resulting_moves = []
            parser._convert_token("lurD", tessellation_factory("Sokoban"))
            assert (
                parser._resulting_moves == [
                    AtomicMove(Direction.LEFT), AtomicMove(Direction.UP),
                    AtomicMove(Direction.RIGHT), AtomicMove(
                        Direction.DOWN, box_moved=True
                    )
                ]
            )
