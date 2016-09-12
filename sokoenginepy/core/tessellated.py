from .tessellation import Tessellation
from .variant import Variant


class Tessellated:
    """
    Mixin that marks class depending on Tessellation specifics. This means that
    class will have to be initialized with Variant and it will use one of
    Tessellation subclass instances.
    """

    def __init__(self, variant):
        """
        variant - either case insensitive  string naming tessellation
        (ie. "hexoban") or one of Variant members
        """
        assert variant in Variant
        self._variant = variant
        self._tessellation_instance = Tessellation.factory(variant)

    @property
    def variant(self):
        return self._variant

    @property
    def tessellation(self):
        return self._tessellation_instance
