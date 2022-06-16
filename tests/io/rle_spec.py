import pytest
from sokoenginepy.io import Rle


class DescribeRle:
    def it_rle_encodes_string(self):
        assert Rle.encode("aaaabbbbccdeee") == "4a4b2cd3e"
        assert Rle.encode("aaaabbbbccdeeefghij") == "4a4b2cd3efghij"
        assert Rle.encode("aaaabbbbccdeeef") == "4a4b2cd3ef"
        assert Rle.encode("aaaabbfbbccdeee") == "4a2bf2b2cd3e"
        assert Rle.encode("aaaabbfghijbbccdeee") == "4a2bfghij2b2cd3e"
        assert Rle.encode(" aaaaaaaaaa   ") == " 10a3 "
        assert Rle.encode("   ") == "3 "

    def it_rle_line_must_have_at_least_one_non_digit(self):
        with pytest.raises(ValueError):
            assert Rle.encode("1234567890") == "1234567890"

    def it_decodes_rle_string(self):
        assert Rle.decode("4a4b2cd3e") == "aaaabbbbccdeee"
        assert Rle.decode("4a4b2cd3efghij") == "aaaabbbbccdeeefghij"
        assert Rle.decode("4a4b2cd3ef") == "aaaabbbbccdeeef"
        assert Rle.decode("4a2bf2b2cd3e") == "aaaabbfbbccdeee"
        assert Rle.decode("4a2bfghij2b2cd3e") == "aaaabbfghijbbccdeee"
        assert Rle.decode(" 10a3 ") == " aaaaaaaaaa   "
        assert Rle.decode("ccc") == "ccc"
        assert Rle.decode("3a4b") == "aaabbbb"

        assert Rle.decode("3(a2b)4b") == "abbabbabbbbbb"
        assert Rle.decode("aa2(bb)cc2(dd2(ee)ff)") == "aabbbbccddeeeeffddeeeeff"
        assert Rle.decode("2a4b2c2d2e|2e2f2d4e2f") == "aabbbbccddee\neeffddeeeeff"
        assert Rle.decode("2a4b2c2d2e5 2e2f2d4e2f") == "aabbbbccddee     eeffddeeeeff"

    def it_decodes_grouped_rle_string(self):
        assert (
            Rle.decode("2abc3def3(adfdf)2abc3def")
            == "aabcdddefadfdfadfdfadfdfaabcdddef"
        )
        assert (
            Rle.decode("2abc3def3(2a3bc)2abc3def")
            == "aabcdddefaabbbcaabbbcaabbbcaabcdddef"
        )
        assert (
            Rle.decode("2abc3def2(fdsfs2(dfgh)gtr)2abc3def")
            == "aabcdddeffdsfsdfghdfghgtrfdsfsdfghdfghgtraabcdddef"
        )
        assert (
            Rle.decode("2abc3def2(2a2bc2(2a3b)2d)2abc3def")
            == "aabcdddefaabbcaabbbaabbbddaabbcaabbbaabbbddaabcdddef"
        )

        assert Rle.decode("2(abcd)efgh") == "abcdabcdefgh"
        assert Rle.decode("2(3abcd)efgh") == "aaabcdaaabcdefgh"
        assert Rle.decode("2(abcd)3efgh") == "abcdabcdeeefgh"
        assert Rle.decode("(abcd)3efgh") == "abcdeeefgh"
        assert Rle.decode("(ab3cd)efgh") == "abcccdefgh"
        assert Rle.decode("(ab2(3c)d)efgh") == "abccccccdefgh"
        assert Rle.decode("efgh(ab3cd)") == "efghabcccd"

    def it_doesnt_modify_original_newlines_in_any_way(self):
        assert Rle.decode("\n\n\n") == "\n\n\n"
        assert Rle.decode("\n|\n") == "\n\n\n"
        assert Rle.decode("|||") == "\n\n\n"
