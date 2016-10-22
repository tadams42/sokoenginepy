from datetime import datetime
from inspect import getsourcefile
from os.path import abspath

import pytz
from unipath import Path

RESOURCES_ROOT = Path(abspath(getsourcefile(lambda: 0))
                     ).ancestor(1).ancestor(1).child('res')


def utcnow():
    return pytz.utc.localize(datetime.utcnow())


def first_index_of(lst, predicate):
    return next((index for index, elem in enumerate(lst)
                 if predicate(elem)), None)


def last_index_of(lst, predicate):
    candidate_index = first_index_of(reversed(lst), predicate)
    if candidate_index is not None:
        return len(lst) - candidate_index - 1
    return None
