import pytz
from datetime import datetime
from unipath import Path
from inspect import getsourcefile
from os.path import abspath


RESOURCES_ROOT = (
    Path(abspath(getsourcefile(lambda: 0))).ancestor(1).ancestor(1).child('res')
)


class PrettyPrintable(object):
    """
    Convenience class.
    Default implementation for __str__ that gives uniform representation.
    """

    def _representation_attributes(self):
        return self.__dict__

    def __str__(self):
        return "<{0} ({1}) {2}>".format(
            type(self).__name__,
            hex(id(self)),
            ", ".join(
                "{0}: {1}".format(k, v)
                for k, v in self._representation_attributes().items()
            )
        )


class EqualityComparable(object):
    """
    Provides default __eq__ implementation that compares objects by subset of
    their attributes.
    """

    def _equality_attributes(self):
        return self.__dict__

    def __eq__(self, other):
        return (
            self._equality_attributes() == other._equality_attributes()
        )


def utcnow():
    return pytz.utc.localize(datetime.utcnow())


def first_index_of(lst, predicate):
    return next(
        (
            index for index, elem in enumerate(lst)
            if predicate(elem)
        ), None
    )

def last_index_of(lst, predicate):
    candidate_index = first_index_of(reversed(lst), predicate)
    if candidate_index is not None:
        return len(lst) - candidate_index - 1
    return None
