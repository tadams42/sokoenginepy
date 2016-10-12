from ..common import Variant
from .factories import tessellation_factory


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
        self._variant_instance = Variant.factory(variant)
        self._tessellation_instance = tessellation_factory(variant)

    @property
    def variant(self):
        return self._variant_instance

    @property
    def tessellation(self):
        return self._tessellation_instance
