import os
from inspect import getsourcefile


RESOURCES_ROOT = os.path.abspath(
    os.path.join(getsourcefile(lambda: 0), "..", "..", "res")
)


def first_index_of(lst, predicate):
    return next((index for index, elem in enumerate(lst) if predicate(elem)), None)


def last_index_of(lst, predicate):
    candidate_index = first_index_of(reversed(lst), predicate)
    if candidate_index is not None:
        return len(lst) - candidate_index - 1
    return None
