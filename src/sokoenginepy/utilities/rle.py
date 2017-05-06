import re
from enum import Enum
from itertools import groupby

from pyparsing import CharsNotIn, ParseBaseException, ZeroOrMore, nestedExpr

from .text_utils import ending_digits


class RleCharacters(str, Enum):
    """Separators used in RLE encoded board and snapshot texts."""
    GROUP_LEFT_DELIM = '('
    GROUP_RIGHT_DELIM = ')'
    RLE_ROW_SEPARATOR = '|'


_RE_RLE_REPLACER = re.compile(r"(\d+)(\D)")
_RE_RLE_SPLITTER = re.compile(
    '|'.join(map(re.escape, [RleCharacters.RLE_ROW_SEPARATOR, '\n']))
)


class Rle:
    @classmethod
    def encode(cls, line):
        if len(line) == 0:
            return line

        encoded = [(len(list(g)), k) for k, g in groupby(line)]
        return "".join(
            "".join((
                str(c) if c > 1 else "",
                v,
            )) for c, v in encoded
        )

    @classmethod
    def decode_rle_token(cls, rle_token):
        """
        Decodes rle encoded strings without grouping support. ie.
        decode('3a4b') == "aaabbb"
        decode('3(a2b)4b') == "abbabbabbbbbb"
        decode('3a4b44') == "aaabbb44"
        """
        return _RE_RLE_REPLACER.sub(
            lambda m: m.group(2) * int(m.group(1)), rle_token
        )

    rle_token = CharsNotIn(
        RleCharacters.GROUP_LEFT_DELIM + RleCharacters.GROUP_RIGHT_DELIM
    )
    grouped_rle = nestedExpr(
        RleCharacters.GROUP_LEFT_DELIM, RleCharacters.GROUP_RIGHT_DELIM
    )
    token_or_group = rle_token | grouped_rle
    grammar = ZeroOrMore(token_or_group)

    @classmethod
    def tokenize_grouped_rle(cls, line):
        retv = []
        try:
            retv = cls.grammar.leaveWhitespace().parseString(line).asList()
        except ParseBaseException:
            retv = []
        return retv

    @classmethod
    def proces_group_tokens(cls, tokens):
        retv = ""
        ending_digits_num = 1
        for token in tokens:
            if isinstance(token, list):
                retv += ending_digits_num * cls.decode_rle_token(
                    cls.proces_group_tokens(token)
                )
                ending_digits_num = 1
            else:
                token_contents, ending_digits_str = ending_digits(token)
                retv += cls.decode_rle_token(token_contents)
                ending_digits_num = (
                    int(ending_digits_str) if ending_digits_str else 1
                )
        return retv

    @classmethod
    def decode(cls, line):
        return cls.proces_group_tokens(cls.tokenize_grouped_rle(line))


def rle_encode(line):
    return Rle.encode(line)


def rle_decode(line):
    return _RE_RLE_SPLITTER.sub('\n', Rle.decode(line))
