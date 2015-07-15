
class PrettyPrintable(object):

    def __representation_attributes__(self):
        return self.__dict__

    def __str__(self):
        return "<{0} ({1}) {2}>".format(
            type(self).__name__,
            hex(id(self)),
            ", ".join([
                "{0}: {1}".format(k, v)
                for k, v in self.__representation_attributes__().items()
            ])
        )


class EqualityComparable(object):
    def __equality_attributes__(self):
        return self.__dict__

    def __eq__(self, other):
        return (
            self.__equality_attributes__() == other.__equality_attributes__()
        )
