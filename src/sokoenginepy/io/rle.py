from __future__ import annotations

from itertools import groupby
from typing import Final, Optional, Set

import lark


class Rle:
    """
    Rle encoding and decoding.
    """

    GROUP_START: Final[str] = "("
    GROUP_END: Final[str] = ")"
    EOL: Final[str] = "|"

    @classmethod
    def encode(cls, line: str) -> str:
        """RLE encodes string, ie "aaabbbb" becomes "3a4b"."""
        if not line:
            return line

        digits = {str(_) for _ in range(10)}
        if all(_ in digits for _ in line):
            raise ValueError("Cant encode fully numeric strings!")

        encoded = [(len(list(g)), k) for k, g in groupby(line.replace("\n", cls.EOL))]
        return "".join("".join((str(c) if c > 1 else "", v)) for c, v in encoded)

    @classmethod
    def decode(cls, data: Optional[str]) -> str:
        """
        Decodes RLE encoded string.

        Supports RLE groups, ie strings like "3(a2b)4b"
        """
        if not data:
            return ""

        try:
            parsed = LarkTreeTransformer().transform(cls._PARSER.parse(data))

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

    _GRAMMAR = f"""
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

    _PARSER = lark.Lark(_GRAMMAR, parser="lalr", start="data")


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
