import pytest

from sokoenginepy import BoardConversionError, AtomicMove,\
    Direction, SnapshotConversionError

from sokoenginepy.core import Tessellation

from sokoenginepy.io import *
from sokoenginepy.io.text_utils import Rle


class Describe_is_board_string:
    input = "0123456789\n\t bB$*p_pmM@+#_-|"

    def it_recognizes_board_string(self):
        assert is_board_string(self.input)

    def it_fails_on_illegal_characters(self):
        assert not is_board_string(self.input + "z")

    def it_fails_on_numeric_string(self):
        assert not is_board_string("42")

    def it_fails_on_blank_string(self):
        assert not is_board_string("")
        assert not is_board_string("    ")
        assert not is_board_string("   \r\n ")


class Describe_is_snapshot_string:
    input = "0123456789\n\t lurdLURDnwseNWSE"

    def it_recognizes_snapshot_string(self):
        assert is_snapshot_string(self.input)

    def it_fails_on_illegal_characters(self):
        assert not is_board_string(self.input + "z")

    def it_fails_on_numeric_string(self):
        assert not is_board_string("42")

    def it_fails_on_blank_string(self):
        assert not is_board_string("")
        assert not is_board_string("    ")
        assert not is_board_string("   \r\n ")


class Describe_is_pusher:

    def it_correctly_categorizes(self):
        assert is_pusher(BoardEncodingCharacters.PUSHER)
        assert is_pusher(BoardEncodingCharacters.ALT_PUSHER1)
        assert is_pusher(BoardEncodingCharacters.ALT_PUSHER2)
        assert is_pusher(BoardEncodingCharacters.PUSHER_ON_GOAL)
        assert is_pusher(BoardEncodingCharacters.ALT_PUSHER_ON_GOAL1)
        assert is_pusher(BoardEncodingCharacters.ALT_PUSHER_ON_GOAL2)


class Describe_is_box:

    def it_correctly_categorizes(self):
        assert is_box(BoardEncodingCharacters.BOX)
        assert is_box(BoardEncodingCharacters.ALT_BOX1)
        assert is_box(BoardEncodingCharacters.BOX_ON_GOAL)
        assert is_box(BoardEncodingCharacters.ALT_BOX_ON_GOAL1)


class Describe_is_goal:

    def it_correctly_categorizes(self):
        assert is_goal(BoardEncodingCharacters.GOAL)
        assert is_goal(BoardEncodingCharacters.ALT_GOAL1)
        assert is_goal(BoardEncodingCharacters.PUSHER_ON_GOAL)
        assert is_goal(BoardEncodingCharacters.ALT_PUSHER_ON_GOAL1)
        assert is_goal(BoardEncodingCharacters.ALT_PUSHER_ON_GOAL2)
        assert is_goal(BoardEncodingCharacters.BOX_ON_GOAL)
        assert is_goal(BoardEncodingCharacters.ALT_BOX_ON_GOAL1)


class Describe_is_empty_floor:

    def it_correctly_categorizes(self):
        assert is_empty_floor(BoardEncodingCharacters.FLOOR)
        assert is_empty_floor(BoardEncodingCharacters.VISIBLE_FLOOR)
        assert is_empty_floor(BoardEncodingCharacters.ALT_VISIBLE_FLOOR1)


class Describe_is_wall:

    def it_correctly_categorizes(self):
        assert is_wall(BoardEncodingCharacters.WALL)


class Describe_parse_board_string:

    def it_parses_regular_board(self):
        src = " ##########\n    \n" +\
              " ## @ *   #\n" +\
              "##  $ ####\n" +\
              "# $.+ #\n" +\
              "#######\n"
        result = [
            " ##########",
            "           ",
            " ## @ *   #",
            "##  $ #### ",
            "# $.+ #    ",
            "#######    ",
            "           ",
        ]
        parsed = parse_board_string(src)
        assert parsed == result

    def it_parses_RLE_board(self):
        src = " ##########   |" +\
              " ## @ *   #|" +\
              "##  $ ####|" +\
              "# $.+ #|||" +\
              "#######   |"
        result = [
            " ##########   ",
            " ## @ *   #   ",
            "##  $ ####    ",
            "# $.+ #       ",
            "              ",
            "              ",
            "#######       ",
            "              ",
        ]
        parsed = parse_board_string(src)
        assert parsed == result

    def it_raises_on_illegal_characters(self):
        src = " ##########\n\n" +\
              " ##       #\n" +\
              "##   z####\n" +\
              "#   a #\n" +\
              "#######\n"
        with pytest.raises(BoardConversionError):
            parse_board_string(src)

    def it_discards_empty_but_not_blank_lines(self):
        src = " ##########\n    \n\n" +\
              " ## @ *   #\n\n" +\
              "##  $ ####\n\n" +\
              "# $.+ #\n\n" +\
              "#######\n\n"
        result = [
            " ##########",
            "           ",
            "           ",
            " ## @ *   #",
            "           ",
            "##  $ #### ",
            "           ",
            "# $.+ #    ",
            "           ",
            "#######    ",
            "           ",
            "           ",
        ]
        parsed = parse_board_string(src)
        assert parsed == result

    def test_id_discards_blank_boards(self):
        src = "              "
        parsed = parse_board_string(src)
        assert parsed == []


class DescribeRle:

    class Describe_decode_rle_token:

        def it_decodes_rle_token(self):
            assert Rle.decode_rle_token("4a4b2cd3e") == "aaaabbbbccdeee"
            assert Rle.decode_rle_token(
                "4a4b2cd3efghij"
            ) == "aaaabbbbccdeeefghij"
            assert Rle.decode_rle_token("4a4b2cd3ef") == "aaaabbbbccdeeef"
            assert Rle.decode_rle_token("4a2bf2b2cd3e") == "aaaabbfbbccdeee"
            assert Rle.decode_rle_token(
                "4a2bfghij2b2cd3e"
            ) == "aaaabbfghijbbccdeee"
            assert Rle.decode_rle_token(" 10a3 ") == " aaaaaaaaaa   "
            assert Rle.decode_rle_token("ccc") == "ccc"

        def it_preserves_ending_digits(self):
            assert Rle.decode_rle_token("3a4b44") == "aaabbbb44"


class Describe_rle_encode:

    def it_rle_encodes_string(self):
        assert rle_encode("aaaabbbbccdeee") == "4a4b2cd3e"
        assert rle_encode("aaaabbbbccdeeefghij") == "4a4b2cd3efghij"
        assert rle_encode("aaaabbbbccdeeef") == "4a4b2cd3ef"
        assert rle_encode("aaaabbfbbccdeee") == "4a2bf2b2cd3e"
        assert rle_encode("aaaabbfghijbbccdeee") == "4a2bfghij2b2cd3e"
        assert rle_encode(" aaaaaaaaaa   ") == " 10a3 "
        assert rle_encode("   ") == "3 "
        assert rle_encode("1234567890") == "1234567890"


class Describe_rle_decode:

    def it_decodes_rle_string(self):
        assert rle_decode("4a4b2cd3e") == "aaaabbbbccdeee"
        assert rle_decode("4a4b2cd3efghij") == "aaaabbbbccdeeefghij"
        assert rle_decode("4a4b2cd3ef") == "aaaabbbbccdeeef"
        assert rle_decode("4a2bf2b2cd3e") == "aaaabbfbbccdeee"
        assert rle_decode("4a2bfghij2b2cd3e") == "aaaabbfghijbbccdeee"
        assert rle_decode(" 10a3 ") == " aaaaaaaaaa   "
        assert rle_decode("ccc") == "ccc"

    def it_decodes_grouped_rle_string(self):
        assert rle_decode(
            "2abc3def3(adfdf)2abc3def"
        ) == "aabcdddefadfdfadfdfadfdfaabcdddef"
        assert rle_decode(
            "2abc3def3(2a3bc)2abc3def"
        ) == "aabcdddefaabbbcaabbbcaabbbcaabcdddef"
        assert rle_decode(
            "2abc3def2(fdsfs2(dfgh)gtr)2abc3def"
        ) == "aabcdddeffdsfsdfghdfghgtrfdsfsdfghdfghgtraabcdddef"
        assert rle_decode(
            "2abc3def2(2a2bc2(2a3b)2d)2abc3def"
        ) == "aabcdddefaabbcaabbbaabbbddaabbcaabbbaabbbddaabcdddef"
        assert rle_decode("2(abcd)efgh") == "abcdabcdefgh"
        assert rle_decode("2(3abcd)efgh") == "aaabcdaaabcdefgh"
        assert rle_decode("2(abcd)3efgh") == "abcdabcdeeefgh"
        assert rle_decode("(abcd)3efgh") == "abcdeeefgh"
        assert rle_decode("(ab3cd)efgh") == "abcccdefgh"
        assert rle_decode("(ab2(3c)d)efgh") == "abccccccdefgh"
        assert rle_decode("efgh(ab3cd)") == "efghabcccd"


@pytest.fixture
def parser():
    return SnapshotStringParser()


class DescribeSnapshotTextParser:

    class Describe_convert:

        def it_ignores_spaces_and_current_position_character(self, parser):
            success = parser.convert(
                "  \n **  \t l ", Tessellation.factory("Sokoban")
            )
            assert success
            assert parser._resulting_solving_mode == 'forward'
            assert parser._resulting_moves == [AtomicMove(Direction.LEFT)]

        def it_accepts_blank_input_as_empty_forward_snapshot(self, parser):
            success = parser.convert(
                "  \n   \t  ", Tessellation.factory("Sokoban")
            )
            assert success
            assert parser._resulting_solving_mode == 'forward'
            assert parser._resulting_moves == []

        def it_fails_on_non_snapshot_characters(self, parser):
            success = parser.convert("ZOMG! ", Tessellation.factory("Sokoban"))
            assert not success
            assert parser._first_encountered_error == SnapshotConversionError.NON_SNAPSHOT_CHARACTERS_FOUND

        def it_sets_mode_to_reverse_if_jumps_are_found(self, parser):
            success = parser.convert("[lurd] ", Tessellation.factory("Sokoban"))
            assert success
            for atomic_move in parser._resulting_moves:
                assert atomic_move.is_jump

        def it_ignores_empty_jump_and_pusher_selection_sequences(self, parser):
            success = parser.convert("[]lurd", Tessellation.factory("Sokoban"))
            assert success
            assert len(parser._resulting_moves) == 4

        def it_detects_reverse_snapshot_while_ignoring_empty_jumps(
            self, parser
        ):
            success = parser.convert("[]lurd", Tessellation.factory("Sokoban"))
            assert success
            assert parser._resulting_solving_mode == 'reverse'

        def it_fails_on_rle_errors(self, parser):
            success = parser.convert("((4l)", Tessellation.factory("Sokoban"))
            assert not success
            assert parser._first_encountered_error == SnapshotConversionError.RLE_DECODING_ERROR

        def it_fails_on_non_matched_sequence_separators(self, parser):
            success = parser.convert("[lurd", Tessellation.factory("Sokoban"))
            assert not success
            assert parser._first_encountered_error == SnapshotConversionError.TOKENIZATION_ERROR

        def it_fails_on_moves_illegal_in_context_of_requested_tessellation(
            self, parser
        ):
            success = parser.convert("Nlurd", Tessellation.factory("Sokoban"))
            assert not success
            assert parser._first_encountered_error == SnapshotConversionError.NON_VARIANT_CHARACTERS_FOUND

        def it_correctly_detects_jumps(self, parser):
            success = parser.convert("[lurd] ", Tessellation.factory("Sokoban"))
            assert success
            for atomic_move in parser._resulting_moves:
                assert atomic_move.is_jump

        def it_correctly_detects_pusher_selections(self, parser):
            success = parser.convert("{lurd} ", Tessellation.factory("Sokoban"))
            assert success
            for atomic_move in parser._resulting_moves:
                assert atomic_move.is_pusher_selection

    class Describe_convert_token:

        def it_fails_on_moves_illegal_in_context_of_requested_tessellation(
            self, parser
        ):
            parser._convert_token("Nlurd", Tessellation.factory("Sokoban"))
            assert parser._first_encountered_error == SnapshotConversionError.NON_VARIANT_CHARACTERS_FOUND

        def it_fails_on_jumps_that_contain_pushes(self, parser):
            parser._resulting_moves = []
            parser._convert_token(
                "lurD", Tessellation.factory("Sokoban"), is_jump=True
            )
            assert parser._first_encountered_error == SnapshotConversionError.JUMP_CONTAINS_PUSHES

        def it_fails_on_pusher_selections_that_contain_pushes(self, parser):
            parser._resulting_moves = []
            parser._convert_token(
                "lurD", Tessellation.factory("Sokoban"), is_pusher_change=True
            )
            assert parser._first_encountered_error == SnapshotConversionError.PUSHER_CHANGE_CONTAINS_PUSHES

        def it_appends_converted_moves_to_parser_resulting_moves(self, parser):
            parser._resulting_moves = []
            parser._convert_token("lurD", Tessellation.factory("Sokoban"))
            assert (
                parser._resulting_moves == [
                    AtomicMove(Direction.LEFT), AtomicMove(Direction.UP),
                    AtomicMove(Direction.RIGHT), AtomicMove(
                        Direction.DOWN, box_moved=True
                    )
                ]
            )
