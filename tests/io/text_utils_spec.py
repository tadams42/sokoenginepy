import pytest
from hamcrest import assert_that, equal_to

from sokoengine import BoardConversionError

from sokoengine.io.text_utils import is_board_string, is_snapshot_string,\
    is_pusher, is_box, is_goal, is_empty_floor, BoardEncodingCharacters,\
    is_wall, parse_board_string, rle_encode, rle_decode, Rle


class Describe_is_board_string(object):
    input = "0123456789\n\t bB$*p_pmM@+#_-|"

    def test_it_recognizes_board_string(self):
        assert_that(is_board_string(self.input), equal_to(True))

    def test_it_recognizes_illegal_characters(self):
        assert_that(is_board_string(self.input + "z"), equal_to(False))

    def test_it_doesnt_recognize_numeric_string(self):
        assert_that(is_board_string("42"), equal_to(False))

    def test_it_doesnt_recognize_blank_string(self):
        assert_that(is_board_string(""), equal_to(False))
        assert_that(is_board_string("    "), equal_to(False))
        assert_that(is_board_string("   \r\n "), equal_to(False))


class Describe_is_snapshot_string(object):
    input = "0123456789\n\t lurdLURDnwseNWSE"

    def test_it_recognizes_snapshot_string(self):
        assert_that(is_snapshot_string(self.input), equal_to(True))

    def test_it_recognizes_illegal_characters(self):
        assert_that(is_board_string(self.input + "z"), equal_to(False))

    def test_it_doesnt_recognize_numeric_string(self):
        assert_that(is_board_string("42"), equal_to(False))

    def test_it_doesnt_recognize_blank_string(self):
        assert_that(is_board_string(""), equal_to(False))
        assert_that(is_board_string("    "), equal_to(False))
        assert_that(is_board_string("   \r\n "), equal_to(False))


class Describe_is_pusher(object):
    def test_it_correctly_categorizes(self):
        assert_that(is_pusher(BoardEncodingCharacters.PUSHER), equal_to(True))
        assert_that(is_pusher(BoardEncodingCharacters.ALT_PUSHER1), equal_to(True))
        assert_that(is_pusher(BoardEncodingCharacters.ALT_PUSHER2), equal_to(True))
        assert_that(is_pusher(BoardEncodingCharacters.PUSHER_ON_GOAL), equal_to(True))
        assert_that(is_pusher(BoardEncodingCharacters.ALT_PUSHER_ON_GOAL1), equal_to(True))
        assert_that(is_pusher(BoardEncodingCharacters.ALT_PUSHER_ON_GOAL2), equal_to(True))


class Describe_is_box(object):
    def test_it_correctly_categorizes(self):
        assert_that(is_box(BoardEncodingCharacters.BOX), equal_to(True))
        assert_that(is_box(BoardEncodingCharacters.ALT_BOX1), equal_to(True))
        assert_that(is_box(BoardEncodingCharacters.BOX_ON_GOAL), equal_to(True))
        assert_that(is_box(BoardEncodingCharacters.ALT_BOX_ON_GOAL1), equal_to(True))


class Describe_is_goal(object):
    def test_it_correctly_categorizes(self):
        assert_that(is_goal(BoardEncodingCharacters.GOAL), equal_to(True))
        assert_that(is_goal(BoardEncodingCharacters.ALT_GOAL1), equal_to(True))
        assert_that(is_goal(BoardEncodingCharacters.PUSHER_ON_GOAL), equal_to(True))
        assert_that(is_goal(BoardEncodingCharacters.ALT_PUSHER_ON_GOAL1), equal_to(True))
        assert_that(is_goal(BoardEncodingCharacters.ALT_PUSHER_ON_GOAL2), equal_to(True))
        assert_that(is_goal(BoardEncodingCharacters.BOX_ON_GOAL), equal_to(True))
        assert_that(is_goal(BoardEncodingCharacters.ALT_BOX_ON_GOAL1), equal_to(True))


class Describe_is_empty_floor(object):
    def test_it_correctly_categorizes(self):
        assert_that(is_empty_floor(BoardEncodingCharacters.FLOOR), equal_to(True))
        assert_that(is_empty_floor(BoardEncodingCharacters.VISIBLE_FLOOR), equal_to(True))
        assert_that(is_empty_floor(BoardEncodingCharacters.ALT_VISIBLE_FLOOR1), equal_to(True))


class Describe_is_wall(object):
    def test_it_correctly_categorizes(self):
        assert_that(is_wall(BoardEncodingCharacters.WALL), equal_to(True))


class Describe_parse_board_string(object):
    def test_it_parses_regular_board(self):
        src = " ##########\n    \n" +\
              " ## @ *   #\n" +\
              "##  $ ####\n" +\
              "# $.+ #\n" +\
              "#######\n"
        parsed = parse_board_string(src)
        assert_that(len(parsed), equal_to(6))
        assert_that(len(parsed[0]), equal_to(11))

    def test_it_parses_RLE_board(self):
        src = " ##########   |" +\
              " ## @ *   #|" +\
              "##  $ ####|" +\
              "# $.+ #|||" +\
              "#######   |"
        parsed = parse_board_string(src)
        assert_that(len(parsed), equal_to(5))
        assert_that(len(parsed[0]), equal_to(14))

    def test_it_raises_on_illegal_characters(self):
        src = " ##########\n\n" +\
              " ##       #\n" +\
              "##   z####\n" +\
              "#   a #\n" +\
              "#######\n"
        with pytest.raises(BoardConversionError):
            parse_board_string(src)

    def test_it_discards_empty_but_not_blank_lines(self):
        src = " ##########\n    \n\n" +\
              " ## @ *   #\n\n" +\
              "##  $ ####\n\n" +\
              "# $.+ #\n\n" +\
              "#######\n\n"
        parsed = parse_board_string(src)
        assert_that(len(parsed), equal_to(6))
        assert_that(len(parsed[0]), equal_to(11))

    def test_id_discards_blank_boards(self):
        src = "              "
        parsed = parse_board_string(src)
        assert_that(parsed, equal_to([]))


class DescribeRle(object):

    class Describe_decode_rle_token(object):

        def test_it_decodes_rle_token(self):
            assert_that(
                Rle.decode_rle_token("4a4b2cd3e"),
                equal_to("aaaabbbbccdeee")
            )
            assert_that(
                Rle.decode_rle_token("4a4b2cd3efghij"),
                equal_to("aaaabbbbccdeeefghij")
            )
            assert_that(
                Rle.decode_rle_token("4a4b2cd3ef"),
                equal_to("aaaabbbbccdeeef")
            )
            assert_that(
                Rle.decode_rle_token("4a2bf2b2cd3e"),
                equal_to("aaaabbfbbccdeee")
            )
            assert_that(
                Rle.decode_rle_token("4a2bfghij2b2cd3e"),
                equal_to("aaaabbfghijbbccdeee")
            )
            assert_that(
                Rle.decode_rle_token(" 10a3 "),
                equal_to(" aaaaaaaaaa   ")
            )
            assert_that(
                Rle.decode_rle_token("ccc"),
                equal_to("ccc")
            )

        def test_it_preserves_ending_digits(self):
            assert_that(
                Rle.decode_rle_token("3a4b44"),
                equal_to("aaabbbb44")
            )


class Describe_rle_encode(object):
    def test_it_rle_encodes_string(self):
        assert_that(
            rle_encode("aaaabbbbccdeee"), equal_to("4a4b2cd3e")
        )
        assert_that(
            rle_encode("aaaabbbbccdeeefghij"), equal_to("4a4b2cd3efghij")
        )
        assert_that(
            rle_encode("aaaabbbbccdeeef"), equal_to("4a4b2cd3ef")
        )
        assert_that(
            rle_encode("aaaabbfbbccdeee"), equal_to("4a2bf2b2cd3e")
        )
        assert_that(
            rle_encode("aaaabbfghijbbccdeee"), equal_to("4a2bfghij2b2cd3e")
        )
        assert_that(
            rle_encode(" aaaaaaaaaa   "), equal_to(" 10a3 ")
        )
        assert_that(
            rle_encode("   "), equal_to("3 ")
        )
        assert_that(
            rle_encode("1234567890"), equal_to("1234567890")
        )


class Describe_rle_decode(object):
    def test_it_decodes_rle_string(self):
        assert_that(
            rle_decode("4a4b2cd3e"), equal_to("aaaabbbbccdeee")
        )
        assert_that(
            rle_decode("4a4b2cd3efghij"), equal_to("aaaabbbbccdeeefghij")
        )
        assert_that(
            rle_decode("4a4b2cd3ef"), equal_to("aaaabbbbccdeeef")
        )
        assert_that(
            rle_decode("4a2bf2b2cd3e"), equal_to("aaaabbfbbccdeee")
        )
        assert_that(
            rle_decode("4a2bfghij2b2cd3e"), equal_to("aaaabbfghijbbccdeee")
        )
        assert_that(
            rle_decode(" 10a3 "), equal_to(" aaaaaaaaaa   ")
        )
        assert_that(
            rle_decode("ccc"), equal_to("ccc")
        )

    def test_it_decodes_grouped_rle_string(self):
        assert_that(
            rle_decode("2abc3def3(adfdf)2abc3def"),
            equal_to("aabcdddefadfdfadfdfadfdfaabcdddef")
        )
        assert_that(
            rle_decode("2abc3def3(2a3bc)2abc3def"),
            equal_to("aabcdddefaabbbcaabbbcaabbbcaabcdddef")
        )
        assert_that(
            rle_decode("2abc3def2(fdsfs2(dfgh)gtr)2abc3def"),
            equal_to("aabcdddeffdsfsdfghdfghgtrfdsfsdfghdfghgtraabcdddef")
        )
        assert_that(
            rle_decode("2abc3def2(2a2bc2(2a3b)2d)2abc3def"),
            equal_to("aabcdddefaabbcaabbbaabbbddaabbcaabbbaabbbddaabcdddef")
        )
        assert_that(
            rle_decode("2(abcd)efgh"),
            equal_to("abcdabcdefgh")
        )
        assert_that(
            rle_decode("2(3abcd)efgh"),
            equal_to("aaabcdaaabcdefgh")
        )
        assert_that(
            rle_decode("2(abcd)3efgh"),
            equal_to("abcdabcdeeefgh")
        )
        assert_that(
            rle_decode("(abcd)3efgh"),
            equal_to("abcdeeefgh")
        )
        assert_that(
            rle_decode("(ab3cd)efgh"),
            equal_to("abcccdefgh")
        )
        assert_that(
            rle_decode("(ab2(3c)d)efgh"),
            equal_to("abccccccdefgh")
        )
        assert_that(
            rle_decode("efgh(ab3cd)"),
            equal_to("efghabcccd")
        )