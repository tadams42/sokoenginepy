import itertools
import re
from functools import reduce
from typing import Iterable, List, Optional, Union

_RE_ONLY_DIGITS_AND_SPACES = re.compile(r"^([0-9\s])*$")


def is_blank(data: Optional[Union[str, List[str]]]) -> bool:
    """True if ``line`` is empty or it contains only spaces."""

    _check = lambda l: l is None or l.strip() == ""

    if not data:
        return True

    if isinstance(data, str):
        return _check(data)

    return all(_check(_) for _ in data)


def contains_only_digits_and_spaces(line: Optional[str]) -> bool:
    return reduce(
        lambda x, y: x and y,
        [
            True if _RE_ONLY_DIGITS_AND_SPACES.match(l) else False
            for l in line.splitlines()
        ],
        True,
    )


def in_batches(iterable, of_size=1):
    """
    Generator that yields generator slices of iterable.

    Since it is elegant and working flawlessly, it is shameles C/P from
    https://stackoverflow.com/questions/8991506/iterate-an-iterator-by-chunks-of-n-in-python/8998040#8998040

    Warning:
        Each returned batch should be completely consumed before next batch
        is yielded. See example below to better understand what that means.

    Example::

        g = (o for o in range(10))
        for batch in in_batches(g, of_size=3):
            print(list(batch))
        # [0, 1, 2]
        # [3, 4, 5]
        # [6, 7, 8]
        # [9]

        # And don't consume whole batch before yielding another one...
        g = list(range(10))
        for batch in in_batches(g, of_size=3):
            print( [next(batch), next(batch)] )
        # [0, 1]
        # [2, 3]
        # [4, 5]
        # [6, 7]
        # [8, 9]
    """
    it = iter(iterable)
    while True:
        chunk_it = itertools.islice(it, of_size)
        try:
            first_el = next(chunk_it)
        except StopIteration:
            return
        yield itertools.chain((first_el,), chunk_it)
