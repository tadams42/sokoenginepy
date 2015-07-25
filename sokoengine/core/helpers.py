
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
            ", ".join([
                "{0}: {1}".format(k, v)
                for k, v in self._representation_attributes().items()
            ])
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
