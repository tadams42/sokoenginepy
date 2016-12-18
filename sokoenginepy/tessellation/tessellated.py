from .. import game
from .tessellation import Tessellation


class Tessellated:
    """
    Mixin that marks class depending on :class:`.Tessellation` specifics.
    This means that class will have to be initialized with :class:`.Variant`
    and it will use one of :class:`.Tessellation` subclass instances.
    """

    def __init__(self, variant):
        """
        variant - either case insensitive  string naming tessellation
        (ie. "hexoban") or one of :class:`.Variant` members
        """
        self._variant_instance = game.Variant.instance_from(variant)
        self._tessellation_instance = Tessellation.instance_for(variant)

    @property
    def variant(self):
        return self._variant_instance

    @property
    def tessellation(self):
        return self._tessellation_instance
