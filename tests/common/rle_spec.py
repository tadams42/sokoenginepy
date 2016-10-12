from sokoenginepy.common import rle_decode, rle_encode
from sokoenginepy.common.rle import Rle


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
