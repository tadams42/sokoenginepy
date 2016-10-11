# Helper utilities for string manipulation and Sokoban data parsing. Mostly
# related to SOK file format, but probably useful for parsing any Sokoban file
# format.

import re
from functools import reduce

_re_only_digits_and_spaces = re.compile(r"^([0-9\s])*$")
_re_ending_digits = re.compile(r"(\d+)$")
_re_contains_any_digit = re.compile(r"([0-9])+")


def is_blank(line):
    return line is None or line.strip() == ""


def contains_only_digits_and_spaces(line):
    return reduce(
        lambda x, y: x and y, [
            True if _re_only_digits_and_spaces.match(l) else False
            for l in line.splitlines()
        ], True
    )


def normalize_width(string_list, fill_chr=' '):
    """Normalizes length of strings in ``string_list``.

    All strings are modified to be as long as the longest one in list. Missing
    characters in string are appended using ``fill_chr``.
    """
    width = calculate_width(string_list)
    return [l + (fill_chr * (width - len(l))) for l in string_list]


def calculate_width(string_list):
    width = 0
    for line in string_list:
        if len(line) > width:
            width = len(line)
    return width


def ending_digits(line):
    retv = _re_ending_digits.findall(line)
    if retv:
        return _re_ending_digits.sub("", line), retv[-1]
    return line, None


def drop_blank(string_list):
    return [l for l in string_list if len(l.strip()) > 0]


def drop_empty(string_list):
    return [l for l in string_list if len(l) > 0]
