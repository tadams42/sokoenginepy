from __future__ import annotations

from itertools import groupby
from typing import Final, Optional, Set

import lark


class Rle:
    """
    Rle encoding and decoding.
    """

    #: Counted group delimiter. ie. "ab3(cd)e4f" will be decoded as "abcdcdcdefff".
    GROUP_START: Final[str] = "("

    #: Counted group delimiter. ie. "ab3(cd)e4f" will be decoded as "abcdcdcdefff".
    GROUP_END: Final[str] = ")"

    #: Line separator in encoded strings
    EOL: Final[str] = "|"

    DELIMITERS: Final[Set[str]] = {GROUP_START, GROUP_END, EOL}

    @classmethod
    def encode(cls, line: str) -> str:
        """
        RLE encodes string.

        - "aaabbbb"                       -> "3a4b"
        - "aabbbbccddeeeeffddeeeeff"      -> "2a4b2c2d4e2f2d4e2f"
        - "aabbbbccddee\neeffddeeeeff"    -> "2a4b2c2d2e|2e2f2d4e2f"
        - "aabbbbccddee     eeffddeeeeff" -> "2a4b2c2d2e5 2e2f2d4e2f"
        """
        if not line:
            return line
        encoded = [(len(list(g)), k) for k, g in groupby(line.replace("\n", cls.EOL))]
        return "".join("".join((str(c) if c > 1 else "", v)) for c, v in encoded)

    @classmethod
    def decode(cls, data: Optional[str]) -> str:
        """
        Decodes RLE encoded string.

        Supports RLE groups, ie strings like:

        - "3(a2b)4b"               -> "abbabbabbbbbb"

        Returns a list of RLE decoded lines:

        - "2a4b2c2d2e|2e2f2d4e2f"  -> "aabbbbccddee\neeffddeeeeff"
        """
        if not data:
            return ""

        try:
            parsed = LarkTreeTransformer().transform(cls.PARSER.parse(data))

        except lark.exceptions.VisitError as e:
            # raise ValueError(str(e))
            raise e.orig_exc from e

        except lark.exceptions.UnexpectedInput as e:
            raise ValueError("Unexpected input in Rle string! " + str(e)) from e

        # Rle should only modify it's own tokens, leaving the rest of input as is. This
        # means all following examples must work like this:
        #
        #     Rle.decode("\n\n\n") -> "\n\n\n"
        #     Rle.decode("\n|\n")  -> "\n\n\n"
        #     Rle.decode("|||")    -> "\n\n\n"
        #
        # To effectively normalize new lines in final output, we must do following:
        return "".join(parsed)

    GRAMMAR = f"""
        data: expr+
        expr: atoms | term | group
        term: count (ATOM | group)
        group: _GB expr+ _GE
        atoms: ATOM+
        count: DIGITS

        ATOM: /([^0-9\\{GROUP_START}\\{GROUP_END}])|([ \\n\\r\\t\\{EOL}])/
        _GB: "{GROUP_START}"
        _GE: "{GROUP_END}"
        DIGITS: /[0-9]+/
    """

    PARSER = lark.Lark(GRAMMAR, parser="lalr", start="data")


class LarkTreeTransformer(lark.Transformer):
    def data(self, lines):
        return list(lines)

    def expr(self, args):
        return "".join(args)

    def term(self, args):
        return args[0] * args[1]

    def group(self, args):
        return "".join(args)

    def atoms(self, args):
        return "".join(args).replace(Rle.EOL, "\n")

    def count(self, args):
        return int(args[0])
